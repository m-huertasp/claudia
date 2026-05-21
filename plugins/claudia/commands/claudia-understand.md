---
description: One-time codebase bootstrap — analyze stack, architecture, conventions, sensitive areas, and capture environment + config. Writes .planning/CONTEXT.md, .planning/ENVIRONMENT.md, and .planning/config.json. Re-runnable as a refresh when verify/ship detect drift.
---

# Understand the codebase

Follow `plugins/claudia/workflows/understand.md`.

Argument: `$ARGUMENTS` — optional focus hint (a subdirectory or subsystem),
or `refresh` to force a CONTEXT.md drift pass on an already-initialized repo.
