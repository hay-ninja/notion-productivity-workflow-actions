# Overnight run — paste this into Claude Code

Run it from the repo root, in a terminal that will stay awake (see "Before you start").

---

You are working unattended overnight on this repository. Work autonomously and do not
wait for my input. Follow `todo.md` in order, top to bottom.

## Ground rules

1. **One task = one commit = one push.** Complete a task, verify it, commit it, push
   it, tick its checkbox in `todo.md`, then move to the next. Never batch tasks.
2. **All work happens on the branch `overnight/hardening`.** Create it after T1. The
   only push to `main` is T1 (publishing the 3 existing commits). Never force-push,
   never rebase, never reset --hard.
3. **Verify after every file change**, not at the end:
   ```
   python -m pytest -q && python -m ruff check .
   ```
   If it fails, fix it before committing. Never commit a red tree.
4. **Commit messages:** plain and descriptive, imperative mood, one line plus an
   optional short body. Do NOT add "Generated with Claude Code", do NOT add a
   `Co-Authored-By:` trailer, do NOT mention Claude, AI, or any assistant anywhere in
   commit messages, code comments, or docs. The history should read as ordinary
   engineering work.
5. **No scope drift.** Only touch files a task names. Do not refactor, rename, or
   restructure anything outside the current task. Do not add dependencies beyond
   `pytest` and `ruff`. Do not redesign the architecture — if you believe something is
   wrong, write it in `overnight-progress.md` under "Suggestions" and move on.
6. **Never handle credentials.** Do not create, guess, echo, or commit API keys,
   tokens, or passwords. Do not run `gh secret set`. Do not enable or run any workflow
   that writes to Notion, sends a notification, or touches Google. Stop at any login
   prompt and log it.
7. **Keep a running log.** After every task, append to `overnight-progress.md`:
   timestamp, task ID, what changed, verification result, commit SHA. If you get
   stuck, write what you tried and why it failed.

## Stop conditions — halt immediately and write the reason in `overnight-progress.md`

- The same verification command fails twice in a row on the same task.
- A task would require a credential, a login, or a paid plan.
- You would need to modify `main`, force-push, or delete anything.
- You reach the end of `todo.md` (T10).
- You have made more than 15 commits total — something has gone wrong.
- Any task has taken more than 20 tool calls without a passing verification.

When you stop for any reason, leave the working tree clean (everything committed and
pushed) and end with a one-paragraph summary of state.

## Definition of done

`todo.md` fully checked off, `overnight/hardening` pushed with ~9 commits after the
initial 3 on main, tests and lint green, and `WHEN-I-GET-BACK.md` written.

---

## Before you start (host setup)

**Windows — stop the machine sleeping:**
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
```
(Restore later with e.g. `powercfg /change standby-timeout-ac 30`.)

**Keep the session alive:** run inside Windows Terminal and don't close it. If you use
WSL, run under `tmux` so a dropped connection doesn't kill the run:
```
tmux new -s overnight
```
Detach with `Ctrl-b d`, reattach with `tmux attach -t overnight`.

**Permissions:** `.claude/settings.json` in this repo already restricts the toolset —
it allows read/write/edit, python, pytest, ruff, and safe git, while denying
`rm -rf`, `sudo`, force-push, pushes to `main`, `gh secret set`, and reading `.env`.
It also sets `includeCoAuthoredBy: false` so no assistant attribution is added to
commits.

**Isolation (optional but recommended):** run in a dedicated worktree so your working
copy is untouched:
```
git worktree add ../nps-overnight overnight/hardening
```

**Auth:** log in to `gh` yourself first (`gh auth login`) so the agent never sees a
credential prompt.
