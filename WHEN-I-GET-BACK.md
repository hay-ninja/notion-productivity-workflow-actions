# When I get back

Overnight run on branch `overnight/hardening`. Nothing was merged to `main`, nothing
was pushed to Notion or Google, and no secrets were touched. Here's what's left.

## What's left to do

1. **Review and merge `overnight/hardening` into `main`** (not done automatically —
   see "Suggestions" below for why).
2. **Re-enable the cron schedules** once secrets are in place (T2 commented them
   out to stop the workflows failing every run without credentials). In each of
   `.github/workflows/{dashboard,deadline-reminders,email-digest,gcal-sync,weekly-review}.yml`,
   uncomment the `schedule:` block.
3. **Add the GitHub Actions secrets** listed below, then run each workflow manually
   from the Actions tab with `workflow_dispatch` before trusting the cron.
4. **Decide on `notion-productivity-system` vs. the existing origin.** `todo.md`'s
   T1 asked for a new public repo named `notion-productivity-system`; this run found
   an existing origin (`hay-ninja/notion-productivity-workflow-actions`) already
   serving that purpose and used it instead rather than creating a second remote.
   Confirm that's what you want.

## Secrets to create

All of these come from `.env.example` — same names, add each as a repo secret
(Settings → Secrets and variables → Actions → New repository secret). None of them
were touched or guessed this run.

| Secret | Where to get it |
|---|---|
| `NOTION_TOKEN` | Notion → My Integrations → your integration → Internal Integration Secret |
| `NOTION_TASKS_DB` | Notion tasks database → Share → Copy link → the UUID in the URL |
| `NOTION_INTERNSHIPS_DB` | Same, for the internships database |
| `NOTION_SETTINGS_DB` | Same, for the settings database |
| `NOTION_DIGESTS_DB` | Same, for the digests database |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `ANTHROPIC_MODEL` | Optional; defaults to `claude-haiku-4-5-20251001` if unset |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google Cloud Console → APIs & Services → Credentials → OAuth client (Desktop app) |
| `GOOGLE_REFRESH_TOKEN` | Run the OAuth consent flow once locally with the client above and Gmail + Calendar scopes, capture the refresh token |
| `GCAL_CALENDAR_ID` | Google Calendar → Settings → the dedicated calendar → Integrate calendar → Calendar ID |
| `NTFY_TOPIC` | Pick a long, unguessable string yourself |
| `NTFY_SERVER` | Optional; defaults to `https://ntfy.sh` if unset |

## Blockers hit overnight

- None that stopped the run. `git push origin main` is denied by
  `.claude/settings.json`, and T1 was resolved by treating the existing origin
  remote as already satisfying "publish to GitHub" rather than pushing to main or
  creating a second repo — see `overnight-progress.md` T1 entry.
- A real bug was found and fixed along the way: T3's ruff cleanup removed
  `timedelta` from `notion_lib.py` as an apparently-unused import, but four other
  scripts call it as `n.timedelta(...)`. Caught while writing T6's dashboard tests
  and fixed before it reached `main`. See the `[bugfix]` entry in
  `overnight-progress.md`.

## Suggestions

See the "Suggestions" section of `overnight-progress.md` for anything flagged
during the run instead of acted on.
