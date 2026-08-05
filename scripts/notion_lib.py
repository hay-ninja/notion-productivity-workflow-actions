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


def env(name: str, required: bool = True, default: str | None = None) -> str | None:
    # GitHub Actions injects "" for a secret that isn't set, so an empty value
    # must fall back to default rather than being treated as present.
    val = os.environ.get(name) or default
    if required and not val:
        raise SystemExit(f"Missing required environment variable: {name}")
    return val


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {env('NOTION_TOKEN')}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def now_la() -> datetime:
    return datetime.now(LA)


def today_la() -> date:
    return now_la().date()


def iso_week(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y:04d}-{w:02d}"


def query_database(database_id: str, filter_: dict | None = None,
                   sorts: list | None = None) -> list[dict]:
    results: list[dict] = []
    payload: dict = {}
    if filter_:
        payload["filter"] = filter_
    if sorts:
        payload["sorts"] = sorts
    url = f"{API}/databases/{database_id}/query"
    while True:
        r = requests.post(url, headers=_headers(), json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


def update_page(page_id: str, properties: dict) -> dict:
    r = requests.patch(f"{API}/pages/{page_id}", headers=_headers(),
                       json={"properties": properties}, timeout=30)
    r.raise_for_status()
    return r.json()


def prop(page: dict, name: str) -> dict:
    return page.get("properties", {}).get(name, {}) or {}


def read_title(page: dict, name: str = "Name") -> str:
    return "".join(p.get("plain_text", "") for p in prop(page, name).get("title", [])).strip()


def read_text(page: dict, name: str) -> str:
    return "".join(p.get("plain_text", "") for p in prop(page, name).get("rich_text", [])).strip()


def read_date(page: dict, name: str) -> str | None:
    d = prop(page, name).get("date")
    return d.get("start") if d else None


def read_status(page: dict, name: str = "Status") -> str | None:
    s = prop(page, name).get("status")
    return s.get("name") if s else None


def read_select(page: dict, name: str) -> str | None:
    s = prop(page, name).get("select")
    return s.get("name") if s else None


def read_multi(page: dict, name: str) -> list[str]:
    return [o.get("name", "") for o in prop(page, name).get("multi_select", [])]


def read_checkbox(page: dict, name: str) -> bool:
    return bool(prop(page, name).get("checkbox"))


def status_is(name: str, value: str) -> dict:
    return {"property": name, "status": {"equals": value}}


def status_is_not(name: str, value: str) -> dict:
    return {"property": name, "status": {"does_not_equal": value}}


def date_on_or_before(name: str, iso_day: str) -> dict:
    return {"property": name, "date": {"on_or_before": iso_day}}


def date_between(name: str, start: str, end: str) -> dict:
    return {"and": [
        {"property": name, "date": {"on_or_after": start}},
        {"property": name, "date": {"on_or_before": end}},
    ]}


def ntfy_push(message: str, title: str | None = None, tags: str | None = None) -> None:
    server = env("NTFY_SERVER", required=False, default="https://ntfy.sh")
    topic = env("NTFY_TOPIC")
    headers = {}
    if title:
        headers["Title"] = title
    if tags:
        headers["Tags"] = tags
    r = requests.post(f"{server}/{topic}", data=message.encode("utf-8"),
                      headers=headers, timeout=30)
    r.raise_for_status()
