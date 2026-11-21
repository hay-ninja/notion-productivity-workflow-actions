"""Generate site/data/stats.sample.json by simulating ~10 weeks of daily snapshots.

Dev-only: lets the page be previewed (and the fallback render) before any real
history exists. Run: python scripts/make_sample_stats.py
"""
from __future__ import annotations

import json
import os
import random
from datetime import date, datetime, time, timedelta

from insights import build_insights
from notion_lib import LA
from task_history import empty_history, snapshot_from_pages, update_history

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "data", "stats.sample.json")
TODAY = date(2026, 11, 25)
DAYS = 70
COLORS = {"academics": "blue", "CS": "purple", "personal": "green",
          "extracurricular": "orange", "scholarships": "pink"}
# type: (weight, finish offset range relative to due, chance of a push-back)
HABITS = {"academics": (5, (-1, 1), 0.10), "CS": (4, (-5, -1), 0.05),
          "personal": (2, (-2, 2), 0.15), "extracurricular": (2, (-3, 0), 0.10),
          "scholarships": (1, (-1, 4), 0.55)}


def ts(d: date, hour: int) -> str:
    return datetime.combine(d, time(hour), LA).isoformat()


def page(t: dict, today: date) -> dict:
    done = t["done_on"] is not None and t["done_on"] <= today - timedelta(days=0) \
        and t["done_on"] < today
    edited = t["done_on"] if done else t["edited"]
    return {
        "id": t["id"], "created_time": ts(t["created"], 12),
        "last_edited_time": ts(min(edited, today), 21),
        "properties": {
            "Status": {"status": {"name": "Done" if done else "Not started"}},
            "Due Date": {"date": {"start": t["due"].isoformat()}},
            "Type": {"multi_select": [{"name": t["type"], "color": COLORS[t["type"]]}]},
            "Course": {"multi_select": []},
        },
    }


def main() -> None:
    rng = random.Random(7)
    start = TODAY - timedelta(days=DAYS)
    tasks: list[dict] = []
    names = list(HABITS)
    weights = [HABITS[k][0] for k in names]
    hist = empty_history()
    for i in range(DAYS + 1):
        day = start + timedelta(days=i)
        for _ in range(rng.choice([0, 1, 1, 2, 2, 3])):
            typ = rng.choices(names, weights)[0]
            lead = rng.choice([0, 1, 1, 2, 3, 4, 5, 7, 10])
            due = day + timedelta(days=lead)
            lo, hi = HABITS[typ][1]
            done_on = due + timedelta(days=rng.randint(lo, hi))
            # weekend batching: nudge some finishes onto Sunday
            if rng.random() < 0.3:
                done_on += timedelta(days=(6 - done_on.weekday()) % 7)
            done_on = max(done_on, day)
            if rng.random() < 0.12:
                done_on = None  # never finished
            tasks.append({"id": f"sim-{len(tasks)}", "type": typ, "created": day, "due": due,
                          "done_on": done_on, "edited": day, "push": HABITS[typ][2]})
        for t in tasks:
            open_ = t["done_on"] is None or t["done_on"] >= day
            if open_ and t["due"] <= day + timedelta(days=1) and rng.random() < t["push"] / 5:
                shift = timedelta(days=rng.randint(1, 3))
                t["due"] += shift
                if t["done_on"]:
                    t["done_on"] += shift
                t["edited"] = day
        live = [t for t in tasks if t["created"] <= day]
        hist = update_history(hist, snapshot_from_pages([page(t, day) for t in live]), day)

    # a lopsided week ahead, so the load chart has something to flag
    for k, (typ, off) in enumerate([("academics", 1), ("academics", 1), ("CS", 1), ("academics", 1),
                                    ("personal", 1), ("CS", 3), ("academics", 5)]):
        tasks.append({"id": f"ahead-{k}", "type": typ, "created": TODAY - timedelta(days=2),
                      "due": TODAY + timedelta(days=off), "done_on": None,
                      "edited": TODAY - timedelta(days=2), "push": 0})
    hist = update_history(hist, snapshot_from_pages([page(t, TODAY) for t in tasks]), TODAY)
    ins = build_insights(hist, TODAY)
    monday = TODAY - timedelta(days=TODAY.weekday())
    def due_in(a, b, done=None):
        return [t for t in tasks if a <= t["due"] <= b
                and (done is None or ((t["done_on"] is not None and t["done_on"] < TODAY) == done))]
    today_all = due_in(TODAY, TODAY)
    week_all = due_in(monday, monday + timedelta(days=6))
    payload = {
        "sample": True,
        "generated_at": ts(TODAY, 6),
        "today": {"total": len(today_all), "done": len(due_in(TODAY, TODAY, True))},
        "week": {"total": len(week_all),
                 "done": len(due_in(monday, monday + timedelta(days=6), True))},
        "open_total": ins["stale"]["open"],
        "by_type": {},
        "weeks": [],
        "type_colors": COLORS,
        "insights": ins,
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
