# claudia-workflow

A phased, control-first development workflow for Claude Code. GSD-shaped:
explicit phase commands, persistent state, and a config file of toggles — with
a **review gate** in front of every direction-locking artifact and every
outward action.

## Prerequisites

- Claude Code with this plugin enabled.
- The [`claudia-tools`](../../claudia_tools/) Python package, installed and
  on PATH as the `claudia` console script — every workflow command calls it
  for deterministic operations on the `.planning/` files:
  ```bash
  uv tool install ./claudia_tools     # or pipx install ./claudia_tools
  claudia --help
  ```
- The `gh-workflow` plugin (for `/claudia-ship`, which delegates to
  `/gh-pr-draft`).

## Architecture — commands, workflows, CLI

Each `/claudia-*` command file in `commands/` is a thin entry point: it
carries the slash-command frontmatter and a single pointer to the matching
file in `workflows/`. The full orchestration text — steps, review gates,
rules, and explicit `claudia` CLI invocations — lives in the workflow file.

This means:

- **Commands** stay small and easy to scan.
- **Workflows** can grow without bloating the command surface.
- Every deterministic operation (state update, config read/write, phase
  status transition, template render, gate acceptance) goes through the
  tested `claudia` CLI rather than the model hand-editing JSON or Markdown.

See [`workflows/README.md`](workflows/README.md) for the full mapping.

## The workflow

Each command is invoked explicitly. `/claudia-progress` tells you where you are.

| Command | Phase | Output |
|---|---|---|
| `/claudia-map` | Map an existing codebase | `.planning/CONTEXT.md` |
| `/claudia-new` | Start a project, build the roadmap | `PROJECT.md`, `ROADMAP.md`, `config.json` |
| `/claudia-discuss` | Pin down design decisions | `.planning/DECISIONS.md` |
| `/claudia-plan` | Research + task breakdown | task list in `STATE.md` |
| `/claudia-execute` | Implement tasks via subagents | code + atomic commits |
| `/claudia-verify` | Two-stage review | verification report |
| `/claudia-ship` | Open a PR (via `gh-workflow`) | pull request |
| `/claudia-progress` | Where am I / what's next | reads `STATE.md` |
| `/claudia-settings` | Edit `.planning/config.json` | updated config |

## State — `.planning/`

Persists across sessions; agents reload it cold. Kept out of git by default.

- `PROJECT.md` — vision and scope
- `ROADMAP.md` — phases
- `CONTEXT.md` — codebase baseline
- `DECISIONS.md` — design choices made in discussion
- `STATE.md` — current position, task list, resume notes
- `config.json` — mode, model profile, agent toggles

## Configuration — `config.json`

Created from [config.template.json](config.template.json) by `/claudia-new`.

| Setting | Values | Effect |
|---|---|---|
| `mode` | `interactive`, `yolo` | `interactive` confirms each phase; `yolo` auto-proceeds |
| `model_profile` | `quality`, `balanced`, `budget` | which model each agent role uses |
| `agents.researcher` / `.planner` / `.verifier` | `true` / `false` | toggle quality agents on/off |
| `execution.parallel` | `true` / `false` | run executor tasks in waves (default `false`, sequential) |

The review gate and the secret scan are **not** configurable — they always run.

## Agents

`researcher`, `planner`, `executor`, `verifier` — each dispatched with a fresh
context. `verifier` runs a two-stage review: spec compliance, then code
quality.
