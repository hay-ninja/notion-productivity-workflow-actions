"""Job D — Sunday 18:00 LA review ping, gated by a Notion checkbox."""
from __future__ import annotations

import argparse
import logging

import notion_lib as n

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _toggle_on(settings_db: str) -> bool:
    return any(n.read_checkbox(row, "Weekly Review Ping")
               for row in n.query_database(settings_db))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Read normally but make no writes or notifications.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    settings_db = n.env("NOTION_SETTINGS_DB")
    tasks_db = n.env("NOTION_TASKS_DB")
    intern_db = n.env("NOTION_INTERNSHIPS_DB")

    if not _toggle_on(settings_db):
        logger.info("Weekly Review Ping is OFF — exiting silently.")
        return

    today = n.today_la()
    week_end = today + n.timedelta(days=7)

    open_tasks = n.query_database(tasks_db, {"and": [
        n.date_between("Due Date", today.isoformat(), week_end.isoformat()),
        n.status_is_not("Status", "Done"),
    ]}, sorts=[{"property": "Due Date", "direction": "ascending"}])

    deadlines = n.query_database(intern_db, {"and": [
        {"property": "Application Deadline", "date": {"on_or_after": today.isoformat()}},
        {"property": "Application Deadline", "date": {"on_or_before": week_end.isoformat()}},
    ]}, sorts=[{"property": "Application Deadline", "direction": "ascending"}])

    lines = [f"Week of {today.isoformat()}", "",
             f"Tasks due this week: {len(open_tasks)}"]
    lines += [f"  - {n.read_title(p)} ({(n.read_date(p, 'Due Date') or '')[:10]})"
              for p in open_tasks[:8]]
    lines += ["", f"Internship deadlines: {len(deadlines)}"]
    lines += [f"  - {n.read_title(p, 'Company')} ({(n.read_date(p, 'Application Deadline') or '')[:10]})"
              for p in deadlines[:8]]

    body = "\n".join(lines)
    if args.dry_run:
        logger.info("[dry-run] would push weekly review notification:\n%s", body)
        return
    n.ntfy_push(body, title="Weekly review", tags="rotating_light")
    logger.info(body)


if __name__ == "__main__":
    main()
