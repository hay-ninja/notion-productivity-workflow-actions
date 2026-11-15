"""Habit and workload insights computed from the task history.

Every function returns aggregate counts only (no titles), plus a plain-English
`headline` so the page leads with the takeaway, and a `ready` flag so charts say
"collecting data" instead of reading patterns into a handful of tasks.
"""
from __future__ import annotations

from datetime import date, timedelta
from statistics import median

from notion_lib import DONE_STATUS

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
STALE_DAYS = 7
PACE_WINDOW = 28          # days of completions used for "your usual pace"
RHYTHM_WEEKS = 12
HEATMAP_WEEKS = 20
BACKLOG_DAYS = 56
MIN_TIMING = 8            # finished tasks with a due date before timing is shown
MIN_RHYTHM = 10           # completions before the weekday rhythm is shown
MIN_PUSH_DAYS = 14        # days of tracking before push-back rates mean anything
MIN_TYPE_N = 3            # per-Type rows with fewer tasks are flagged "few tasks"

TIMING_BUCKETS = [
    ("1 wk+ early", lambda d: d <= -7),
    ("3–6d early", lambda d: -6 <= d <= -3),
    ("1–2d early", lambda d: -2 <= d <= -1),
    ("Due day", lambda d: d == 0),
    ("1–2d late", lambda d: 1 <= d <= 2),
    ("3d+ late", lambda d: d >= 3),
]
LEAD_BUCKETS = [
    ("Same day", lambda d: d <= 0),
    ("1–2 days", lambda d: 1 <= d <= 2),
    ("3–6 days", lambda d: 3 <= d <= 6),
    ("1 week+", lambda d: d >= 7),
]


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _types(rec: dict) -> list[str]:
    return rec.get("types") or ["untyped"]


def _bucketize(values: list[int], buckets) -> list[dict]:
    return [{"label": lbl, "count": sum(1 for v in values if test(v))} for lbl, test in buckets]


def _days_phrase(n: float) -> str:
    n = round(n)
    if n == 0:
        return "on the due date"
    unit = "day" if abs(n) == 1 else "days"
    return f"{abs(n)} {unit} {'early' if n < 0 else 'late'}"


def _cap(s: str) -> str:
    """Capitalise the first letter only (Type names are often lowercase)."""
    return s[:1].upper() + s[1:]


def _pct(part: int, whole: int) -> int:
    return round(100 * part / whole) if whole else 0


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def load_next_7(open_recs: list[dict], done_recs: list[dict], today: date) -> dict:
    """Open tasks due each of the next 7 days vs your usual daily finish rate."""
    window_start = today - timedelta(days=PACE_WINDOW)
    recent = [r for r in done_recs if window_start <= _d(r["done_on"]) < today]
    pace = round(len(recent) / PACE_WINDOW, 2)
    days = []
    for i in range(7):
        d = today + timedelta(days=i)
        due = [r for r in open_recs if r.get("due") == d.isoformat()]
        by_type: dict[str, int] = {}
        for r in due:
            for t in _types(r):
                by_type[t] = by_type.get(t, 0) + 1
        days.append({"date": d.isoformat(), "label": "Today" if i == 0 else WEEKDAYS[d.weekday()],
                     "count": len(due), "by_type": by_type})
    overdue = sum(1 for r in open_recs if r.get("due") and _d(r["due"]) < today)
    peak = max(days, key=lambda x: x["count"])
    if peak["count"] == 0:
        headline = "Nothing due in the next 7 days."
    elif pace and peak["count"] > max(2 * pace, pace + 2):
        when = "today" if peak["label"] == "Today" else peak["label"]
        headline = (f"{when} is heavy: {peak['count']} due vs. your usual "
                    f"{pace:.1f}/day. Start some of it earlier.")
    else:
        total = sum(x["count"] for x in days)
        headline = f"{total} due this coming week, no single day over your usual pace."
    return {"days": days, "pace": pace, "overdue": overdue, "headline": headline}


