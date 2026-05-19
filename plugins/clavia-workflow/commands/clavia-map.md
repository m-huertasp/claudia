---
description: Analyze an existing codebase — stack, architecture, conventions, sensitive areas — and write .planning/CONTEXT.md so later phases are grounded in the real repo.
---

# Map the codebase

The user wants `clavia` to understand an existing repository before any
planning. Produce `.planning/CONTEXT.md`.

Argument: `$ARGUMENTS` — optional focus hint (a subdirectory or subsystem). If
empty, map the whole repo.

## Steps

1. **Ensure `.planning/` exists.** Create it if needed, and add it to
   `.gitignore` unless the user has opted in to tracking it.
2. **Explore.** Dispatch the `code-explorer` agent (or explore directly for a
   small repo): entry points, module layout, data flow, dependencies.
3. **Detect the stack** — language and version, package manager, test runner,
   lint/type tooling — from manifests (`pyproject.toml`, `nextflow.config`,
   etc.), not guesses.
4. **Identify sensitive areas** — data directories, credential files,
   embargoed or patient data. See the secure-ai-use rule. List them so later
   agents avoid them.
5. **Write `.planning/CONTEXT.md`** from the template, filling every section.

## Review gate

`CONTEXT.md` is reference, not direction-locking — it does not need an
accept/cancel gate. But **present a summary** of what you found (stack,
key files, sensitive areas) so the user can correct it before it is relied on.
If they correct something, update the file.

## Rules

- Report only what you verified in the repo. Mark anything uncertain as an
  unknown rather than guessing.
- Never read or quote the contents of files in sensitive areas.
