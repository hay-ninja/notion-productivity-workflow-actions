"""Job D — Sunday 18:00 LA review ping, gated by a Notion checkbox."""
from __future__ import annotations

import notion_lib as n

WEEK_DAYS = 7
MAX_LISTED = 8  # cap on lines shown per section, to keep the push short
PRIORITY = 3


def _toggle_on(settings_db: str) -> bool:
    """True if any Automations Settings row has Weekly Review Ping checked."""
    return any(n.read_checkbox(row, "Weekly Review Ping")
               for row in n.query_database(settings_db))


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

    lines = [f"Tasks due this week: {len(open_tasks)}"]
    lines += [n.format_task_line(p, today) for p in open_tasks[:MAX_LISTED]]
    lines += ["", f"Internship deadlines: {len(deadlines)}"]
    lines += [n.format_task_line(p, today, title_prop="Company", due_prop="Application Deadline")
              for p in deadlines[:MAX_LISTED]]

    body = "\n".join(lines)
    title = f"Week of {today:%b} {today.day}"
    n.ntfy_push(body, title=title, tags="rotating_light", priority=PRIORITY,
                click=n.NOTION_HOME_URL, actions=n.OPEN_TASKS_ACTION)
    print(body)


if __name__ == "__main__":
    main()
