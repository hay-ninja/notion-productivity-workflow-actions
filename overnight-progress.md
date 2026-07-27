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

- `notion_lib.py` re-exports `timedelta` from `datetime` purely so callers can write
  `n.timedelta(...)`. It's easy to break (T3 nearly did, see the bugfix entry above)
  and saves only one import line per caller. Worth having each script import
  `timedelta` directly from `datetime` instead, next time this file is touched.
- Five near-identical `argparse`/`--dry-run`/`logging.basicConfig` blocks were added
  across `email_digest.py`, `deadline_reminders.py`, `gcal_sync.py`,
  `weekly_review.py`, and `build_dashboard.py` in T7/T8. A tiny shared `cli.py`
  helper (parse args once, configure logging once) would remove the duplication,
  but that's a new module and wasn't in scope for either task.

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
- Commit: 89b8473
- Notes/blockers: monkeypatches n.query_database to branch on filter shape (date_between vs status_is_not) since build_dashboard.main() issues several date-window queries and one open-status query; covers both a populated fixture and the zero-task case.

## [T7] --dry-run for every job — 2026-07-26T01:20:00
- Changed: scripts/email_digest.py, scripts/deadline_reminders.py, scripts/gcal_sync.py, scripts/weekly_review.py, tests/test_dry_run.py (new)
- Verify: pytest 30 passed, ruff check . passes
- Commit: 2200dd8
- Notes/blockers: dry-run skips the single write/notify call in each script (create_page, ntfy_push x2, calendar events + update_page) and prints a summary instead; gcal_sync also skips constructing calendar_service() in dry-run since it isn't needed to compute the create/update counts.

## [T8] Structured logging — 2026-07-26T01:35:00
- Changed: scripts/{email_digest,deadline_reminders,gcal_sync,weekly_review,build_dashboard}.py
- Verify: pytest 30 passed, ruff check . passes
- Commit: a4fa7a8
- Notes/blockers: each script sets its own logging.basicConfig(INFO, one-line format) since each runs standalone via its own workflow step; messages kept equivalent to the prior print() output.

## [T9] CI lint and tests — 2026-07-26T01:45:00
- Changed: .github/workflows/validate.yml
- Verify: YAML parse OK, pytest 30 passed, ruff check . passes (same commands CI will run)
- Commit: 4398eb4
- Notes/blockers: kept the existing compile/YAML/.env steps and appended dependency install + ruff + pytest steps.

## [T10] Docs and handoff — 2026-07-26T01:55:00
- Changed: WHEN-I-GET-BACK.md (new), README.md (Development section)
- Verify: pytest 30 passed, ruff check . passes (docs-only change, verification re-run for safety)
- Commit: (pending)
- Notes/blockers: none
