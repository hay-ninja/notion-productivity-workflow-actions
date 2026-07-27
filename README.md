# Notion Productivity System

A free automation layer for a personal Notion productivity workspace (tasks,
internships, daily digests, a progress dashboard). Notion stays the single source of
truth; **GitHub Actions** runs the automation on a schedule with no server to
maintain, and a **GitHub Pages** chart can be embedded back into Notion.

> Built by Haydn (UCLA). Timezone: America/Los_Angeles.

**New here or returning after a break?** Read `docs/FEATURES.md` for a plain-language
tour, then follow `docs/SETUP.md` to plug in your accounts.

## Why this exists

Notion's free plan is capped: one chart per workspace, no database automations, no
auto-relations. An earlier design used a self-hosted **n8n** container to fill those
gaps — powerful, but a fragile box to keep alive. This repo replaces it with
**scheduled GitHub Actions**: free, versioned, and every run leaves a visible log.
The commit history is the build story.

## What it does

| # | Job | Schedule (LA) | Engine |
|---|-----|---------------|--------|
| A | Email digest + tomorrow's top 3 | 08:00 & 18:00 | Actions + Claude Haiku |
| B | Deadline reminders (due within 3 days) | 07:00 | Actions + ntfy |
| C | Notion -> Google Calendar sync | every 15 min | Actions + GCal API |
| D | Weekly review ping (toggle-gated) | Sun 18:00 | Actions + ntfy |
| - | Dashboard data -> Pages chart | 06:00 | Actions + Pages |

The 18:00 digest also appends **tomorrow's top 3** tasks — the habit tip that one
protected focus block beats an elaborate system.

## Repo layout

```
.
|-- scripts/            Python for each job + shared Notion helper
|-- .github/workflows/  one YAML per job (crons in UTC) + validate.yml
|-- site/               GitHub Pages dashboard (index.html + generated data/)
|-- docs/               FEATURES, SETUP, ARCHITECTURE, NOTION-SCHEMA, TIPS
|-- .env.example        every secret the scripts read (no real values)
`-- requirements.txt
```

## Quick start

1. Read `docs/SETUP.md`.
2. Add each token from `.env.example` as a **GitHub Actions secret**.
3. Push. Run each workflow manually from the **Actions** tab before trusting cron.
4. Enable **Pages** (Settings -> Pages -> deploy from Actions) to publish the chart.

## Development

Install dev dependencies once:

```
pip install -r requirements.txt -r requirements-dev.txt
```

Run the test suite and linter:

```
pytest -q
ruff check .
```

Every scheduled job script (`email_digest.py`, `deadline_reminders.py`, `gcal_sync.py`,
`weekly_review.py`) accepts a `--dry-run` flag: it reads from Notion/Google normally
but makes no writes and sends no notifications, printing what it would have done
instead. Use it to sanity-check a change before letting cron run for real, e.g.:

```
python scripts/deadline_reminders.py --dry-run
```

## License

MIT — see `LICENSE`.
