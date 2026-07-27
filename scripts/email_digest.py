"""Job A — Gmail digest into Notion, plus tomorrow's top 3 on the evening run.

Morning run: inbox digest only.
Evening run: digest + "tomorrow's top 3" so your brain pre-loads the next day
(the habit that makes the rest of the system worth having).
"""
from __future__ import annotations

import argparse

import requests

import notion_lib as n
from google_lib import gmail_service

MAX_MESSAGES = 25
EVENING_HOUR = 12  # runs at/after noon LA count as the evening digest


def _headers_of(service, msg_id: str) -> dict:
    m = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "Subject"]).execute()
    h = {x["name"]: x["value"] for x in m.get("payload", {}).get("headers", [])}
    return {"from": h.get("From", ""), "subject": h.get("Subject", "(no subject)"),
            "snippet": m.get("snippet", "")}


def _fetch_recent() -> list[dict]:
    service = gmail_service()
    resp = service.users().messages().list(
        userId="me", q="in:inbox newer_than:1d", maxResults=MAX_MESSAGES).execute()
    return [_headers_of(service, x["id"]) for x in resp.get("messages", [])]


def _summarize(items: list[dict]) -> str:
    if not items:
        return "No new mail in the lookback window."
    listing = "\n".join(
        f"- From: {it['from']}\n  Subject: {it['subject']}\n  {it['snippet']}"
        for it in items)
    prompt = (
        "You are an inbox assistant. Summarize the emails below into a concise daily "
        "digest for a busy student. Group by theme, flag anything time-sensitive or "
        "action-required with a leading '! '. Under 200 words. Plain text.\n\n"
        f"{listing}")
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": n.env("ANTHROPIC_API_KEY"),
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": n.env("ANTHROPIC_MODEL", required=False,
                             default="claude-haiku-4-5-20251001"),
              "max_tokens": 700,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=60)
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json().get("content", [])).strip()


def tomorrow_top3() -> list[str]:
    """Top 3 unfinished tasks due tomorrow or earlier, by priority then due date."""
    tasks_db = n.env("NOTION_TASKS_DB")
    tomorrow = (n.today_la() + n.timedelta(days=1)).isoformat()
    pages = n.query_database(tasks_db, {"and": [
        {"property": "Due Date", "date": {"on_or_before": tomorrow}},
        n.status_is_not("Status", "Done"),
    ]})
    pages.sort(key=lambda p: n.read_date(p, "Due Date") or "9999")
    out = []
    for p in pages[:3]:
        due = (n.read_date(p, "Due Date") or "")[:10]
        out.append(f"{n.read_title(p) or '(untitled)'} — due {due}")
    return out


def _blocks(text: str) -> list[dict]:
    blocks = []
    for para in text.split("\n"):
        blocks.append({"object": "block", "type": "paragraph",
                       "paragraph": {"rich_text": [{"type": "text",
                                                    "text": {"content": para[:1900]}}] if para else []}})
    return blocks[:90]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Read normally but make no writes or notifications.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    digests_db = n.env("NOTION_DIGESTS_DB")
    now = n.now_la()
    is_evening = now.hour >= EVENING_HOUR

    body = _summarize(_fetch_recent())

    if is_evening:
        top3 = tomorrow_top3()
        body += "\n\n— Tomorrow's top 3 —\n"
        body += "\n".join(f"{i}. {t}" for i, t in enumerate(top3, 1)) if top3 \
            else "Nothing queued for tomorrow. Pick one thing tonight."

    today = n.today_la().isoformat()
    title = f"Digest {today} {now:%H:%M}"
    if args.dry_run:
        print(f"[dry-run] would write digest {title!r} (evening={is_evening}):\n{body}")
        return
    n.create_page(digests_db,
                  properties={"Name": {"title": [{"text": {"content": title}}]},
                              "Date": {"date": {"start": today}}},
                  children=_blocks(body))
    print(f"Wrote {title!r} (evening={is_evening}).")


if __name__ == "__main__":
    main()
