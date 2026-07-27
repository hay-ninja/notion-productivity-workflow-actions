import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import notion_lib as n


def test_iso_week_basic():
    assert n.iso_week(date(2024, 1, 1)) == "2024-01"


def test_iso_week_year_boundary():
    assert n.iso_week(date(2025, 12, 29)) == "2026-01"


def test_status_is():
    assert n.status_is("Status", "Done") == {"property": "Status", "status": {"equals": "Done"}}


def test_status_is_not():
    assert n.status_is_not("Status", "Done") == {
        "property": "Status",
        "status": {"does_not_equal": "Done"},
    }


def test_date_on_or_before():
    assert n.date_on_or_before("Due", "2024-01-01") == {
        "property": "Due",
        "date": {"on_or_before": "2024-01-01"},
    }


def test_date_between():
    assert n.date_between("Due", "2024-01-01", "2024-01-31") == {
        "and": [
            {"property": "Due", "date": {"on_or_after": "2024-01-01"}},
            {"property": "Due", "date": {"on_or_before": "2024-01-31"}},
        ]
    }


def _page(properties):
    return {"properties": properties}


def test_read_title():
    page = _page({"Name": {"title": [{"plain_text": "Hello "}, {"plain_text": "World"}]}})
    assert n.read_title(page) == "Hello World"


def test_read_title_missing_property():
    assert n.read_title(_page({})) == ""


def test_read_text():
    page = _page({"Notes": {"rich_text": [{"plain_text": "abc"}]}})
    assert n.read_text(page, "Notes") == "abc"


def test_read_date_present():
    page = _page({"Due": {"date": {"start": "2024-01-01"}}})
    assert n.read_date(page, "Due") == "2024-01-01"


def test_read_date_missing():
    assert n.read_date(_page({}), "Due") is None


def test_read_status():
    page = _page({"Status": {"status": {"name": "In Progress"}}})
    assert n.read_status(page) == "In Progress"


def test_read_status_missing():
    assert n.read_status(_page({})) is None


def test_read_select():
    page = _page({"Priority": {"select": {"name": "High"}}})
    assert n.read_select(page, "Priority") == "High"


def test_read_multi():
    page = _page({"Tags": {"multi_select": [{"name": "a"}, {"name": "b"}]}})
    assert n.read_multi(page, "Tags") == ["a", "b"]


def test_read_multi_empty():
    assert n.read_multi(_page({}), "Tags") == []


def test_read_checkbox():
    page = _page({"Done": {"checkbox": True}})
    assert n.read_checkbox(page, "Done") is True


def test_read_checkbox_missing():
    assert n.read_checkbox(_page({}), "Done") is False
