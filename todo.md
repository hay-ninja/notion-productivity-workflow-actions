# Overnight task list

Rules: work top to bottom. One task = one commit = one push. Do not start a task until
the previous one is checked off and pushed. After every file change run:

```
python -m pytest -q && python -m ruff check .
```

If that command fails, fix it before committing. Never commit red.

---

- [ ] **T1 — Publish repo (main).**
      Create the public GitHub repo `notion-productivity-system`, add the remote, push
      the 3 existing commits to `main`. This is the ONLY push to main. Verify the repo
      is visible and the commit history shows 3 commits.

- [ ] **T2 — Disable cron schedules.**
      On branch `overnight/hardening`. In every file under `.github/workflows/` except
      `validate.yml`, comment out the `schedule:` block (leave `workflow_dispatch`).
      Reason: without secrets the crons fail every 15 min and spam failure emails.
      Verify: `python -c "import glob,yaml; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"`

- [ ] **T3 — Dev tooling.**
      Add `requirements-dev.txt` (pytest, ruff), a `[tool.ruff]` section in
      `pyproject.toml` (line-length 100), and a `tests/` package with `__init__.py`.
      Verify: `pytest -q` runs (0 tests is fine) and `ruff check .` passes.

- [ ] **T4 — Tests for pure helpers.**
      In `tests/test_notion_lib.py`, cover only functions needing no network:
      `iso_week`, `status_is`, `status_is_not`,
      `date_between`, `date_on_or_before`, and the `read_*` helpers using hand-built
      page dicts. Aim for ~15 focused assertions. Verify: `pytest -q` green.

- [ ] **T5 — Retry + backoff on Notion calls.**
      In `scripts/notion_lib.py`, add a small `_request()` wrapper used by
      `query_database`, `update_page`, `create_page`: retry up to 3 times on HTTP 429
      and 5xx with exponential backoff (1s, 2s, 4s), respecting `Retry-After` when
      present. Do not change function signatures. Add
      `tests/test_retry.py` using a fake session/monkeypatch — no real network.
      Verify: `pytest -q` green.

- [ ] **T6 — `--dry-run` for every job.**
      Add a `--dry-run` flag to `email_digest.py`, `deadline_reminders.py`,
      `gcal_sync.py`, `weekly_review.py`. In dry-run: read normally
      but perform NO writes and NO pushes — print what would happen instead. Use
      `argparse`. Verify: `pytest -q` green, plus a test asserting dry-run never calls
      the write helpers (monkeypatched).

- [ ] **T7 — Structured logging.**
      Replace bare `print()` in `scripts/` with the `logging` module (INFO to stdout,
      one-line format). Keep messages equivalent. Verify: `pytest -q` green,
      `ruff check .` clean.

- [ ] **T8 — CI: lint + tests.**
      Extend `.github/workflows/validate.yml` with steps that install
      `requirements-dev.txt` then run `ruff check .` and `pytest -q`. Keep the existing
      compile/YAML/.env checks. Verify: YAML parses.

- [ ] **T9 — Docs + handoff.**
      Write `WHEN-I-GET-BACK.md` at the repo root: ordered list of what is left for
      Haydn, every secret to create (where to get it, where to paste it), plus any
      blockers hit overnight. Update `README.md` with a short "Development" section
      (how to run tests, how to use `--dry-run`). Verify: `ruff check .` clean.

- [ ] **T10 — Final sweep.**
      Run the full verification once more, append a summary to `overnight-progress.md`,
      push, and STOP. Do not open a pull request. Do not merge to main.
