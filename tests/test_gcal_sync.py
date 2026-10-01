"""Offline tests for the gcal_sync upsert logic — no network."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
pytest.importorskip("googleapiclient")
import gcal_sync as g
from googleapiclient.errors import HttpError


class _Resp(dict):
    def __init__(self, status):
        super().__init__()
        self.status = status
        self.reason = "x"


def _err(code):
    return HttpError(_Resp(code), b"{}")


class FakeCal:
    """Minimal stand-in for cal.events() that tracks events by ID."""

    def __init__(self, existing=(), deleted=(), fail_update=None):
        self.events_by_id = {i: {} for i in existing}
        self.deleted = set(deleted)
        self.fail_update = fail_update
        self.inserts = 0

    def events(self):
        return self

    def update(self, calendarId, eventId, body):
        def run():
            if self.fail_update:
                raise _err(self.fail_update)
            if eventId not in self.events_by_id and eventId not in self.deleted:
                raise _err(404)
            self.deleted.discard(eventId)
            self.events_by_id[eventId] = body
        return type("R", (), {"execute": staticmethod(run)})

    def insert(self, calendarId, body):
        def run():
            if body["id"] in self.events_by_id or body["id"] in self.deleted:
                raise _err(409)
            self.inserts += 1
            self.events_by_id[body["id"]] = body
        return type("R", (), {"execute": staticmethod(run)})


def test_event_id_is_dashless_page_id():
    assert g.event_id_for({"id": "3ee5c1d1-502c-80ff-a636-f7a2b5dfec45"}) == \
        "3ee5c1d1502c80ffa636f7a2b5dfec45"


def test_creates_when_missing():
    cal = FakeCal()
    assert g.upsert(cal, "c", "abc12", {}) == "created"
    assert cal.inserts == 1


def test_running_twice_never_duplicates():
    cal = FakeCal()
    g.upsert(cal, "c", "abc12", {})
    g.upsert(cal, "c", "abc12", {})
    assert cal.inserts == 1 and len(cal.events_by_id) == 1


def test_revives_hand_deleted_event_instead_of_new_one():
    cal = FakeCal(deleted={"abc12"})
    assert g.upsert(cal, "c", "abc12", {}) == "updated"
    assert cal.inserts == 0


def test_transient_error_is_raised_not_duplicated():
    cal = FakeCal(existing={"abc12"}, fail_update=503)
    with pytest.raises(HttpError):
        g.upsert(cal, "c", "abc12", {})
    assert cal.inserts == 0
