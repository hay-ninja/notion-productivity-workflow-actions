import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from notion_lib import date
from tomorrow_top3 import EMPTY_MESSAGE, body_for, top3_lines

TODAY = date(2026, 8, 5)


def _page(title: str, due: str | None) -> dict:
    props: dict = {"Name": {"title": [{"plain_text": title}]}}
    if due is not None:
        props["Due Date"] = {"date": {"start": due}}
    return {"properties": props}


def test_ranks_by_ascending_due_date_and_caps_at_three():
    pages = [
        _page("D", "2026-08-09"),
        _page("A", "2026-08-06"),
        _page("C", "2026-08-08"),
        _page("B", "2026-08-07"),
    ]
    lines = top3_lines(pages, TODAY)
    assert lines == [
        "🔵 A — tomorrow",
        "🔵 B — Fri",
        "🔵 C — Sat",
    ]


def test_missing_due_date_sorts_last():
    pages = [_page("No date", None), _page("Has date", "2026-08-06")]
    lines = top3_lines(pages, TODAY)
    assert lines[0] == "🔵 Has date — tomorrow"
    assert lines[1].startswith("⚪ No date")


def test_empty_pages_yields_no_lines():
    assert top3_lines([], TODAY) == []


def test_body_for_empty_uses_fallback_message():
    assert body_for([]) == EMPTY_MESSAGE


def test_body_for_joins_lines():
    body = body_for(["🔵 A — tomorrow", "🔵 B — Fri"])
    assert body == "🔵 A — tomorrow\n🔵 B — Fri"