def backlog(history: dict, recs: list[dict], done_recs: list[dict], today: date) -> dict:
    """Open-task count over time, plus tasks added vs finished per week."""
    start = today - timedelta(days=BACKLOG_DAYS - 1)
    daily = [{"date": d, "open": v["open"]} for d, v in sorted(history.get("daily", {}).items())
             if _d(d) >= start]
    weeks = []
    this_monday = _week_start(today)
    for i in range(7, -1, -1):
        ws = this_monday - timedelta(days=7 * i)
        we = ws + timedelta(days=6)
        added = sum(1 for r in recs if r.get("created") and ws <= _d(r["created"]) <= we)
        done = sum(1 for r in done_recs if ws <= _d(r["done_on"]) <= we)
        weeks.append({"week": ws.isoformat(), "added": added, "done": done})
    last4 = weeks[-5:-1]  # four full weeks before this one
    added4, done4 = sum(w["added"] for w in last4), sum(w["done"] for w in last4)
    net = added4 - done4
    if added4 == 0 and done4 == 0:
        headline = "No tasks added or finished in the last four weeks."
    elif net > 0:
        headline = (f"Backlog grew by {net} over the last 4 weeks: {added4} added, "
                    f"{done4} finished.")
    elif net < 0:
        headline = (f"Backlog shrank by {-net} over the last 4 weeks: {done4} finished, "
                    f"{added4} added.")
    else:
        headline = f"Holding steady: {added4} added and {done4} finished in 4 weeks."
    return {"daily": daily, "weeks": weeks, "headline": headline}


def stale(open_recs: list[dict], today: date) -> dict:
    """Open tasks whose status and due date haven't changed in STALE_DAYS+ days."""
    cutoff = today - timedelta(days=STALE_DAYS)
    st = [r for r in open_recs if r.get("last_change") and _d(r["last_change"]) <= cutoff]
    by_type: dict[str, int] = {}
    for r in st:
        for t in _types(r):
            by_type[t] = by_type.get(t, 0) + 1
    by_type = dict(sorted(by_type.items(), key=lambda kv: -kv[1]))
    if not st:
        headline = "Nothing's gone stale. Every open task moved in the last week."
    else:
        top = next(iter(by_type))
        headline = (f"{len(st)} of {len(open_recs)} open tasks haven't moved in a week+, "
                    f"mostly {top}.")
    return {"count": len(st), "open": len(open_recs), "by_type": by_type, "headline": headline}


def finish_timing(done_recs: list[dict]) -> dict:
    """How many days before/after the due date tasks get finished."""
    rows = [r for r in done_recs if r.get("due")]
    offsets = [(_d(r["done_on"]) - _d(r["due"])).days for r in rows]
    by_type: dict[str, list[int]] = {}
    for r, off in zip(rows, offsets):
        for t in _types(r):
            by_type.setdefault(t, []).append(off)
    types = sorted(
        ({"type": t, "median": median(v), "n": len(v), "few": len(v) < MIN_TYPE_N}
         for t, v in by_type.items()),
        key=lambda x: x["median"])
    ready = len(offsets) >= MIN_TIMING
    if not ready:
        headline = f"Collecting data: {len(offsets)} of {MIN_TIMING} finished tasks so far."
    else:
        overall = median(offsets)
        solid = [t for t in types if not t["few"]]
        headline = f"You usually finish {_days_phrase(overall)}."
        if len(solid) >= 2 and solid[-1]["median"] - solid[0]["median"] >= 2:
            headline += (f" {_cap(solid[0]['type'])}: {_days_phrase(solid[0]['median'])}; "
                         f"{solid[-1]['type']}: {_days_phrase(solid[-1]['median'])}.")
    return {"buckets": _bucketize(offsets, TIMING_BUCKETS), "by_type": types, "n": len(offsets),
            "estimated": sum(1 for r in rows if r.get("done_est")), "ready": ready,
            "headline": headline}


def rhythm(recs: list[dict], done_recs: list[dict], today: date) -> dict:
    """Tasks due vs. tasks finished on each weekday over the last RHYTHM_WEEKS weeks."""
    start = today - timedelta(weeks=RHYTHM_WEEKS)
    due = [0] * 7
    done = [0] * 7
    for r in recs:
        if r.get("due") and start <= _d(r["due"]) < today:
            due[_d(r["due"]).weekday()] += 1
    recent_done = [r for r in done_recs if start <= _d(r["done_on"]) < today]
    for r in recent_done:
        done[_d(r["done_on"]).weekday()] += 1
    n = len(recent_done)
    ready = n >= MIN_RHYTHM
    if not ready:
        headline = f"Collecting data: {n} of {MIN_RHYTHM} completions so far."
    else:
        top = max(range(7), key=lambda i: done[i])
        low = min(range(7), key=lambda i: done[i])
        headline = (f"{WEEKDAYS[top]} is your strongest day ({_pct(done[top], n)}% of "
                    f"finishes); {WEEKDAYS[low]} is the quietest.")
        wknd = done[5] + done[6]
        if _pct(wknd, n) >= 40:
            headline += f" Weekends carry {_pct(wknd, n)}% of your work."
    return {"days": [{"label": WEEKDAYS[i], "due": due[i], "done": done[i]} for i in range(7)],
            "n": n, "estimated": sum(1 for r in recent_done if r.get("done_est")),
            "ready": ready, "headline": headline}


