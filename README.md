# Notion Productivity System

lil side project for fun to help me stay on top of things -> complements my notion system v2
want to learn how to use github actions a little for some automation purposes + dabble in some more github features like github pages

**GitHub Actions** runs the automation on a schedule and **GitHub Pages** is used for embedded charts for notion.

> Built by haydn (me).

## Why this exists

notion kinda sucks on free plan (or at least i can't figure out how to use it well).
wanted to use n8n to do some automation and stuff, but honestly after some research i think this is better and easier

this repo has
**scheduled GitHub Actions**: free, versioned, and every run leaves a visible log.

## What it does

| # | Job | Schedule (LA) | Engine |
|---|-----|---------------|--------|
| B | Deadline reminders (due within 3 days) | 07:00 | Actions + ntfy |
| C | Notion -> Google Calendar sync | hourly | Actions + GCal API |
| D | Weekly review ping (toggle-gated) | Sun 18:00 | Actions + ntfy |
| - | Tomorrow's top 3 | 18:00 | Actions + ntfy |
| - | Dashboard data -> Pages chart | 06:00 | Actions + Pages |

tomorrow's top 3 used to ride along with the daily email digest (now retired — it
needed a restricted inbox scope and a paid API key for output that wasn't worth
either). it's its own ping now.

^^ apparently supposed to be a good habit tip.

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
