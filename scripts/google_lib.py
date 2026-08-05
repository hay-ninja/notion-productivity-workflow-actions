"""Build Google API credentials from a stored refresh token (headless / Actions)."""
from __future__ import annotations

import notion_lib as n
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
]


def _credentials() -> Credentials:
    """Build OAuth credentials from the stored refresh token (no interactive login)."""
    return Credentials(
        token=None,
        refresh_token=n.env("GOOGLE_REFRESH_TOKEN"),
        client_id=n.env("GOOGLE_CLIENT_ID"),
        client_secret=n.env("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )


def calendar_service():
    """Authenticated Google Calendar API client."""
    return build("calendar", "v3", credentials=_credentials(), cache_discovery=False)
