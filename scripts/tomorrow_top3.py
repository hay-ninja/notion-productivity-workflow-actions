"""Push tomorrow's top 3 unfinished tasks via ntfy. Cron 18:00 LA.

This carries over the single most valuable habit from the old email digest:
writing down what's due soon primes the next day before you sit down to work.
"""
from __future__ import annotations

import notion_lib as n

TOP_N = 3
EMPTY_MESSAGE = "Nothing queued for tomorrow. Pick one thing tonight."


def top3_lines(pages: list[dict]) -> list[str]:
    """Format the TOP_N soonest-due pages as display lines, earliest due date first."""
    ranked = sorted(pages, key=lambda p: n.read_date(p, "Due Date") or "9999")[:TOP_N]
    return [f"{n.read_title_or(p)} — due {n.read_due_day(p)}" for p in ranked]


def body_for(lines: list[str]) -> str:
    """Build the ntfy message body from formatted lines, or a fallback for none due."""
    if not lines:
        return EMPTY_MESSAGE
    return "\n".join(f"{i}. {line}" for i, line in enumerate(lines, 1))


def main() -> None:
    """Push the top 3 unfinished tasks due tomorrow or earlier to ntfy."""
    tasks_db = n.env("NOTION_TASKS_DB")
    tomorrow = (n.today_la() + n.timedelta(days=1)).isoformat()

    pages = n.query_database(tasks_db, {"and": [
        n.date_on_or_before("Due Date", tomorrow),
        n.status_is_not_done(),
    ]})

    body = body_for(top3_lines(pages))
    n.ntfy_push(body, title="Tomorrow's top 3", tags="clipboard")
    print(body)


if __name__ == "__main__":
    main()
