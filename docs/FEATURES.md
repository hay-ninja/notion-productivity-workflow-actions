# What this is — every feature explained

## The one-sentence version

Notion holds all your tasks, internships, and notes. A set of free scheduled robots
(GitHub Actions) do chores on a timer — reminding you of deadlines, syncing tasks to
your calendar, nudging you weekly, previewing tomorrow's top 3, and drawing a chart
you can pin inside Notion.

## Part 1 — The Notion workspace

### Tasks database (the trimmed schema)
Kept deliberately lean — every property earns its place:
- **Name, Due Date, Status** — the core of a task.
- **Type** — CS / academics / personal / social / scholarships / extracurricular.
  This is what the Home page view switchers filter on.
- **When** — a formula that color-codes each task by due date: 🔴 overdue, 🟡 today,
  🔵 this week, ⚪ later, ✅ done. Updates itself, never blank.
- **Course** — finer subject tags (comp sci, math, physics, GE).
- **Note** — free text.
- **GCal Event ID** (hidden) — lets the calendar sync update the right event instead
  of duplicating. You never touch this.
- **Stats** + four 0/1 counter formulas — the free progress-ring engine.

Removed as dead weight: Place, Done At (paid-only), Grade, Priority (never used),
Archived (redundant once views filter by status), and three unused helper formulas.
Views hide finished work with a native Status filter (To-do + In progress), so there is
no archive flag and no auto-archive job.

### Dashboard Stats
One hidden row that sums the counters and renders progress for today and this week.
Set the property display to **Ring** for the circular look. *Quirk:* tasks created
without a template don't auto-link here, so bulk-link occasionally or the rings
undercount.

### Internships
Company, Role, Status (Researching → Applied → OA → Interview → Offer / Rejected /
Withdrawn), Application Deadline, Applied Date, Link, Notes, Priority. Pipeline board
+ deadlines view.

### Automations Settings
One row with a **Weekly Review Ping** checkbox — the on/off switch for the Sunday
nudge (your finals-week kill switch).

### Daily Digests
Legacy — was where the email digest wrote its output. That job has been retired, so
this database is no longer written to; safe to archive.

### Home dashboard
Collapsible sections: **Today & this week**, **All tasks** (one full-width panel with
switchable views), **At a glance** (progress · chart · internships), then calendar and
photos, then footer links.

## Part 2 — The automation layer (this repo)

- **B · Deadline reminders — 7:00 AM.** Unfinished tasks due within 3 days, pushed to
  your phone via ntfy.
- **C · Calendar sync — hourly.** Tasks with due dates become events on a
  dedicated "Tasks (Notion)" calendar; the event ID is written back to prevent
  duplicates. One-way; doesn't delete events. Set to hourly (not */15) because GitHub
  throttles free-tier schedules heavily — a */15 cron only ever actually ran roughly
  every 1-2 hours.
- **D · Weekly review — Sunday 6:00 PM.** Only fires if the Notion checkbox is on.
  Pushes the week's tasks plus internship deadlines.
- **Tomorrow's top 3 — 6:00 PM.** The most useful part of the old email digest,
  kept as its own job: the top 3 unfinished tasks due tomorrow or earlier, pushed to
  your phone via ntfy.
- **Dashboard — 6:00 AM.** Publishes aggregate counts as a chart on GitHub Pages,
  embeddable in Notion.
- **Validate (CI).** Runs on every push: scripts compile, YAML parses, no `.env`
  committed.

## Privacy
Data stays in Notion. The repo stores code, not data. Secrets live in GitHub Actions
Secrets. Only anonymized counts are ever published to Pages.

## Known limits
- Calendar sync is one-way and never deletes events.
- Rings undercount tasks created without a template.
- Cron is UTC and doesn't shift for daylight saving (drifts 1h in winter).
- Notion's free plan allows one chart per workspace.
