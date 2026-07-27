"""Job B — push tasks due within 3 days to your phone via ntfy. Cron 07:00 LA."""
from __future__ import annotations

import argparse

import notion_lib as n


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Read normally but make no writes or notifications.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    tasks_db = n.env("NOTION_TASKS_DB")
    today = n.today_la()
    horizon = today + n.timedelta(days=3)

    pages = n.query_database(tasks_db, {"and": [
        n.date_between("Due Date", today.isoformat(), horizon.isoformat()),
        n.status_is_not("Status", "Done"),
    ]}, sorts=[{"property": "Due Date", "direction": "ascending"}])

    if not pages:
        print("Nothing due in the next 3 days.")
        return

    lines = []
    for p in pages:
        due = (n.read_date(p, "Due Date") or "")[:10]
        when = "today" if due == today.isoformat() else due
        lines.append(f"- {n.read_title(p) or '(untitled)'} ({when})")

    body = "\n".join(lines)
    if args.dry_run:
        print(f"[dry-run] would push notification {len(pages)} task(s) due soon:\n{body}")
        return
    n.ntfy_push(body, title=f"{len(pages)} task(s) due soon", tags="calendar")
    print(body)


if __name__ == "__main__":
    main()
