---
description: Close out the issue — run a final secret scan and CONTEXT.md drift check, then invoke the internal draft-pr workflow. In yolo mode the PR is pushed and created; in pair mode the draft title and body are printed for the user to open the PR themselves.
---

# Close the issue

Follow `plugins/claudia/workflows/close.md`.

Argument: `$ARGUMENTS` — optional base branch override (e.g. `base:dev`).
Passed through to the internal draft-pr workflow.
