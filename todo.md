# Overnight task list

Work top to bottom. One task = one commit = one push. Do not start a task until the
previous one is verified, committed, pushed, and ticked.

After every file change run:

```
python -m pytest -q && python -m ruff check .
```

Fix failures before committing. Never commit red.

Scripts in this repo: `notion_lib.py`, `google_lib.py`, `email_digest.py`,
`deadline_reminders.py`, `gcal_sync.py`, `weekly_review.py`, `build_dashboard.py`.

---

- [x] **T1 — Publish to GitHub (main).**
      Create the public repo `notion-productivity-system`, add the remote, push the
      existing commits to `main`. This is the ONLY push to main.
      Verify: `gh repo view --web` resolves and history is intact.

- [x] **T2 — Disable cron schedules.**
      Create and switch to branch `overnight/hardening`. In every file under
      `.github/workflows/` except `validate.yml`, comment out the `schedule:` block,
      leaving `workflow_dispatch`. Without secrets the crons fail every 15 minutes.
      Verify: all workflow YAML still parses.

- [x] **T3 — Dev tooling.**
      Add `requirements-dev.txt` (pytest, ruff), a `pyproject.toml` with
      `[tool.ruff]` line-length 100, and `tests/__init__.py`.
      Verify: `pytest -q` runs and `ruff check .` passes.

- [x] **T4 — Tests for pure helpers.**
      `tests/test_notion_lib.py` covering only no-network functions: `iso_week`,
      `status_is`, `status_is_not`, `date_between`, `date_on_or_before`, and the
      `read_*` helpers using hand-built page dicts. ~15 focused assertions.

- [x] **T5 — Retry and backoff.**
      In `notion_lib.py` add a `_request()` wrapper used by `query_database`,
      `update_page`, `create_page`: up to 3 retries on HTTP 429 and 5xx with
      exponential backoff (1s, 2s, 4s), honouring `Retry-After` when present. Do not
      change public signatures. Add `tests/test_retry.py` with a monkeypatched
      session — no real network.

- [x] **T6 — Dashboard aggregation tests.**
      `tests/test_dashboard.py`: monkeypatch `query_database` to return fixed page
      dicts and assert `build_dashboard` produces correct `today`, `week`,
      `open_total`, and `by_type` counts, including the zero-task case (no division
      by zero). This is what the progress rings render, so it must be right.

- [ ] **T7 — `--dry-run` for every job.**
      Add an `argparse` `--dry-run` flag to `email_digest.py`,
      `deadline_reminders.py`, `gcal_sync.py`, `weekly_review.py`. In dry-run: read
      normally, perform NO writes and NO notifications, print what would happen.
      Add a test asserting dry-run never calls the write helpers.

- [ ] **T8 — Structured logging.**
      Replace bare `print()` in `scripts/` with the `logging` module (INFO to stdout,
      one-line format). Keep messages equivalent.

- [ ] **T9 — CI: lint and tests.**
      Extend `.github/workflows/validate.yml` to install `requirements-dev.txt` then
      run `ruff check .` and `pytest -q`, keeping the existing compile/YAML/.env
      checks.

- [ ] **T10 — Docs and handoff.**
      Write `WHEN-I-GET-BACK.md` at the repo root: an ordered list of what is left,
      every secret to create (where to get it, where to paste it), and any blockers
      hit overnight. Add a short "Development" section to `README.md` covering how to
      run tests and `--dry-run`.

- [ ] **T11 — Final sweep.**
      Run the full verification once more, append a summary to
      `overnight-progress.md`, push, and STOP. Do not open a pull request. Do not
      merge to main.
