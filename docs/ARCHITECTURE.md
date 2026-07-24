# Architecture

## Principle

Notion is the **single source of truth**. GitHub Actions is a *stateless* scheduler:
each run reads from Notion (and Gmail/Calendar), does one job, writes back or pushes a
notification, and exits. No database in this repo, no server to keep alive.

## Why GitHub Actions instead of a self-hosted runner

An earlier design used n8n in a container. It worked, but it's a long-running box you
must patch and restart, a silent crash stops everything, and the logic lives as JSON
blobs rather than reviewable code. Actions removes the server, logs every run, and
versions the logic as Python. Tradeoff: cron is UTC-only and can drift 5–15 minutes —
fine for daily jobs.

## Jobs

| Job | Reads | Writes | Notifies |
|-----|-------|--------|----------|
| A digest | Gmail | Daily Digests (+ tomorrow's top 3 in the evening) | — |
| B reminders | tasks (due <= 3 days) | — | ntfy |
| C gcal sync | tasks (with due dates) | tasks `GCal Event ID`, Google Calendar | — |
| D weekly review | tasks + internships + settings toggle | — | ntfy (if on) |
| E auto-archive | tasks (Done > 7 days) | tasks `Archived` | — |
| dashboard | tasks (aggregates) | `site/data/stats.json` -> Pages | — |

## Chart embed flow

```
tasks DB --(Action aggregates)--> site/data/stats.json
        --(Pages deploy)--> https://<user>.github.io/<repo>/
        --(/embed block)--> Notion Home
```
Published JSON contains only aggregate counts — never task titles.

## Timezone / DST

Date logic is timezone-aware via `zoneinfo` (America/Los_Angeles). **Cron schedules
are UTC and do not observe DST** — they're set for PDT (UTC-7) and run an hour early
during PST until you shift them.

## Known limitations

- Sync is one-way; archiving a task stops updates but leaves the event.
- Rings undercount tasks created without a template (free plan has no auto-relations).
- A failed Action shows red in the Actions tab but doesn't alert you.
