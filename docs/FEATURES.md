# What this is — every feature explained

## The one-sentence version

Notion holds all your tasks, internships, and notes. A set of free scheduled robots
(GitHub Actions) do chores on a timer — summarizing email, reminding you of deadlines,
syncing tasks to your calendar, nudging you weekly, tidying old tasks, and drawing a
chart you can pin inside Notion.

## Part 1 — The Notion workspace

### Tasks database (the trimmed schema)
Kept deliberately lean — every property earns its place:
- **Name, Due Date, Status** — the core of a task.
- **Type** — CS / academics / personal / social / scholarships / extracurricular.
  This is what the Home page view switchers filter on.
- **Priority** (Low/Medium/High) — sorts your Today list and colors the pills.
- **Course** — finer subject tags (comp sci, math, physics, GE).
- **Note** — free text.
- **Archived** — hides finished clutter; the auto-archive robot writes to it.
- **GCal Event ID** (hidden) — lets the calendar sync update the right event instead
  of duplicating. You never touch this.
- **Stats** + four 0/1 counter formulas — the free progress-ring engine.

Removed as dead weight: Place, Done At (paid-only), Grade, and two unused helper
formulas.

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
Where the email robot drops its output, one dated page per run.

### Home dashboard
Collapsible sections: **Today & this week**, **All tasks** (one full-width panel with
switchable views), **At a glance** (progress · chart · internships), then calendar and
photos, then footer links.

## Part 2 — The automation layer (this repo)

- **A · Email digest — 8:00 AM & 6:00 PM.** Reads recent Gmail (read-only), has Claude
  Haiku summarize it, writes a page to Daily Digests. The evening run also appends
  **tomorrow's top 3** tasks so your brain pre-loads the next day.
- **B · Deadline reminders — 7:00 AM.** Unfinished tasks due within 3 days, pushed to
  your phone via ntfy.
- **C · Calendar sync — every 15 min.** Tasks with due dates become events on a
  dedicated "Tasks (Notion)" calendar; the event ID is written back to prevent
  duplicates. One-way; doesn't delete events.
- **D · Weekly review — Sunday 6:00 PM.** Only fires if the Notion checkbox is on.
  Pushes the week's tasks plus internship deadlines.
- **E · Auto-archive — 3:00 AM.** Archives tasks Done more than 7 days.
- **Dashboard — 6:00 AM.** Publishes aggregate counts as a Chart.js bar chart on
  GitHub Pages, embeddable in Notion.
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
