"""Dashboard builder — computes progress directly from the tasks database.

This replaces Notion's Stats database entirely. Counts are derived from the tasks
data at run time, so there is no relation to maintain and no undercounting: every
task is included whether or not it was created from a template.

Emits ONLY aggregate counts (no task titles), safe to publish and embed.
"""
from __future__ import annotations

import json
import os

import notion_lib as n
from insights import build_insights
from task_history import empty_history, snapshot_from_pages, type_colors_from_pages, update_history

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "data", "stats.json")
# Task history lives on the `dashboard-history` branch; the workflow checks it out here.
HISTORY_PATH = os.environ.get("HISTORY_PATH") or os.path.join(
    os.path.dirname(__file__), "..", "history", "history.json")
HISTORY_WEEKS = 8  # weeks of history for the bar chart, including the current week


def _due_between(start, end) -> dict:
    """Filter: Due Date falls within [start, end] inclusive."""
    return n.date_between("Due Date", start.isoformat(), end.isoformat())


def _split(pages: list[dict]) -> dict:
    """Count total vs. done pages."""
    done = sum(1 for p in pages if n.read_status(p) == n.DONE_STATUS)
    return {"total": len(pages), "done": done}


def _weekly_history(tasks_db: str, monday) -> list[dict]:
    """Total/done counts for each of the last HISTORY_WEEKS weeks, oldest first."""
    weeks = []
    for i in range(HISTORY_WEEKS - 1, -1, -1):
        start = monday - n.timedelta(days=7 * i)
        end = start + n.timedelta(days=6)
        pages = n.query_database(tasks_db, _due_between(start, end))
        weeks.append({"week": n.iso_week(start), **_split(pages)})
    return weeks


def _open_by_type(open_tasks: list[dict]) -> dict[str, int]:
    """Open task counts grouped by Type, most common first."""
    by_type: dict[str, int] = {}
    for p in open_tasks:
        for t in n.read_multi(p, "Type") or ["untyped"]:
            by_type[t] = by_type.get(t, 0) + 1
    return dict(sorted(by_type.items(), key=lambda kv: -kv[1]))


def load_history(path: str = HISTORY_PATH) -> dict:
    """Stored history, or a fresh one on the first run."""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return empty_history()


def save_history(history: dict, path: str = HISTORY_PATH) -> None:
    """Write history compactly (one file, rewritten each run)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(history, f, separators=(",", ":"), sort_keys=True)


def main() -> None:
    """Aggregate counts, update the task history, and write stats.json."""
    tasks_db = n.env("NOTION_TASKS_DB")
    today = n.today_la()
    monday = today - n.timedelta(days=today.weekday())
    sunday = monday + n.timedelta(days=6)

    today_tasks = n.query_database(tasks_db, _due_between(today, today))
    week_tasks = n.query_database(tasks_db, _due_between(monday, sunday))
    open_tasks = n.query_database(tasks_db, n.status_is_not_done())

    all_tasks = n.query_database(tasks_db)
    history = update_history(load_history(), snapshot_from_pages(all_tasks), today)
    save_history(history)

    payload = {
        "generated_at": n.now_la().isoformat(),
        "today": _split(today_tasks),
        "week": _split(week_tasks),
        "open_total": len(open_tasks),
        "by_type": _open_by_type(open_tasks),
        "weeks": _weekly_history(tasks_db, monday),
        "type_colors": type_colors_from_pages(all_tasks),
        "insights": build_insights(history, today),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
