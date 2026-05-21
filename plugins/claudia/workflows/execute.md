# Workflow — `/claudia-execute`

Implement the open tasks in `.planning/STATE.md`, one task at a time,
branching on **mode** (`pair` or `yolo`) read from `.planning/config.json`.
The executor agent does the same work in both modes; only the
commit/handoff step differs.

Argument: `$ARGUMENTS` — optional task IDs (e.g. `T1 T2`). Empty means: all
open tasks.

## Read state and mode

```
claudia state tasks
claudia config get mode
```

If `mode` is missing or unreadable, treat it as `pair` (safer default).

## Order

Order the open tasks by their declared dependencies. In `pair` mode,
ignore `execution.parallel` — pair-programming is one task at a time so
the user can review. In `yolo` mode, `execution.parallel=true` permits
parallel waves of independent tasks.

## Loop, per task

1. **Dispatch the executor** with the task spec and `mode=<pair|yolo>`.
   The agent reads `.planning/CONTEXT.md`, implements the task, runs
   tests, and reports back. See [agents/executor.md](../agents/executor.md).
2. **Branch on mode** with the executor's report in hand.

### `yolo` branch

- Executor has already created **one atomic commit** matching the
  `commit-style.md` rule (`{type}: {description}`, no scope).
- Mark the task done:
  ```
  claudia state task-done T<N>
  ```
- If the executor stopped early (spec wrong, decision needed), surface
  it to the user and **stop** the loop.
- Continue to the next task.

### `pair` branch

- Executor reports the diff but **has not committed**. The working tree
  is dirty.
- Present:
  - A short "Changes" summary (`file:line` per change) drawn from the
    executor's report.
  - The executor's suggested commit line in `{type}: {description}`
    form, so the user can paste it as-is when they commit.
  - A reminder that the user can edit any file freely before committing.
- `AskUserQuestion` with three options:
  - **Done — I committed.** Continue to the next task.
  - **Skip this task.** Leave it open. Capture the reason via a quick
    free-text prompt and append it to the `## Notes for the next session`
    section of `STATE.md`.
  - **Abort.** Stop the loop now.
- On **Done**:
  ```
  claudia state task-done T<N>
  ```
  Optionally offer a follow-up `AskUserQuestion`: *add a note about how
  you did it?* (free text → append to `## Notes for the next session`).
- On **Skip**: leave the task unchecked; loop continues to the next task.
- On **Abort**: end the workflow here; advance state below with
  `next_step` unchanged from whatever was in `STATE.md` before.

## Finally

When all requested tasks have been processed (done, skipped, or the user
aborted):

```
claudia state set last_command /claudia-execute
claudia state set next_step /claudia-verify
```

If the user aborted with open tasks still pending, **do not** advance
`next_step` past `/claudia-execute` — the resume point is still execute.

## Review gate

Per-change gates are skipped here — review happens at `/claudia-verify`.
Pushing or opening a PR is never done in this workflow. The pair-mode
"Done / Skip / Abort" prompt is **not** a review gate (it routes the
loop); the review gate is at verify.

## Rules

- Executors stay within their task spec. Re-scoping goes back to the user.
- Keep `STATE.md` current after every task so the workflow can resume cold.
- In `pair` mode, never commit on the user's behalf — even with empty
  intent. The agent's job is to write code, not author commits.
- In `yolo` mode, every commit must match the
  [`commit-style`](../rules/common/commit-style.md) format.
