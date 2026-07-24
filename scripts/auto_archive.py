"""Job E — archive tasks Done for > 7 days. Cron 03:00 LA.

Free-plan default uses last_edited_time as the age proxy (Notion's Done-At stamping
automation requires a paid plan).
"""
from __future__ import annotations

import notion_lib as n

AGE_DAYS = 7


def main() -> None:
    tasks_db = n.env("NOTION_TASKS_DB")
    cutoff = (n.now_la() - n.timedelta(days=AGE_DAYS)).date().isoformat()

    pages = n.query_database(tasks_db, {"and": [
        n.status_is("Status", "Done"),
        n.checkbox_is("Archived", False),
        {"timestamp": "last_edited_time", "last_edited_time": {"on_or_before": cutoff}},
    ]})
    if not pages:
        print("Nothing to archive.")
        return
    for p in pages:
        n.update_page(p["id"], {"Archived": {"checkbox": True}})
        print(f"Archived: {n.read_title(p)!r}")
    print(f"Archived {len(pages)} task(s).")


if __name__ == "__main__":
    main()
