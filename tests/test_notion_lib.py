import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import notion_lib as n


def test_optional_unset_returns_default(monkeypatch):
    monkeypatch.delenv("SOME_VAR", raising=False)
    assert n.env("SOME_VAR", required=False, default="fallback") == "fallback"


def test_optional_empty_string_returns_default(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "")
    assert n.env("SOME_VAR", required=False, default="fallback") == "fallback"


def test_optional_set_returns_value(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "actual")
    assert n.env("SOME_VAR", required=False, default="fallback") == "actual"


def test_required_unset_raises(monkeypatch):
    monkeypatch.delenv("SOME_VAR", raising=False)
    with pytest.raises(SystemExit):
        n.env("SOME_VAR", required=True)


def test_required_empty_string_raises(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "")
    with pytest.raises(SystemExit):
        n.env("SOME_VAR", required=True)


def test_required_set_returns_value(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "actual")
    assert n.env("SOME_VAR", required=True) == "actual"


def _page(title: str = "", due: str | None = None) -> dict:
    props: dict = {"Name": {"title": [{"plain_text": title}] if title else []}}
    if due is not None:
        props["Due Date"] = {"date": {"start": due}}
    return {"properties": props}


def test_read_title_or_returns_fallback_when_blank():
    assert n.read_title_or(_page()) == "(untitled)"
    assert n.read_title_or(_page(), fallback="none") == "none"


def test_read_title_or_returns_title_when_set():
    assert n.read_title_or(_page("Write report")) == "Write report"


def test_read_due_day_truncates_to_date():
    assert n.read_due_day(_page(due="2026-08-06T09:00:00-07:00")) == "2026-08-06"


def test_read_due_day_empty_when_unset():
    assert n.read_due_day(_page()) == ""


def test_status_is_not_done_filters_on_done_status():
    assert n.status_is_not_done() == {
        "property": "Status",
        "status": {"does_not_equal": "Done"},
    }


def test_date_on_or_before_filter_shape():
    assert n.date_on_or_before("Due Date", "2026-08-06") == {
        "property": "Due Date",
        "date": {"on_or_before": "2026-08-06"},
    }
