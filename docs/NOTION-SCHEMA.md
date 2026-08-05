# Notion Schema

Free plan. Timezone: America/Los_Angeles.

## tasks
- DB `fc4118b4-e0c5-4113-a6e7-3ffa5b9513c3` · ds `7fb507e6-6e7a-48d5-98bd-b7361fe55539`
- **Name** (title), **Due Date** (date), **Status** (STATUS-type: Not started /
  In progress / Done), **Type** (multi-select: personal, academics, CS, social,
  scholarships, extracurricular, nothing), **Course** (multi-select), **Note** (text), **When** (formula: date color-coding),
  **GCal Event ID** (text, hidden), **Stats** (relation -> Dashboard Stats).
- Ring engine formulas: Due Today (n), Done Today (n), Due Week (n), Done Week (n) —
  0/1 counters, logic inlined, Done check = `format(prop("Status")) == "Done"`.
- Removed 2026-07: Place, Done At, Grade, Days Until Due, Is This Week, Priority,
  Archived, Open?.
- Views hide finished work with a native **Status is To-do / In progress** filter set in
  the UI (the view DSL cannot write status filters — see gotcha 2).

## Dashboard Stats
- DB `1f3d1984-79a5-4e05-b154-d3d0e06a110b` · ds `db41793b-4cb0-4498-a7e9-bb37a5e62538`
- Single row "Stats". Tasks (relation), 4 rollup SUMs, Ring — Today / Ring — This Week.
- Set the ring properties to **Show as → Ring**, format Percent (UI-only).

## Internships
- DB `4c6eb655-397b-41e9-ac6b-ce43f2459cfd` · ds `a2befdb5-5332-478b-ac5f-b03ce903a2db`
- Company (title), Role, Status (SELECT), Application Deadline, Applied Date, Link,
  Notes, Priority. Views: Pipeline board, Deadlines <= 14 days.

## Automations Settings
- DB `3b15bfb9-f38f-4ca3-ba9c-32e164ad53d7` — one row, `Weekly Review Ping` checkbox.

## Daily Digests
- DB `dfc03151-9269-417f-bc0b-87ec9fa422f7` — Name (title) + Date. Legacy: was the
  target of the email digest job, which has been retired. No longer written to.

## Home
- Page `3965c1d1-502c-814b-8764-e6b36b7960a7`. Collapsible sections via `<details>`:
  Today & this week · All tasks · At a glance. Then calendar/photos, footer links.

## API gotchas (do not re-learn)
1. tasks `Status` is STATUS-type -> REST filters use `"status": {...}`; Internships
   `Status` is SELECT -> `"select": {...}`.
2. **The view DSL cannot filter on status-type properties** — `=`, `!=`, and OR-groups
   all produce empty filters. Add status filters in the UI.
3. View DSL has no `LIMIT` and no date-granularity (`GROUP BY "Due Date" WEEK` fails);
   set row limits and week grouping in the UI.
4. Formula creation via API: function-style only (`and()`, `or()`, `not()`); no `!`,
   `lets()`, or `repeat()`. Formulas can't reference other formulas — inline them.
5. Views can't be deleted via API. Charts: free plan allows one per workspace.
6. Page markdown: `<columns>/<column>` for layout, `<details><summary>` for
   collapsible sections. `<database url=...>` tags only *move* existing blocks —
   to add a linked view use `create_view` with `parent_page_id` (it appends at the
   page end), then reposition with `update_content`.
