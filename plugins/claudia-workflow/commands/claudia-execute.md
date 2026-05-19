---
description: Implement the planned tasks by dispatching executor subagents — sequential by default — each in a fresh context, making one atomic commit per task and updating STATE.md as it goes.
---

# Execute the plan

The user wants the planned tasks implemented. Each task runs in a fresh
`executor` context; progress is tracked in `.planning/STATE.md`.

Argument: `$ARGUMENTS` — optional task IDs to run (e.g. `T1 T2`). If empty,
run all open tasks.

## Steps

1. **Read** `STATE.md` for the open tasks, `config.json` for `mode` and
   `execution.parallel`, `CONTEXT.md` for conventions.
2. **Order the tasks** by their dependencies.
3. **Dispatch executors:**
   - **Sequential (default).** One `executor` agent per task, in order. After
     each, check the executor's report.
   - **Parallel** (only if `execution.parallel` is `true`). Run independent
     tasks — those with satisfied dependencies — in the same wave.
4. **After each task:** mark it done in `STATE.md`'s task list, record the
   commit. If an executor stopped early (spec wrong, decision needed),
   **stop** and surface it to the user — in `interactive` mode always; in
   `yolo` mode still stop for spec problems.
5. **When all tasks are done**, update `STATE.md`: next step = `/claudia-verify`.

## Review gate

Routine code edits inside a task do **not** need a per-change gate — they are
reviewed at `/claudia-verify`. But anything outward-facing (a push, a PR) is
never done here — that is `/claudia-ship`. If an executor needs a decision,
that pause is the gate: ask the user before continuing.

## Rules

- Executors stay within their task spec. A task that needs re-scoping goes
  back to the user, not improvised.
- Do not push or open PRs from this command.
- Keep `STATE.md` current after every task so the workflow can resume cold.
