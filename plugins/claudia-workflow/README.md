# clavia-workflow

A phased, control-first development workflow for Claude Code. GSD-shaped:
explicit phase commands, persistent state, and a config file of toggles — with
a **review gate** in front of every direction-locking artifact and every
outward action.

## Prerequisites

- Claude Code with this plugin enabled.
- The `gh-workflow` plugin (for `/clavia-ship`, which delegates to
  `/gh-pr-draft`).

## The workflow

Each command is invoked explicitly. `/clavia-progress` tells you where you are.

| Command | Phase | Output |
|---|---|---|
| `/clavia-map` | Map an existing codebase | `.planning/CONTEXT.md` |
| `/clavia-new` | Start a project, build the roadmap | `PROJECT.md`, `ROADMAP.md`, `config.json` |
| `/clavia-discuss` | Pin down design decisions | `.planning/DECISIONS.md` |
| `/clavia-plan` | Research + task breakdown | task list in `STATE.md` |
| `/clavia-execute` | Implement tasks via subagents | code + atomic commits |
| `/clavia-verify` | Two-stage review | verification report |
| `/clavia-ship` | Open a PR (via `gh-workflow`) | pull request |
| `/clavia-progress` | Where am I / what's next | reads `STATE.md` |
| `/clavia-settings` | Edit `.planning/config.json` | updated config |

## State — `.planning/`

Persists across sessions; agents reload it cold. Kept out of git by default.

- `PROJECT.md` — vision and scope
- `ROADMAP.md` — phases
- `CONTEXT.md` — codebase baseline
- `DECISIONS.md` — design choices made in discussion
- `STATE.md` — current position, task list, resume notes
- `config.json` — mode, model profile, agent toggles

## Configuration — `config.json`

Created from [config.template.json](config.template.json) by `/clavia-new`.

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
