"""Job C — one-way Notion -> Google Calendar sync. Cron hourly.

Every open task with a due date becomes exactly one event on a dedicated calendar:
  * due date with no time  -> an all-day event on that date
  * due date with a time   -> a timed event of DEFAULT_MINUTES starting then

Idempotency: an event's ID is derived from the Notion page ID (a 32-char hex string,
which is valid Google base32hex), so a task can only ever map to one event even if a
run crashes before writing back, two runs overlap, or `GCal Event ID` is blank.
Tasks synced before this change keep their stored legacy (random) event ID.

Sync is one-way and never deletes events.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import notion_lib as n
from google_lib import calendar_service
from googleapiclient.errors import HttpError

EVENT_ID_PROP = "GCal Event ID"
DEFAULT_MINUTES = 30  # length of a timed task event
TZ = "America/Los_Angeles"
GONE = {404, 410}  # event really doesn't exist -> safe to (re)create
EXISTS = 409       # ID already taken (live or previously deleted) -> update instead


def event_id_for(task: dict) -> str:
    """Deterministic Google event ID for a Notion page: its UUID without dashes."""
    return task["id"].replace("-", "").lower()


def _status_code(e: HttpError) -> int:
    return int(getattr(e, "status_code", None) or e.resp.status)


def _event_body(task: dict) -> dict:
    """Build a Calendar API event body for one task's Due Date."""
    due = n.read_date(task, "Due Date")
    url = task.get("url", "")
    body: dict = {"summary": n.read_title_or(task, fallback="(untitled task)").strip(),
                  "description": f"Notion: {url}" if url else "",
                  "source": {"title": "Notion task", "url": url},
                  "status": "confirmed"}  # revives an event that was deleted by hand
    if due and "T" in due:
        start = datetime.fromisoformat(due)
        end = start + timedelta(minutes=DEFAULT_MINUTES)
        body["start"] = {"dateTime": start.isoformat(), "timeZone": TZ}
        body["end"] = {"dateTime": end.isoformat(), "timeZone": TZ}
    else:
        day = n.read_due_day(task)
        # Google treats all-day end as exclusive, so end is the following day.
        end_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
        body["start"] = {"date": day}
        body["end"] = {"date": end_day}
    return body


def upsert(cal, calendar_id: str, event_id: str, body: dict) -> str:
    """Update `event_id`, creating it if it doesn't exist. Returns 'updated'/'created'.

    Any error other than 'not found' / 'already exists' is re-raised instead of
    falling through to a blind insert — that fallthrough is what used to duplicate.
    """
    try:
        cal.events().update(calendarId=calendar_id, eventId=event_id, body=body).execute()
        return "updated"
    except HttpError as e:
        if _status_code(e) not in GONE:
            raise
    try:
        cal.events().insert(calendarId=calendar_id, body={**body, "id": event_id}).execute()
        return "created"
    except HttpError as e:
        if _status_code(e) != EXISTS:
            raise
    cal.events().update(calendarId=calendar_id, eventId=event_id, body=body).execute()
    return "updated"


def main() -> None:
    """Sync every open, due-dated task to its own Google Calendar event."""
    tasks_db = n.env("NOTION_TASKS_DB")
    calendar_id = n.env("GCAL_CALENDAR_ID")
    cal = calendar_service()

    tasks = n.query_database(tasks_db, {"and": [
        {"property": "Due Date", "date": {"is_not_empty": True}},
        n.status_is_not_done(),
    ]})

    counts = {"created": 0, "updated": 0, "failed": 0}
    for task in tasks:
        stored = n.read_text(task, EVENT_ID_PROP)
        event_id = stored or event_id_for(task)
        try:
            counts[upsert(cal, calendar_id, event_id, _event_body(task))] += 1
        except HttpError as e:
            # One bad task shouldn't stop the rest; the next hourly run retries it.
            counts["failed"] += 1
            print(f"skip {task['id']} ({event_id}): {e}")
            continue
        if stored != event_id:
            n.update_page(task["id"], {EVENT_ID_PROP: {"rich_text": [{"text": {"content": event_id}}]}})

    print(f"Sync complete: {counts['created']} created, {counts['updated']} updated, "
          f"{counts['failed']} failed, {len(tasks)} scanned.")
    if counts["failed"]:
        raise SystemExit(1)  # surface it in the Actions UI


if __name__ == "__main__":
    main()
