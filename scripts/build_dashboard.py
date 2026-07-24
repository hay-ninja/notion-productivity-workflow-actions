"""Dashboard builder — Notion -> site/data/stats.json for the Pages chart.

Emits ONLY aggregate counts (no task titles), safe to publish and embed.
"""
from __future__ import annotations

import json
import os

import notion_lib as n

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "data", "stats.json")


def _count(db: str, filt: dict) -> int:
    return len(n.query_database(db, filt))


def main() -> None:
    tasks_db = n.env("NOTION_TASKS_DB")
    today = n.today_la()

    weeks = []
    for i in range(7, -1, -1):
        start = today - n.timedelta(days=today.weekday() + 7 * i)
        end = start + n.timedelta(days=6)
        rng = n.date_between("Due Date", start.isoformat(), end.isoformat())
        weeks.append({
            "week": n.iso_week(start),
            "total": _count(tasks_db, rng),
            "done": _count(tasks_db, {"and": [rng, n.status_is("Status", "Done")]}),
        })

    day = n.date_between("Due Date", today.isoformat(), today.isoformat())
    payload = {
        "generated_at": n.now_la().isoformat(),
        "today": {
            "due": _count(tasks_db, {"and": [day, n.checkbox_is("Archived", False)]}),
            "done": _count(tasks_db, {"and": [day, n.status_is("Status", "Done")]}),
        },
        "weeks": weeks,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
