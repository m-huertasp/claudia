# Workflow — `/claudia-map`

Produce `.planning/CONTEXT.md` from an existing repository.

Argument: `$ARGUMENTS` — optional focus hint. Empty means: map the whole repo.

## Steps

1. **Ensure `.planning/` exists.** Create it if needed; add `.planning/` to
   `.gitignore` unless the user has opted in to tracking it.
2. **Explore.** Dispatch the `code-explorer` agent (or explore directly for a
   small repo): entry points, module layout, data flow, dependencies.
3. **Detect the stack** — language and version, package manager, test
   runner, lint/type tooling — from manifests (`pyproject.toml`,
   `nextflow.config`, etc.), not guesses.
4. **Identify sensitive areas** — data directories, credential files,
   embargoed or patient data. See the secure-ai-use rule.
5. **Render `CONTEXT.md`.** Use the bundled template:
   ```
   claudia template render plugins/claudia/templates/CONTEXT.md \
       --var name=<project> --output .planning/CONTEXT.md
   ```
   Then fill in the prose hint placeholders (`<...>`) with what you
   verified.

## Review gate

`CONTEXT.md` is reference, not direction-locking — no accept/cancel gate.
Present a summary so the user can correct it before later phases rely on it.

## Rules

- Report only what you verified. Mark anything uncertain as an unknown
  rather than guessing.
- Never read or quote contents of files in sensitive areas.
