---
description: Implement the planned tasks by dispatching executor subagents — sequential by default — each in a fresh context, making one atomic commit per task and updating STATE.md as it goes.
---

# Execute the plan

Follow `plugins/claudia-workflow/workflows/execute.md`.

Argument: `$ARGUMENTS` — optional task IDs to run (e.g. `T1 T2`).
