"""Job B — push tasks due within 3 days to your phone via ntfy. Cron 07:00 LA."""
from __future__ import annotations

import notion_lib as n

HORIZON_DAYS = 3


def _line(page: dict, today_iso: str) -> str:
    """One display line for a due task, showing "today" instead of the date when due today."""
    due = n.read_due_day(page)
    when = "today" if due == today_iso else due
    return f"- {n.read_title_or(page)} ({when})"


def main() -> None:
    """Push unfinished tasks due within HORIZON_DAYS to ntfy, oldest due date first."""
    tasks_db = n.env("NOTION_TASKS_DB")
    today = n.today_la()
    horizon = today + n.timedelta(days=HORIZON_DAYS)

    pages = n.query_database(tasks_db, {"and": [
        n.date_between("Due Date", today.isoformat(), horizon.isoformat()),
        n.status_is_not_done(),
    ]}, sorts=[{"property": "Due Date", "direction": "ascending"}])

    if not pages:
        print(f"Nothing due in the next {HORIZON_DAYS} days.")
        return

    body = "\n".join(_line(p, today.isoformat()) for p in pages)
    n.ntfy_push(body, title=f"{len(pages)} task(s) due soon", tags="calendar")
    print(body)


if __name__ == "__main__":
    main()
