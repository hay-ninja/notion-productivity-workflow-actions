# Overnight run — paste this into Claude Code

Run from the repo root in a terminal that will stay awake. Host setup is at the
bottom; do that first.

---

You are working unattended overnight on this repository. Work autonomously and do not
wait for my input. Follow `todo.md` in order, top to bottom.

## Ground rules

1. **One task = one commit = one push.** Complete a task, verify it, commit, push,
   tick its checkbox in `todo.md`, then move on. Never batch tasks.
2. **All work happens on `overnight/hardening`.** Create that branch in T2. The only
   push to `main` is T1. Never force-push, never rebase, never `reset --hard`.
3. **Verify after every file change**, not at the end:
   ```
   python -m pytest -q && python -m ruff check .
   ```
   Fix failures before committing. Never commit a red tree.
4. **Commit messages:** plain, imperative, one line plus an optional short body. Do
   NOT add "Generated with Claude Code", do NOT add a `Co-Authored-By:` trailer, and
   do NOT mention Claude, AI, or any assistant in commit messages, code comments, or
   docs. The history must read as ordinary engineering work.
5. **No scope drift.** Only touch files the current task names. Do not refactor,
   rename, or restructure anything else. Do not add dependencies beyond `pytest` and
   `ruff`. Do not redesign the architecture — if you think something is wrong, write
   it under "Suggestions" in `overnight-progress.md` and move on.
6. **Never handle credentials.** Do not create, guess, echo, or commit API keys,
   tokens, or passwords. Do not run `gh secret set`. Do not enable or run any
   workflow that writes to Notion, sends a notification, or touches Google. Stop at
   any login prompt and log it.
7. **Do not touch my Notion workspace.** This run is repository work only.
8. **Log every task.** Append to `overnight-progress.md`: timestamp, task ID, what
   changed, verification result, commit SHA. If stuck, record what you tried and why
   it failed.

## Stop conditions — halt and write the reason in `overnight-progress.md`

- The same verification command fails twice in a row on the same task.
- A task would require a credential, a login, or a paid plan.
- You would need to modify `main`, force-push, or delete anything.
- You finish T11.
- You exceed 18 commits total.
- Any single task exceeds 25 tool calls without a passing verification.

When you stop for any reason, leave the working tree clean (everything committed and
pushed) and end with a one-paragraph summary of state.

## Definition of done

`todo.md` fully ticked, `overnight/hardening` pushed with ~10 commits beyond main,
tests and lint green, `WHEN-I-GET-BACK.md` written.

---

## Host setup — do this before pasting

**1. Prerequisites**
```powershell
winget install GitHub.cli
pip install pyyaml
gh auth login
```
Authenticate `gh` yourself so the agent never meets a credential prompt.

**2. Stop Windows sleeping**
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
```
Restore later with e.g. `powercfg /change standby-timeout-ac 30`.

**3. Keep the session alive.** Run in Windows Terminal and leave it open. Under WSL,
use `tmux new -s overnight` (detach `Ctrl-b d`, reattach `tmux attach -t overnight`).

**4. Permissions.** `.claude/settings.json` already restricts the toolset: it allows
read/write/edit, python, pytest, ruff and safe git, and denies `rm -rf`, `sudo`,
`curl`, force-push, pushes to `main`, `gh secret set`, and reading `.env`. It sets
`includeCoAuthoredBy: false` so no assistant attribution reaches your commits.

**5. Optional isolation.** After T1 you can run in a worktree so your copy is
untouched: `git worktree add ../nps-overnight overnight/hardening`
