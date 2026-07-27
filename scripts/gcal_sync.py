"""Job C — one-way Notion -> Google Calendar sync. Cron every 15 min.

Every task with a due date becomes one event on a single dedicated calendar:
  * due date with no time  -> an all-day event on that date
  * due date with a time   -> a timed event of DEFAULT_MINUTES starting then

The created event's ID is written back to the task's `GCal Event ID` so later
runs update the same event instead of creating duplicates. Sync is one-way and
never deletes events.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta

import notion_lib as n
from google_lib import calendar_service

EVENT_ID_PROP = "GCal Event ID"
DEFAULT_MINUTES = 30  # length of a timed task event
TZ = "America/Los_Angeles"


def _event_body(task: dict) -> dict:
    due = n.read_date(task, "Due Date")
    body: dict = {"summary": n.read_title(task) or "(untitled task)",
                  "source": {"title": "Notion task", "url": task.get("url", "")}}
    if due and "T" in due:
        start = datetime.fromisoformat(due)
        end = start + timedelta(minutes=DEFAULT_MINUTES)
        body["start"] = {"dateTime": start.isoformat(), "timeZone": TZ}
        body["end"] = {"dateTime": end.isoformat(), "timeZone": TZ}
    else:
        day = (due or "")[:10]
        # Google treats all-day end as exclusive, so end is the following day.
        end_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
        body["start"] = {"date": day}
        body["end"] = {"date": end_day}
    return body


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Read normally but make no writes or notifications.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    tasks_db = n.env("NOTION_TASKS_DB")
    calendar_id = n.env("GCAL_CALENDAR_ID")

    tasks = n.query_database(tasks_db, {"and": [
        {"property": "Due Date", "date": {"is_not_empty": True}},
        n.status_is_not("Status", "Done"),
    ]})

    if args.dry_run:
        would_update = sum(1 for t in tasks if n.read_text(t, EVENT_ID_PROP))
        would_create = len(tasks) - would_update
        print(f"[dry-run] would sync {len(tasks)} task(s): "
             f"{would_create} create, {would_update} update.")
        return

    cal = calendar_service()
    created = updated = 0
    for task in tasks:
        existing = n.read_text(task, EVENT_ID_PROP)
        body = _event_body(task)
        if existing:
            try:
                cal.events().update(calendarId=calendar_id, eventId=existing,
                                    body=body).execute()
                updated += 1
                continue
            except Exception as e:
                print(f"update failed for {existing} ({e}); recreating")
        ev = cal.events().insert(calendarId=calendar_id, body=body).execute()
        n.update_page(task["id"], {EVENT_ID_PROP: {"rich_text": [{"text": {"content": ev["id"]}}]}})
        created += 1

    print(f"Sync complete: {created} created, {updated} updated, {len(tasks)} scanned.")


if __name__ == "__main__":
    main()
