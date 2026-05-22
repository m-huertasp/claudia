# Workflow — `/claudia-understand`

One-time codebase bootstrap. Produces three project-level artifacts that
later issue-scoped commands rely on:

- `.planning/CONTEXT.md` — architecture, stack, conventions, sensitive areas
- `.planning/ENVIRONMENT.md` — tool-version snapshot via `claudia env capture`
- `.planning/config.json` — claudia mode, model profile, agent toggles

Re-runnable as a **refresh** when `/claudia-verify` or `/claudia-close`
detect drift in the codebase (new top-level dirs, new dependencies,
renamed key files).

Argument: `$ARGUMENTS` — optional. A subdirectory or subsystem to focus the
exploration on, or the literal token `refresh` to force a CONTEXT.md drift
pass on an already-initialized repo.

## Detect state

Before doing anything, decide which path to take based on what already
exists in `.planning/`:

| State on disk | Action |
|---|---|
| `.planning/` missing or empty | **First run** path below |
| All three files exist, no `refresh` arg, no drift | **No-op** — print status, point user at `/claudia-brief` |
| `refresh` arg, or drift detected by verify/ship | **Refresh** path below |

## First run

1. **Ensure `.planning/` exists.** Create it if needed; add `.planning/` to
   `.gitignore` unless the user has opted in to tracking it.
2. **Initialise the config:**
   ```
   claudia config init
   claudia config set mode <chosen>
   claudia config set model_profile <chosen>
   ```
   Use `AskUserQuestion` for the discrete choices.
3. **Explore.** Dispatch the `code-explorer` agent (or explore directly for a
   small repo): entry points, module layout, data flow, dependencies. Honour
   the `$ARGUMENTS` focus hint if given.
4. **Detect the stack** — language and version, package manager, test
   runner, lint/type tooling — from manifests (`pyproject.toml`,
   `nextflow.config`, etc.), not guesses.
5. **Identify sensitive areas** — data directories, credential files,
   embargoed or patient data. See the secure-ai-use rule.
6. **Render `CONTEXT.md`.** Use the bundled template:
   ```
   claudia template render plugins/claudia/templates/CONTEXT.md \
       --var name=<project> --output .planning/CONTEXT.md
   ```
   Then fill in the prose hint placeholders (`<...>`) with what you
   verified.
7. **Capture the environment** and write `ENVIRONMENT.md`:
   ```
   claudia env capture --name <project> --output .planning/ENVIRONMENT.md
   ```
   The captured `project_type` (output of `claudia detect`) determines which
   automated tests `/claudia-verify` will run. Manually fill the
   **Containers** and **Datasets** sections — `claudia env capture` never
   touches them.
8. **Advance state:**
   ```
   claudia state set last_command /claudia-understand
   claudia state set next_step /claudia-brief
   ```
   If `STATE.md` does not exist yet, this is fine — `/claudia-plan` will
   initialise it from its own template; `claudia state set` against a
   missing file should be deferred until `STATE.md` exists, so on a first
   run skip this step and rely on `/claudia-brief` setting state.

## Refresh

1. **Re-explore** the same areas, honouring the `$ARGUMENTS` focus hint.
2. **Re-render** `CONTEXT.md` against current repo state into a temp
   location, then diff against the existing file.
3. **Show the diff** to the user via `AskUserQuestion`: *apply diff* /
   *edit before applying* / *cancel*.
4. **`ENVIRONMENT.md` / `config.json`** are left alone unless the user
   explicitly opts in (`claudia env capture` is cheap; `config` changes go
   through `/claudia-settings`).

## Review gate

`CONTEXT.md` is reference, not strictly direction-locking — but a
controlled refresh pass shows the diff and asks before overwriting. On a
first run, present a summary so the user can correct it before later
phases rely on it.

## Rules

- Report only what you verified. Mark anything uncertain as an unknown
  rather than guessing.
- Never read or quote contents of files in sensitive areas.
- This command is **one-time** for first run; `/claudia-brief` will refuse
  to run if `CONTEXT.md` does not exist.
