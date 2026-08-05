# Setup guide (start here)

If you haven't touched this in a while, read this page once before doing anything.

## Where you are

- **The Notion side is built** — tasks, internships, settings, Home dashboard.
- **This repo is the automation side.** The code is done. What's left is plugging in
  your accounts so the robots can log in.
- Nothing is "on" until you test it by hand. You can't break anything going slowly.

**Total time:** ~30 min. Step 4 (Google) is the only fiddly part — budget 10 min.

## Mental model

Each robot is a script that runs on GitHub's servers on a timer. To do its job it
needs to log into your services. You provide those logins as **GitHub Secrets** —
encrypted values the code reads but which never appear in the code. So setup is
really: *collect a handful of keys, paste each into GitHub Secrets.*

## Step 1 — Put the repo on GitHub (5 min)

```
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```
The project already has commits, so this just uploads it. Public is fine — no secrets
are in the code.

## Step 2 — Where secrets go

Repo **Settings → Secrets and variables → Actions → New repository secret.** Add one
per name in `.env.example` (database IDs are pre-filled there — copy them across).
Never commit a `.env`; the `validate` workflow fails the push if you do.

## Step 3 — Notion (10 min) — needed by every robot

1. **notion.so/my-integrations → New integration** (Internal). Copy the secret →
   `NOTION_TOKEN`.
2. **Share the three databases with the integration** — the #1 thing people forget. If
   you skip it the robots see nothing and fail silently. For each of tasks,
   Internships, Automations Settings: open it → `•••` → **Connections
   → Connect to →** your integration.
3. Add the `NOTION_TASKS_DB`, `NOTION_INTERNSHIPS_DB`, `NOTION_SETTINGS_DB` secrets
   from `.env.example`. `NOTION_DIGESTS_DB` is legacy (see Troubleshooting) and no
   longer read by anything — skip it unless you still have that database around.

> Checkpoint: you can now test the **dashboard** robot.

## Step 4 — Google (10 min) — for calendar sync

GitHub's servers can't click a login popup, so you generate a long-lived refresh token
once.

1. **console.cloud.google.com** → new project.
2. Enable the **Google Calendar API**.
3. **APIs & Services → Credentials → Create credentials → OAuth client ID → Desktop
   app.** Copy the client ID/secret → `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.
4. **developers.google.com/oauthplayground** → gear icon → check *Use your own OAuth
   credentials* → paste them. Authorize this scope:
   ```
   https://www.googleapis.com/auth/calendar.events
   ```
   Then *Exchange authorization code for tokens* → copy the **refresh token** →
   `GOOGLE_REFRESH_TOKEN`.
5. In Google Calendar create a calendar named **"Tasks (Notion)"**, timezone
   **(GMT-08:00) Los Angeles**. Settings → Integrate calendar → copy the **Calendar
   ID** → `GCAL_CALENDAR_ID`.
   - Don't reuse an old Zapier "notion" calendar (wrong timezone, stale events).

## Step 5 — Phone notifications (5 min)

1. Install the **ntfy** app (free, no account).
2. Subscribe to a long, unguessable topic — the name *is* the password →
   `NTFY_TOPIC`.
3. Test: `curl -d "hello" ntfy.sh/YOUR-TOPIC` → phone buzzes.

## Step 6 — Test each robot, then let it run

**Actions tab → pick a workflow → Run workflow.** In this order:

1. **Dashboard** — proves Notion reads work.
2. **B · Deadline Reminders** — phone buzzes (or correctly sends nothing).
3. **C · GCal Sync** — make a test task with a due date; confirm the event appears and
   `GCal Event ID` fills in. **Then turn any old Zapier zap OFF.**
4. **D · Weekly Review** — tick the Notion checkbox, run, untick.
5. **Tomorrow's Top 3** — phone buzzes with up to 3 tasks due tomorrow or earlier.

Each workflow is scheduled *and* manual, so passing the manual test means the timer is
live. To keep one off, comment out its `schedule:` block.

## Step 7 — Pin the chart in Notion

Settings → Pages → Source: **GitHub Actions**. After the Dashboard run, your chart is
at `https://<you>.github.io/<repo>/`. In Notion, `/embed` that URL.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Runs green but does nothing | Database not shared with the integration (Step 3.2). |
| `Missing required environment variable` | Secret not set or misspelled. |
| Auth error on calendar sync | Refresh token expired or wrong scope — redo Step 4.4. |
| Duplicate calendar events | Old Zapier zap still on. |
| Reminders an hour off in winter | Cron is UTC and ignores daylight saving. |
| No push notification | Topic mismatch, or ntfy notifications disabled on phone. |
| Daily Digests page never updates | Expected — the email digest job was retired. That database is legacy and safe to archive. |

## Secret checklist

- [ ] `NOTION_TOKEN` + tasks/Internships/Automations Settings shared
- [ ] `NOTION_TASKS_DB`, `NOTION_INTERNSHIPS_DB`, `NOTION_SETTINGS_DB`
- [ ] `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN`
- [ ] `GCAL_CALENDAR_ID`
- [ ] `NTFY_TOPIC`
- [ ] Pages set to deploy from Actions
