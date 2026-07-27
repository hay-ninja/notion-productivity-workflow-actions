import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import notion_lib as n
import build_dashboard as bd


def _page(status, types=None):
    props = {"Status": {"status": {"name": status}}}
    if types is not None:
        props["Type"] = {"multi_select": [{"name": t} for t in types]}
    return {"properties": props}


def _run(monkeypatch, tmp_path, date_pages, open_pages):
    monkeypatch.setattr(n, "env", lambda name, **kw: "fake-db-id")

    def fake_query_database(database_id, filter_=None, sorts=None):
        if filter_ and "and" in filter_:
            return date_pages
        return open_pages

    monkeypatch.setattr(bd.n, "query_database", fake_query_database)
    monkeypatch.setattr(bd, "OUT", str(tmp_path / "stats.json"))

    bd.main()
    return json.loads((tmp_path / "stats.json").read_text())


def test_counts_with_tasks(monkeypatch, tmp_path):
    date_pages = [_page("Done"), _page("Done"), _page("In Progress")]
    open_pages = [
        _page("In Progress", ["Deep Work"]),
        _page("In Progress", ["Deep Work"]),
        _page("Not Started", ["Admin"]),
        _page("Not Started", []),
    ]
    payload = _run(monkeypatch, tmp_path, date_pages, open_pages)

    assert payload["today"] == {"total": 3, "done": 2}
    assert payload["week"] == {"total": 3, "done": 2}
    assert payload["open_total"] == 4
    assert payload["by_type"] == {"Deep Work": 2, "Admin": 1, "untyped": 1}
    assert len(payload["weeks"]) == 8


def test_zero_tasks_no_division_by_zero(monkeypatch, tmp_path):
    payload = _run(monkeypatch, tmp_path, [], [])

    assert payload["today"] == {"total": 0, "done": 0}
    assert payload["week"] == {"total": 0, "done": 0}
    assert payload["open_total"] == 0
    assert payload["by_type"] == {}
    assert all(w["total"] == 0 and w["done"] == 0 for w in payload["weeks"])
