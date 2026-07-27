import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def _boom(*a, **kw):
    raise AssertionError("write helper was called during --dry-run")


def _page(status="Not Started"):
    return {"id": "p1", "properties": {"Status": {"status": {"name": status}}}}


def test_deadline_reminders_dry_run_no_writes(monkeypatch):
    import deadline_reminders as dr

    monkeypatch.setattr(sys, "argv", ["deadline_reminders.py", "--dry-run"])
    monkeypatch.setattr(dr.n, "env", lambda name, **kw: "fake-db")
    monkeypatch.setattr(dr.n, "query_database", lambda *a, **kw: [_page()])
    monkeypatch.setattr(dr.n, "ntfy_push", _boom)

    dr.main()


def test_weekly_review_dry_run_no_writes(monkeypatch):
    import weekly_review as wr

    monkeypatch.setattr(sys, "argv", ["weekly_review.py", "--dry-run"])
    monkeypatch.setattr(wr.n, "env", lambda name, **kw: "fake-db")

    def fake_query_database(database_id, filter_=None, sorts=None):
        if filter_ is None:
            return [{"properties": {"Weekly Review Ping": {"checkbox": True}}}]
        return []

    monkeypatch.setattr(wr.n, "query_database", fake_query_database)
    monkeypatch.setattr(wr.n, "ntfy_push", _boom)

    wr.main()


def test_email_digest_dry_run_no_writes(monkeypatch):
    import email_digest as ed

    monkeypatch.setattr(sys, "argv", ["email_digest.py", "--dry-run"])
    monkeypatch.setattr(ed.n, "env", lambda name, **kw: "fake-db")
    monkeypatch.setattr(ed, "_fetch_recent", lambda: [])
    monkeypatch.setattr(ed, "_summarize", lambda items: "digest body")
    monkeypatch.setattr(ed.n, "query_database", lambda *a, **kw: [])
    monkeypatch.setattr(ed.n, "create_page", _boom)

    ed.main()


def test_gcal_sync_dry_run_no_writes(monkeypatch):
    import gcal_sync as gs

    monkeypatch.setattr(sys, "argv", ["gcal_sync.py", "--dry-run"])
    monkeypatch.setattr(gs.n, "env", lambda name, **kw: "fake-db")
    monkeypatch.setattr(gs.n, "query_database", lambda *a, **kw: [_page()])
    monkeypatch.setattr(gs.n, "update_page", _boom)
    monkeypatch.setattr(gs, "calendar_service", _boom)

    gs.main()
