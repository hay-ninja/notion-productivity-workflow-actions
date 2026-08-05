"""Build Google API credentials from a stored refresh token (headless / Actions)."""
from __future__ import annotations

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import notion_lib as n

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
]


def _credentials() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=n.env("GOOGLE_REFRESH_TOKEN"),
        client_id=n.env("GOOGLE_CLIENT_ID"),
        client_secret=n.env("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )


def gmail_service():
    return build("gmail", "v1", credentials=_credentials(), cache_discovery=False)


def calendar_service():
    return build("calendar", "v3", credentials=_credentials(), cache_discovery=False)
