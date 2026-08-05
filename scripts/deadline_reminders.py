"""Job B — push tasks due within 3 days to your phone via ntfy. Cron 07:00 LA."""
from __future__ import annotations

import notion_lib as n

HORIZON_DAYS = 3


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

    body = "\n".join(n.format_task_line(p, today) for p in pages)
    today_count = sum(1 for p in pages if n.task_urgency(n.read_due_day(p), today) == "today")
    title = f"Due soon · {today_count} today" if today_count else "Due soon"
    n.ntfy_push(body, title=title, tags="calendar")
    print(body)


if __name__ == "__main__":
    main()
