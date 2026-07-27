"""Job C — one-way Notion -> Google Calendar sync. Cron every 15 min.

Writes the created event's ID back to the task's `GCal Event ID` so later runs
update instead of duplicating. Deletions/archival do not remove existing events.
"""
from __future__ import annotations

import notion_lib as n
from google_lib import calendar_service

EVENT_ID_PROP = "GCal Event ID"


def _event_body(task: dict) -> dict:
    due = n.read_date(task, "Due Date")
    body: dict = {"summary": n.read_title(task) or "(untitled task)",
                  "source": {"title": "Notion task", "url": task.get("url", "")}}
    if due and "T" in due:
        body["start"] = {"dateTime": due, "timeZone": "America/Los_Angeles"}
        body["end"] = {"dateTime": due, "timeZone": "America/Los_Angeles"}
    else:
        day = (due or "")[:10]
        body["start"] = {"date": day}
        body["end"] = {"date": day}
    return body


def main() -> None:
    tasks_db = n.env("NOTION_TASKS_DB")
    calendar_id = n.env("GCAL_CALENDAR_ID")
    cal = calendar_service()

    tasks = n.query_database(tasks_db, {"and": [
        {"property": "Due Date", "date": {"is_not_empty": True}},
        n.status_is_not("Status", "Done"),
    ]})

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
