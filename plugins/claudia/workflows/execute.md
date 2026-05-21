# Workflow — `/claudia-execute`

Implement the open tasks in `.planning/STATE.md`, one fresh executor
context per task, one atomic commit per task.

Argument: `$ARGUMENTS` — optional task IDs (e.g. `T1 T2`). Empty means: all
open tasks.

## Steps

1. **Read state.**
   ```
   claudia state tasks
   claudia config get
   ```
2. **Order the tasks** by their declared dependencies.
3. **Dispatch executors.**
   - Sequential (default): one `executor` agent per task, in order.
   - Parallel (only if `execution.parallel` is `true`): independent tasks
     with satisfied dependencies in the same wave.
4. **After each task succeeds:**
   ```
   claudia state task-done T<N>
   ```
   Record the commit. If an executor stopped early (spec wrong, decision
   needed), **stop** and surface it to the user.
5. **When all tasks are done:**
   ```
   claudia state set last_command /claudia-execute
   claudia state set next_step /claudia-verify
   ```

## Review gate

Per-change gates are skipped here — review happens at `/claudia-verify`.
Pushing or opening a PR is never done in this workflow.

## Rules

- Executors stay within their task spec. Re-scoping goes back to the user.
- Keep `STATE.md` current after every task so the workflow can resume cold.
