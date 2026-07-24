# Research notes — what to steal, what to avoid

Distilled from how other engineers build personal productivity systems.

## The biggest risk: over-engineering

There's a named failure mode — "the Notion Sunday": you sit down to organize the
system, and three hours later you've redesigned the task database and done zero real
work. Engineers over-build because requirements feel murky, so they prepare for every
hypothetical.

**The fix:** KISS, YAGNI, MVP. Ship the layout, use it two weeks, and only add
something when a *real* pain shows up three times — not a hypothetical one.

## One mental model: GTD + PARA

- **GTD** runs tasks: capture → clarify → organize → reflect → engage.
- **PARA** organizes information: Projects (time-bound), Areas (ongoing), Resources,
  Archives.

Mapping here: the tasks DB is the GTD engine; CS / academics / personal are PARA
Areas; the weekly review job *is* the GTD "reflect" step; the internships tracker is a
textbook PARA Project. Knowing which system each part serves stops you from cramming
reference notes into the task list.

## Free Notion tricks worth adopting

- **Recurring tasks are native now.** Add a "Recur interval" number property and a
  Button using `dateAdd()` to push the due date and reset Status. No third-party tool.
- **Buttons** can create a task with defaults pre-filled — including the Stats
  relation, which fixes the ring undercount at the source.
- **Repeating database templates** auto-appear on a schedule.
- Caveat: full database *automations* (auto-triggered) need paid Notion. Buttons and
  template recurrence are the free equivalents.

## GitHub Actions as a personal cron server

This is a recognized pattern, not a hack — engineers call it exactly that. Other ideas
that fit a student/dev: a daily Hacker News or subreddit digest into Notion, an
auto-updating README, deadline/cert expiry pingers. Caveat: free cron isn't
minute-exact.

## The part a system can't do for you

The strongest finding across sources: **one protected daily focus block beats an
elaborate setup.** "I code 9–11am every day" works because it removes the decision.
And writing tomorrow's key tasks at end of day pre-loads your brain — which is why the
evening digest in this repo appends **tomorrow's top 3**.