def pushes(recs: list[dict], days_tracked: int) -> dict:
    """How often each Type gets its due date moved later (counted since tracking began)."""
    by_type: dict[str, dict] = {}
    for r in recs:
        if not r.get("first_due"):
            continue
        for t in _types(r):
            b = by_type.setdefault(t, {"type": t, "tasks": 0, "pushed": 0, "pushes": 0})
            b["tasks"] += 1
            b["pushed"] += 1 if r.get("pushes", 0) > 0 else 0
            b["pushes"] += r.get("pushes", 0)
    rows = []
    for b in by_type.values():
        b["rate"] = _pct(b["pushed"], b["tasks"])
        b["few"] = b["tasks"] < MIN_TYPE_N
        rows.append(b)
    rows.sort(key=lambda b: (-b["rate"], -b["tasks"]))
    ready = days_tracked >= MIN_PUSH_DAYS
    total_pushes = sum(r.get("pushes", 0) for r in recs)
    if not ready:
        headline = (f"Collecting data: day {days_tracked} of {MIN_PUSH_DAYS}. "
                    f"{total_pushes} push-backs spotted so far.")
    elif total_pushes == 0:
        headline = "No due dates pushed back since tracking started."
    else:
        solid = [b for b in rows if not b["few"]] or rows
        headline = (f"{_cap(solid[0]['type'])} gets pushed back most: {solid[0]['rate']}% of "
                    f"those tasks moved at least once.")
    return {"by_type": rows, "total": total_pushes, "ready": ready, "headline": headline}


def planning(recs: list[dict]) -> dict:
    """Days between adding a task to Notion and its due date."""
    rows = [r for r in recs if r.get("due") and r.get("created")]
    leads = [(_d(r["due"]) - _d(r["created"])).days for r in rows]
    buckets = _bucketize(leads, LEAD_BUCKETS)
    n = len(leads)
    if n < MIN_TIMING:
        headline = f"Collecting data: {n} tasks with due dates so far."
    else:
        last_minute = buckets[0]["count"] + buckets[1]["count"]
        headline = (f"{_pct(last_minute, n)}% of tasks get added 2 days or less before "
                    f"they're due. Median lead time: {round(median(leads))} days.")
    return {"buckets": buckets, "n": n, "ready": n >= MIN_TIMING, "headline": headline}


def heatmap(done_recs: list[dict], today: date) -> dict:
    """Completions per day for the last HEATMAP_WEEKS weeks, Monday-aligned."""
    start = _week_start(today) - timedelta(weeks=HEATMAP_WEEKS - 1)
    if done_recs:  # don't pad the grid with weeks before any recorded completion
        first = min(_d(r["done_on"]) for r in done_recs)
        start = max(start, _week_start(first))
    else:
        start = _week_start(today)
    counts: dict[str, int] = {}
    for r in done_recs:
        if start <= _d(r["done_on"]) <= today:
            counts[r["done_on"]] = counts.get(r["done_on"], 0) + 1
    days = []
    d = start
    while d <= today:
        days.append({"date": d.isoformat(), "count": counts.get(d.isoformat(), 0)})
        d += timedelta(days=1)
    active = sum(1 for x in days if x["count"])
    total = sum(x["count"] for x in days)
    # longest run of consecutive days with at least one finish
    best = run = 0
    for x in days:
        run = run + 1 if x["count"] else 0
        best = max(best, run)
    headline = (f"{total} tasks finished on {active} of the last {len(days)} days. "
                f"Longest streak: {best} {'day' if best == 1 else 'days'}.")
    return {"start": start.isoformat(), "days": days, "max": max([x["count"] for x in days] or [0]),
            "headline": headline}


def build_insights(history: dict, today: date) -> dict:
    """Every insight block the page renders, from the (already updated) history."""
    all_recs = list(history.get("tasks", {}).values())
    live = [r for r in all_recs if not r.get("gone")]
    open_recs = [r for r in live if r.get("status") != DONE_STATUS]
    done_recs = [r for r in all_recs if r.get("done_on")]
    since = history.get("since") or today.isoformat()
    days_tracked = (today - _d(since)).days + 1
    return {
        "tracking_since": since,
        "days_tracked": days_tracked,
        "estimated_completions": sum(1 for r in done_recs if r.get("done_est")),
        "load": load_next_7(open_recs, done_recs, today),
        "backlog": backlog(history, all_recs, done_recs, today),
        "stale": stale(open_recs, today),
        "timing": finish_timing(done_recs),
        "rhythm": rhythm(all_recs, done_recs, today),
        "pushes": pushes(all_recs, days_tracked),
        "planning": planning(all_recs),
        "heatmap": heatmap(done_recs, today),
    }
