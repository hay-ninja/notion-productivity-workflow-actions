# Overnight progress log

Append one entry per task. Format:

```
## [T#] <task name> — <ISO timestamp>
- Changed: <files>
- Verify: pytest <result>, ruff <result>
- Commit: <sha>
- Notes/blockers:
```

## Suggestions
(Anything you'd redesign but were told not to — record it here instead of doing it.)

---

## [T1] Publish to GitHub (main) — 2026-07-26T00:00:00
- Changed: none
- Verify: n/a
- Commit: n/a
- Notes/blockers: Repo already has an origin remote (github.com/hay-ninja/notion-productivity-workflow-actions) with main pushed. Per operator decision, skipping repo creation/push — treating T1 as already satisfied by the existing origin. Proceeding to T2 on a new branch; no push to main performed this run.

## [T2] Disable cron schedules — 2026-07-26T00:05:00
- Changed: .github/workflows/{dashboard,deadline-reminders,email-digest,gcal-sync,weekly-review}.yml
- Verify: YAML parse OK for all 6 workflow files, ruff n/a (no python changed)
- Commit: 27a4585
- Notes/blockers: none

## [T3] Dev tooling — 2026-07-26T00:15:00
- Changed: requirements-dev.txt, pyproject.toml, tests/__init__.py; scripts/notion_lib.py (removed unused `timedelta` import — required for a clean ruff baseline)
- Verify: pytest exits 5 (no tests yet, expected pre-T4), ruff check . passes
- Commit: a6a5f44
- Notes/blockers: pyproject.toml pins [tool.ruff.lint] select to E4/E7/E9/F (ruff's conventional default) so the linter targets real errors/unused code rather than opinionated style rules across the whole existing codebase.

## [T4] Tests for pure helpers — 2026-07-26T00:30:00
- Changed: tests/test_notion_lib.py (new)
- Verify: pytest 18 passed, ruff check . passes
- Commit: 86e06fc
- Notes/blockers: local Windows dev env needed `tzdata` and `requests`/google deps installed to import notion_lib.py at all (zoneinfo has no OS tz database on Windows); not added to requirements.txt since CI runs on ubuntu-latest with system tzdata — local-only setup note.

## [T5] Retry and backoff — 2026-07-26T00:45:00
- Changed: scripts/notion_lib.py (added `_request()` wrapper used by query_database/update_page/create_page), tests/test_retry.py (new)
- Verify: pytest 24 passed, ruff check . passes
- Commit: 47d3f2f
- Notes/blockers: public signatures of query_database/update_page/create_page unchanged; _request accepts an optional `session` for testability without touching real network.

## [bugfix] Restore notion_lib.timedelta re-export — 2026-07-26T00:50:00
- Changed: scripts/notion_lib.py
- Verify: pytest 24 passed, ruff check . passes
- Commit: bab1061
- Notes/blockers: T3 removed `timedelta` from notion_lib.py's imports as an unused-import fix, but deadline_reminders.py, email_digest.py, weekly_review.py, and build_dashboard.py all call it as `n.timedelta(...)`. Restored the import with a `noqa: F401` explaining the re-export so ruff doesn't flag it again.

## [T6] Dashboard aggregation tests — 2026-07-26T01:00:00
- Changed: tests/test_dashboard.py (new)
- Verify: pytest 26 passed, ruff check . passes
- Commit: (pending)
- Notes/blockers: monkeypatches n.query_database to branch on filter shape (date_between vs status_is_not) since build_dashboard.main() issues several date-window queries and one open-status query; covers both a populated fixture and the zero-task case.
