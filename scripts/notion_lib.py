"""Shared helpers: Notion REST client, timezone utilities, ntfy push."""
from __future__ import annotations

import os
from datetime import (  # noqa: F401 -- re-exported for callers (n.timedelta)
    date,
    datetime,
    timedelta,
)
from zoneinfo import ZoneInfo

import requests

LA = ZoneInfo("America/Los_Angeles")
NOTION_VERSION = "2022-06-28"
API = "https://api.notion.com/v1"
REQUEST_TIMEOUT = 30  # seconds, for every Notion/ntfy network call
DONE_STATUS = "Done"
DEFAULT_NTFY_SERVER = "https://ntfy.sh"


def env(name: str, required: bool = True, default: str | None = None) -> str | None:
    """Read an environment variable, treating an unset or empty value as absent.

    GitHub Actions injects "" for a secret that isn't configured, so a falsy
    value falls back to `default` instead of being returned as-is. Exits the
    process with an error if `required` and no value or default is available.
    """
    val = os.environ.get(name) or default
    if required and not val:
        raise SystemExit(f"Missing required environment variable: {name}")
    return val


def _headers() -> dict:
    """Auth + content headers for every Notion REST request."""
    return {
        "Authorization": f"Bearer {env('NOTION_TOKEN')}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def now_la() -> datetime:
    """Current time in America/Los_Angeles."""
    return datetime.now(LA)


def today_la() -> date:
    """Today's date in America/Los_Angeles."""
    return now_la().date()


def iso_week(d: date) -> str:
    """ISO year-week label for `d`, e.g. "2026-31"."""
    y, w, _ = d.isocalendar()
    return f"{y:04d}-{w:02d}"


def query_database(database_id: str, filter_: dict | None = None,
                   sorts: list | None = None) -> list[dict]:
    """Return every page in a Notion database matching `filter_`, following pagination."""
    results: list[dict] = []
    payload: dict = {}
    if filter_:
        payload["filter"] = filter_
    if sorts:
        payload["sorts"] = sorts
    url = f"{API}/databases/{database_id}/query"
    while True:
        r = requests.post(url, headers=_headers(), json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


def update_page(page_id: str, properties: dict) -> dict:
    """Patch a Notion page's properties."""
    r = requests.patch(f"{API}/pages/{page_id}", headers=_headers(),
                       json={"properties": properties}, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def prop(page: dict, name: str) -> dict:
    """Raw property dict for `name` on a Notion page, or {} if absent."""
    return page.get("properties", {}).get(name, {}) or {}


def read_title(page: dict, name: str = "Name") -> str:
    """Plain-text value of a title property."""
    return "".join(p.get("plain_text", "") for p in prop(page, name).get("title", [])).strip()


def read_title_or(page: dict, name: str = "Name", fallback: str = "(untitled)") -> str:
    """Title property text, or `fallback` if the title is blank."""
    return read_title(page, name) or fallback


def read_text(page: dict, name: str) -> str:
    """Plain-text value of a rich_text property."""
    return "".join(p.get("plain_text", "") for p in prop(page, name).get("rich_text", [])).strip()


def read_date(page: dict, name: str) -> str | None:
    """ISO start value of a date property, or None if unset."""
    d = prop(page, name).get("date")
    return d.get("start") if d else None


def read_due_day(page: dict, name: str = "Due Date") -> str:
    """Just the YYYY-MM-DD portion of a date property, or "" if unset."""
    return (read_date(page, name) or "")[:10]


def read_status(page: dict, name: str = "Status") -> str | None:
    """Name of a status-type property's current value, or None if unset."""
    s = prop(page, name).get("status")
    return s.get("name") if s else None


def read_multi(page: dict, name: str) -> list[str]:
    """Selected option names of a multi_select property."""
    return [o.get("name", "") for o in prop(page, name).get("multi_select", [])]


def read_checkbox(page: dict, name: str) -> bool:
    """Value of a checkbox property."""
    return bool(prop(page, name).get("checkbox"))


def status_is_not(name: str, value: str) -> dict:
    """Filter: status-type property `name` does not equal `value`."""
    return {"property": name, "status": {"does_not_equal": value}}


def status_is_not_done(name: str = "Status") -> dict:
    """Filter: status-type property `name` is not DONE_STATUS."""
    return status_is_not(name, DONE_STATUS)


def date_on_or_before(name: str, iso_day: str) -> dict:
    """Filter: date property `name` is on or before `iso_day`."""
    return {"property": name, "date": {"on_or_before": iso_day}}


def date_between(name: str, start: str, end: str) -> dict:
    """Filter: date property `name` falls within [start, end] inclusive."""
    return {"and": [
        {"property": name, "date": {"on_or_after": start}},
        {"property": name, "date": {"on_or_before": end}},
    ]}


def ntfy_push(message: str, title: str | None = None, tags: str | None = None,
             priority: int | None = None, click: str | None = None,
             actions: str | None = None) -> None:
    """Push a message to the configured ntfy topic.

    `priority` (1-5), `click` (a URL opened on tap), and `actions` (an ntfy
    Actions header value) are sent only when provided, so callers that omit
    them get the same request as before.
    """
    server = env("NTFY_SERVER", required=False, default=DEFAULT_NTFY_SERVER)
    topic = env("NTFY_TOPIC")
    headers = {}
    if title:
        headers["Title"] = title
    if tags:
        headers["Tags"] = tags
    if priority:
        headers["Priority"] = str(priority)
    if click:
        headers["Click"] = click
    if actions:
        headers["Actions"] = actions
    r = requests.post(f"{server}/{topic}", data=message.encode("utf-8"),
                      headers=headers, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
