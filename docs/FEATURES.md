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
- **GCal Event ID** (hidden) — the event this task maps to. The sync derives it from
  the page ID, so it can't duplicate even if this is blank. You never touch this.

Removed as dead weight: Place, Done At (paid-only), Grade, Priority (never used),
Archived (redundant once views filter by status), and three unused helper formulas.
Views hide finished work with a native Status filter (To-do + In progress), so there is
no archive flag and no auto-archive job.

### Internships
Company, Role, Status (Researching → Applied → OA → Interview → Offer / Rejected /
Withdrawn), Application Deadline, Applied Date, Link, Notes, Priority. Pipeline board
+ deadlines view.

### Automations Settings
One row with a **Weekly Review Ping** checkbox — the on/off switch for the Sunday
nudge (your finals-week kill switch).

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
- **Dashboard — 6:00 AM.** Snapshots every task into a daily history, then publishes
  two embeddable Pages views:
  - `index.html` — the compact progress rings (today / this week / open).
  - `insights.html` — the full page: next-7-days load vs. your usual pace, overdue and
    stale counts, backlog trend, finish timing (days early/late, by Type), weekly
    rhythm, pushed-back due dates, planning lead time, and a completion heatmap.
    Each card leads with a one-line takeaway; habit cards say "collecting data" until
    there's enough history (about 2–3 weeks).
- **Validate (CI).** Runs on every push: scripts compile, YAML parses, no `.env`
  committed.

## Privacy
Data stays in Notion. The repo stores code, not data. Secrets live in GitHub Actions
Secrets. Only anonymized counts are ever published to Pages. The task history on the
`dashboard-history` branch holds no titles and no raw Notion IDs — just a short hash,
dates, status and Type/Course tags.

## Known limits
- Calendar sync is one-way and never deletes events.
- Completion and push-back dates are tracked to the day (one snapshot each morning).
  Tasks finished before tracking began get their completion day estimated from their
  last edit; the page footnotes how many.
- Cron is UTC and doesn't shift for daylight saving (drifts 1h in winter).
- Notion's free plan allows one chart per workspace.
