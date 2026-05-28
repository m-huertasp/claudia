---
name: execute
description: Implement the open tasks in the active claudia plan file, one at a time, dispatching the executor agent in a fresh context per task. Use whenever the user says "execute", "implement the plan", "run the tasks", "work through the tasks", or "implement task T1". Ticks checkboxes in the plan as each task completes. Branches on `mode` (`pair` asks before each commit; `yolo` commits autonomously). Invoked via `/claudia execute [task-ids]`. Do NOT auto-trigger; callable-only workflow skill.
---

# Execute

> Invoke as: `/claudia execute [T1 T2 ...]`

**Input**: `$ARGUMENTS` — optional task IDs (e.g. `T1 T2`). Empty means: every
open task in the active plan.

---

## Purpose

Walk the task list in the active plan file and implement each task by
dispatching the `executor` agent in a fresh context. Per-session
progress lives in TodoWrite; on-disk persistence is the checkbox state
inside `## Tasks` of the plan file. There is no separate `STATE.md`.

## Preconditions

1. The active plan file exists at `.planning/plans/YYYY-MM-DD-<slug>.md`.
   If multiple plan files exist, pick the most recent (lexicographic
   sort by filename). If the user wants to target a different plan,
   they should say so in `$ARGUMENTS` (e.g. `/claudia execute --plan
   .planning/plans/2026-04-12-foo.md`). Refuse if no plan file is
   present and tell the user to run `/claudia plan` first.
2. The plan file's review gate has been accepted (i.e. the user signed
   off). Do not begin execution on an unaccepted draft.
3. `.planning/CONTEXT.md` exists. If missing, refuse and point the user
   at `/claudia understand` first — do not proceed without project
   context, even if a plan file is present.

## Read mode and tasks

Read the mode from the deterministic helper:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia config get mode
```

Resolution order if the call above fails or returns nothing:

1. Try the installed CLI directly: `claudia config get mode`.
2. Fall back to reading `.planning/config.json` and extracting the
   top-level `"mode"` field.
3. Only if all three fail, default to `pair` (the safer default).

Print the resolved mode and the source it came from before continuing,
so a misconfigured `yolo` project does not silently degrade to `pair`.

Parse the active plan's `## Tasks` section. Each line of the form
`- [ ] <task description>` is an open task; `- [x] ...` is done.
Assign a stable 1-based index to each task in file order (`T1`, `T2`,
...) so the user can target tasks by ID via `$ARGUMENTS` (e.g.
`/claudia execute T1 T3`). Populate TodoWrite with one entry per
selected open task — full list if `$ARGUMENTS` is empty, otherwise
just the requested IDs.

## Order

Run tasks in the order they appear in the plan file unless the user
overrode the selection with `$ARGUMENTS`. Tasks were sized by the
`planner` agent during `/claudia plan` so they are independently
verifiable; there is no parallel mode in v2.

## Loop, per task

1. **Set TodoWrite entry to `in_progress`** for this task.
2. **Dispatch the `executor` agent** with:
   - The task spec (ID, title, spec, "done when")
   - The `mode` signal (`pair` | `yolo`)
   - A reminder to honour `.planning/CONTEXT.md` and the rules block.

   The executor reads the project context, implements the task, runs
   the relevant tests, and reports back. It stays strictly within the
   task spec — re-scoping comes back to the user.

3. **Branch on mode** with the executor's report in hand.

### `yolo` branch

- The executor has already created **one atomic commit** matching
  the [`commit-style`](../../rules/common/commit-style.md) rule
  (`{type}: {description}`, no scope).
- Tick the checkbox in the plan file: replace the line
  `- [ ] T<N> — ...` with `- [x] T<N> — ...`.
- Mark the TodoWrite entry `completed`.
- If the executor stopped early (spec wrong, decision needed),
  surface it to the user and **stop** the loop.
- Continue to the next task.

### `pair` branch

- The executor reports the diff but **has not committed**. The working
  tree is dirty.
- Present to the user:
  - A short "Changes" summary (`file:line` per change) drawn from the
    executor's report.
  - The executor's suggested commit line in
    `{type}: {description}` form, ready to paste.
  - A reminder that they can edit any file freely before committing.
- Ask via `AskUserQuestion`:
  - **Done — I committed.** Before ticking, verify a commit actually
    landed: run `git log -1 --format=%h` and confirm the hash differs
    from the one captured **before** the executor dispatch, and that
    `git status --porcelain` is empty. If the working tree is still
    dirty or HEAD has not advanced, do **not** tick — re-ask the user
    (they may have hit Done by mistake). Otherwise tick the checkbox
    in the plan file, mark the TodoWrite entry `completed`, and
    continue to the next task.
  - **Skip this task.** Leave the checkbox unticked. Capture the
    reason via a free-text follow-up and append a note to the plan
    file's `## Notes` section: `- T<N> skipped: <reason>`.
  - **Abort.** End the loop now; do not tick any further checkboxes.

## Wrap-up

When all requested tasks have been processed (done, skipped, or
aborted):

- If every task in the plan is ticked, print a one-line "ready for
  `/claudia close`" message.
- Otherwise, list open tasks and remind the user that `/claudia execute`
  resumes where it left off.

## Review gate

Per-change gates are skipped here — review happens at `/claudia close`.
Pushing or opening a PR is never done in this skill. The pair-mode
"Done / Skip / Abort" prompt is **not** a review gate (it routes the
loop); the review gate is at close.

## Rules

- Executors stay within their task spec. Re-scoping goes back to the user.
- Keep the plan file's checkboxes current after every task so the
  skill can resume cold.
- In `pair` mode, never commit on the user's behalf — even with empty
  intent. The agent's job is to write code, not author commits.
- In `yolo` mode, every commit must match the
  [`commit-style`](../../rules/common/commit-style.md) format.
- Skill skips and aborts are persisted in the plan file's `## Notes`,
  not in any side file. The plan file remains the single source of
  truth.
