"""Daily task history — turns once-a-day snapshots into a record of what changed.

Notion's free plan doesn't record *when* a task was finished or how often its due
date moved. This module diffs today's tasks against the stored history so the
dashboard can answer those questions:

- done_on      the day a task first appeared as Done
- pushes       how many times the due date moved later
- last_change  the last day its status or due date changed (for "stale" counts)

Privacy: the repo and Pages site are public, so records hold NO titles and NO raw
Notion IDs — only a short hash, dates, status and Type/Course tags.

Everything here is pure (no network) so it can be unit tested.
"""
from __future__ import annotations

import hashlib
from datetime import date, datetime

from notion_lib import DONE_STATUS, LA, read_due_day, read_multi, read_status

HISTORY_VERSION = 1


def empty_history() -> dict:
    """A brand-new history with nothing recorded yet."""
    return {"version": HISTORY_VERSION, "since": None, "last_snapshot": None,
            "tasks": {}, "daily": {}}


def task_key(page_id: str) -> str:
    """Short, non-reversible key for a Notion page ID."""
    return hashlib.sha256(page_id.replace("-", "").encode()).hexdigest()[:12]


def _la_day(iso_ts: str | None) -> str | None:
    """YYYY-MM-DD in Los Angeles time for a Notion ISO timestamp."""
    if not iso_ts:
        return None
    ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    return ts.astimezone(LA).date().isoformat()


def snapshot_from_pages(pages: list[dict]) -> list[dict]:
    """Reduce raw Notion task pages to the minimal fields history needs."""
    snap = []
    for p in pages:
        snap.append({
            "key": task_key(p["id"]),
            "created": _la_day(p.get("created_time")),
            "edited": _la_day(p.get("last_edited_time")),
            "due": read_due_day(p) or None,
            "status": read_status(p) or "Not started",
            "types": read_multi(p, "Type"),
            "courses": read_multi(p, "Course"),
        })
    return snap


def type_colors_from_pages(pages: list[dict]) -> dict[str, str]:
    """Notion's own color name for each Type option, e.g. {"CS": "purple"}."""
    colors: dict[str, str] = {}
    for p in pages:
        opts = p.get("properties", {}).get("Type", {}).get("multi_select", []) or []
        for o in opts:
            colors.setdefault(o.get("name", ""), o.get("color", "default"))
    return colors


def _clamp_day(day: str | None, lo: str | None, hi: str) -> str:
    """Clamp an ISO day into [lo, hi]; falls back to hi when unknown."""
    if not day:
        return hi
    if lo and day < lo:
        return lo
    return min(day, hi)


def update_history(history: dict, snapshot: list[dict], today: date) -> dict:
    """Fold today's snapshot into `history` (mutates and returns it).

    The job runs early in the morning, so a task finished last night first shows
    up as Done today. Its last-edited day (clamped to the window since the previous
    snapshot) is a better completion day than "today", so that's what's stored.
    """
    today_s = today.isoformat()
    tasks = history.setdefault("tasks", {})
    prev = history.get("last_snapshot")
    bootstrap = prev is None
    if bootstrap:
        history["since"] = today_s
    seen = set()

    for t in snapshot:
        k = t["key"]
        seen.add(k)
        is_done = t["status"] == DONE_STATUS
        change_day = _clamp_day(t["edited"], prev, today_s)
        rec = tasks.get(k)

        if rec is None:
            rec = {
                "created": t["created"] or today_s,
                "first_due": t["due"],
                "due": t["due"],
                "status": t["status"],
                "types": t["types"],
                "courses": t["courses"],
                "done_on": (t["edited"] or today_s) if is_done else None,
                # True when the completion day is a guess (task was already Done
                # before tracking started, so its last edit is the best we have).
                "done_est": bool(is_done and bootstrap),
                "pushes": 0,
                "last_change": t["edited"] or today_s,
                "gone": False,
            }
            tasks[k] = rec
            continue

        rec["gone"] = False
        rec["types"], rec["courses"] = t["types"], t["courses"]

        if t["due"] != rec["due"]:
            if rec["due"] and t["due"] and t["due"] > rec["due"]:
                rec["pushes"] += 1
            if rec["first_due"] is None:
                rec["first_due"] = t["due"]
            rec["due"] = t["due"]
            rec["last_change"] = change_day

        if t["status"] != rec["status"]:
            was_done = rec["status"] == DONE_STATUS
            if is_done and not was_done:
                rec["done_on"], rec["done_est"] = change_day, False
            elif was_done and not is_done:
                rec["done_on"], rec["done_est"] = None, False
            rec["status"] = t["status"]
            rec["last_change"] = change_day

    for k, rec in tasks.items():
        if k not in seen:
            rec["gone"] = True  # deleted in Notion; kept so past completions still count

    open_count = sum(1 for t in snapshot if t["status"] != DONE_STATUS)
    history.setdefault("daily", {})[today_s] = {"open": open_count}
    history["last_snapshot"] = today_s
    return history
