"""Job D — Sunday 18:00 LA review ping, gated by a Notion checkbox."""
from __future__ import annotations

import notion_lib as n

WEEK_DAYS = 7
MAX_LISTED = 8  # cap on lines shown per section, to keep the push short


def _toggle_on(settings_db: str) -> bool:
    """True if any Automations Settings row has Weekly Review Ping checked."""
    return any(n.read_checkbox(row, "Weekly Review Ping")
               for row in n.query_database(settings_db))


def _task_lines(pages: list[dict]) -> list[str]:
    """Up to MAX_LISTED task lines with their due date."""
    return [f"  - {n.read_title(p)} ({n.read_due_day(p)})" for p in pages[:MAX_LISTED]]


def _deadline_lines(pages: list[dict]) -> list[str]:
    """Up to MAX_LISTED internship lines with their application deadline."""
    return [f"  - {n.read_title(p, 'Company')} ({n.read_due_day(p, 'Application Deadline')})"
            for p in pages[:MAX_LISTED]]


def main() -> None:
    """If the review toggle is on, push this week's tasks and internship deadlines."""
    settings_db = n.env("NOTION_SETTINGS_DB")
    tasks_db = n.env("NOTION_TASKS_DB")
    intern_db = n.env("NOTION_INTERNSHIPS_DB")

    if not _toggle_on(settings_db):
        print("Weekly Review Ping is OFF — exiting silently.")
        return

    today = n.today_la()
    week_end = today + n.timedelta(days=WEEK_DAYS)

    open_tasks = n.query_database(tasks_db, {"and": [
        n.date_between("Due Date", today.isoformat(), week_end.isoformat()),
        n.status_is_not_done(),
    ]}, sorts=[{"property": "Due Date", "direction": "ascending"}])

    deadlines = n.query_database(
        intern_db,
        n.date_between("Application Deadline", today.isoformat(), week_end.isoformat()),
        sorts=[{"property": "Application Deadline", "direction": "ascending"}],
    )

    lines = [f"Week of {today.isoformat()}", "",
             f"Tasks due this week: {len(open_tasks)}"]
    lines += _task_lines(open_tasks)
    lines += ["", f"Internship deadlines: {len(deadlines)}"]
    lines += _deadline_lines(deadlines)

    body = "\n".join(lines)
    n.ntfy_push(body, title="Weekly review", tags="rotating_light")
    print(body)


if __name__ == "__main__":
    main()
