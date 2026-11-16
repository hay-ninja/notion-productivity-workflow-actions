import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from insights import build_insights
from task_history import (
    empty_history,
    snapshot_from_pages,
    task_key,
    type_colors_from_pages,
    update_history,
)


def page(pid, status="Not started", due=None, types=("CS",), created="2026-11-01T18:00:00.000Z",
         edited="2026-11-01T18:00:00.000Z"):
    return {
        "id": pid,
        "created_time": created,
        "last_edited_time": edited,
        "properties": {
            "Name": {"title": [{"plain_text": "SECRET TITLE"}]},
            "Status": {"status": {"name": status}},
            "Due Date": {"date": {"start": due} if due else None},
            "Type": {"multi_select": [{"name": t, "color": "purple"} for t in types]},
            "Course": {"multi_select": []},
        },
    }


def snap(*pages):
    return snapshot_from_pages(list(pages))


def test_snapshot_has_no_titles_or_raw_ids():
    s = snap(page("abc-123"))
    blob = repr(s)
    assert "SECRET" not in blob
    assert "abc-123" not in blob and "abc123" not in blob
    assert s[0]["key"] == task_key("abc-123")


def test_created_day_uses_los_angeles_time():
    # 03:00 UTC on Nov 2 is still Nov 1 in LA
    s = snap(page("a", created="2026-11-02T03:00:00.000Z"))
    assert s[0]["created"] == "2026-11-01"


def test_bootstrap_estimates_completion_from_last_edit():
    h = update_history(empty_history(), snap(
        page("a", status="Done", due="2026-11-05", edited="2026-11-04T20:00:00.000Z")),
        date(2026, 11, 10))
    rec = h["tasks"][task_key("a")]
    assert rec["done_on"] == "2026-11-04"
    assert rec["done_est"] is True
    assert h["since"] == "2026-11-10"


def test_completion_detected_between_snapshots_uses_edit_day():
    h = update_history(empty_history(), snap(page("a", due="2026-11-12")), date(2026, 11, 10))
    # finished the evening of Nov 10 (LA), seen by the 6 AM run on Nov 11
    h = update_history(h, snap(page("a", status="Done", due="2026-11-12",
                                    edited="2026-11-11T04:00:00.000Z")), date(2026, 11, 11))
    rec = h["tasks"][task_key("a")]
    assert rec["done_on"] == "2026-11-10"
    assert rec["done_est"] is False


def test_edit_day_is_clamped_to_snapshot_window():
    h = update_history(empty_history(), snap(page("a")), date(2026, 11, 10))
    h = update_history(h, snap(page("a", status="Done", edited="2026-10-01T00:00:00.000Z")),
                       date(2026, 11, 12))
    assert h["tasks"][task_key("a")]["done_on"] == "2026-11-10"


def test_reopening_clears_completion():
    h = update_history(empty_history(), snap(page("a", status="Done")), date(2026, 11, 10))
    h = update_history(h, snap(page("a", status="In progress")), date(2026, 11, 11))
    assert h["tasks"][task_key("a")]["done_on"] is None


def test_pushes_count_only_later_due_dates():
    h = update_history(empty_history(), snap(page("a", due="2026-11-12")), date(2026, 11, 10))
    h = update_history(h, snap(page("a", due="2026-11-14")), date(2026, 11, 11))
    h = update_history(h, snap(page("a", due="2026-11-13")), date(2026, 11, 12))
    h = update_history(h, snap(page("a", due="2026-11-20")), date(2026, 11, 13))
    rec = h["tasks"][task_key("a")]
    assert rec["pushes"] == 2
    assert rec["first_due"] == "2026-11-12"


def test_deleted_tasks_marked_gone_but_kept():
    h = update_history(empty_history(), snap(page("a"), page("b")), date(2026, 11, 10))
    h = update_history(h, snap(page("a")), date(2026, 11, 11))
    assert h["tasks"][task_key("b")]["gone"] is True
    assert h["daily"]["2026-11-11"]["open"] == 1


def test_type_colors_come_from_notion():
    assert type_colors_from_pages([page("a", types=("CS",))]) == {"CS": "purple"}


def test_insights_on_empty_history_do_not_crash():
    ins = build_insights(update_history(empty_history(), [], date(2026, 11, 10)),
                         date(2026, 11, 10))
    assert ins["load"]["headline"] == "Nothing due in the next 7 days."
    assert ins["timing"]["ready"] is False
    assert ins["stale"]["count"] == 0
    assert ins["heatmap"]["days"][-1]["date"] == "2026-11-10"


def test_insights_finish_timing_and_load():
    today = date(2026, 11, 20)
    pages = [page(f"d{i}", status="Done", due="2026-11-10",
                  edited="2026-11-08T20:00:00.000Z") for i in range(8)]
    pages += [page("o1", due="2026-11-21"), page("o2", due="2026-11-21"),
              page("late", due="2026-11-01", edited="2026-11-01T20:00:00.000Z")]
    h = update_history(empty_history(), snap(*pages), today)
    ins = build_insights(h, today)
    assert ins["timing"]["ready"] is True
    assert ins["timing"]["headline"].startswith("You usually finish 2 days early")
    assert ins["load"]["days"][1]["count"] == 2
    assert ins["load"]["overdue"] == 1
    assert ins["stale"]["count"] == 3  # nothing edited in the last week
