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

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "data", "stats.json")
DONE = "Done"


def _due_between(start, end) -> dict:
    return n.date_between("Due Date", start.isoformat(), end.isoformat())


def main() -> None:
    tasks_db = n.env("NOTION_TASKS_DB")
    today = n.today_la()
    monday = today - n.timedelta(days=today.weekday())
    sunday = monday + n.timedelta(days=6)

    today_tasks = n.query_database(tasks_db, _due_between(today, today))
    week_tasks = n.query_database(tasks_db, _due_between(monday, sunday))

    def split(pages):
        done = sum(1 for p in pages if n.read_status(p) == DONE)
        return {"total": len(pages), "done": done}

    # Eight-week history for the bar chart.
    weeks = []
    for i in range(7, -1, -1):
        start = monday - n.timedelta(days=7 * i)
        end = start + n.timedelta(days=6)
        pages = n.query_database(tasks_db, _due_between(start, end))
        s = split(pages)
        weeks.append({"week": n.iso_week(start), **s})

    # Open work by category, for the breakdown bars.
    open_tasks = n.query_database(tasks_db, n.status_is_not("Status", DONE))
    by_type: dict[str, int] = {}
    for p in open_tasks:
        for t in n.read_multi(p, "Type") or ["untyped"]:
            by_type[t] = by_type.get(t, 0) + 1

    payload = {
        "generated_at": n.now_la().isoformat(),
        "today": split(today_tasks),
        "week": split(week_tasks),
        "open_total": len(open_tasks),
        "by_type": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
        "weeks": weeks,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
