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
