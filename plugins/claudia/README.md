# claudia (plugin)

The unified Claude Code plugin for Python and Nextflow development. One
plugin holds everything: phased workflow commands, GitHub commands, shared
subagents, skills, rules, and templates.

It is **control-first**: every direction-locking artifact and every outward
action passes through a review gate before it is accepted.

## Prerequisites

- Claude Code with this plugin enabled (commands, agents, and skills are
  auto-discovered from the plugin's subfolders).
- The [`claudia-tools`](../../claudia_tools/) Python package, installed and
  on PATH as the `claudia` console script — every workflow calls it for
  deterministic operations on `.planning/` files:
  ```bash
  uv tool install ../../claudia_tools     # or pipx install
  claudia --help
  ```
- For GitHub commands (`/gh-*` and `/claudia-ship`): the official `github`
  MCP plugin and a token set in the environment:
  ```bash
  export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx   # repo + read:org scopes
  ```
  Without the MCP server, GitHub commands fail at the first MCP call.

## Entry points

### `/claudia` — natural-language dispatcher

The primary entry point. Routes free-form requests to the right skill or
workflow command. Examples:

- `/claudia prepare docstrings of pipeline.py`
  → invokes the `claudia:prepare-docstrings` skill
- `/claudia ship` → routes to `/claudia-ship`
- `/claudia plan phase 2` → routes to `/claudia-plan`

When intent is ambiguous, the dispatcher asks via `AskUserQuestion` rather
than silently guessing. Direct slash commands still work too.

### Phased workflow commands

| Command | Phase | Output |
|---|---|---|
| `/claudia-map` | Map an existing codebase | `.planning/CONTEXT.md` |
| `/claudia-new` | Start a project, build the roadmap | `PROJECT.md`, `ROADMAP.md`, `config.json` |
| `/claudia-discuss` | Pin down design decisions | `.planning/DECISIONS.md` |
| `/claudia-plan` | Research + task breakdown | task list in `STATE.md` |
| `/claudia-execute` | Implement tasks via subagents | code + atomic commits |
| `/claudia-verify` | Two-stage review + checklist | verification report |
| `/claudia-ship` | Open a PR (delegates to `/gh-pr-draft`) | pull request |
| `/claudia-progress` | Where am I / what's next (read-only) | reads `STATE.md` |
| `/claudia-settings` | Edit `.planning/config.json` | updated config |

Each `/claudia-*` command is a thin pointer. Full orchestration lives in
[`workflows/`](workflows/) and calls the `claudia` CLI for every
deterministic op.

### GitHub commands

| Command | Action | Writes to GitHub? |
|---|---|---|
| `/gh-issue [owner/repo:] <description>` | Draft a structured issue and create it | Yes — after a confirmation gate |
| `/gh-my-issues [filters]` | List issues assigned to me, grouped by repo | No |
| `/gh-my-prs [filters]` | List PRs I authored / am review-requested on | No |
| `/gh-pr-draft [base:branch]` | Draft a PR for the current branch and create it | Yes — after an accept/refuse gate |
| `/gh-pr-review <num\|owner/repo#num\|url>` | Structured review classified URGENT/HIGH/MEDIUM/LOW | **Never** — output stays in chat |

`/gh-pr-draft` defaults the base branch to `dev`; override with
`base:main`. Read commands never mutate; write commands always show a draft
first.

## Skills (`skills/`)

Plugin skills are namespaced `claudia:<name>`. Trigger them through `/claudia`
or directly:

| Skill | Purpose |
|---|---|
| `claudia:prepare-docstrings` | Write/homogenise NumPy/SciPy docstrings |
| `claudia:add-type-hints` | Infer and add type annotations |
| `claudia:python-testing` | pytest TDD |
| `claudia:python-patterns` | Non-obvious Python patterns |
| `claudia:nextflow-patterns` | Production-ready Nextflow DSL2 habits |
| `claudia:nextflow-testing` | nf-test patterns |

## Agents (`agents/`)

| Agent | Role |
|---|---|
| `researcher` | Read-only investigation → findings brief |
| `planner` | Roadmap phase → ordered task breakdown |
| `executor` | Implements one task, one atomic commit |
| `verifier` | Two-stage review: spec compliance, then code quality |
| `code-explorer` | Deep codebase exploration |
| `code-reviewer` | General code review (quality, security) |
| `nextflow-reviewer` | Nextflow DSL2 review (reproducibility, channels, nf-test) |
| `domain-reviewer` | Bioinformatics output sanity |
| `pr-reviewer` | Confidence-gated PR review (never posts) |

## Rules (`rules/`)

`common/` and `python/` rule files. **Not auto-loaded by the plugin** —
consumer projects should `@`-import them from their root `CLAUDE.md` so
they become always-on context for every skill, agent, and workflow:

```markdown
@plugins/claudia/rules/common/review-gate.md
@plugins/claudia/rules/common/coding-style.md
@plugins/claudia/rules/python/coding-style.md
... etc.
```

This is how skills inherit project conventions without per-skill edits.

## State — `.planning/`

Persists across sessions; agents reload it cold. Kept out of git by default.

- `PROJECT.md` — vision and scope
- `ROADMAP.md` — phases
- `CONTEXT.md` — codebase baseline
- `DECISIONS.md` — design choices made in discussion
- `STATE.md` — current position, task list, resume notes
- `VERIFICATION.md` — human checklist gating `/claudia-ship`
- `ENVIRONMENT.md` — tool-version snapshot
- `config.json` — mode, model profile, agent toggles
- `gates.json` — review-gate acceptance ledger

## Configuration — `config.json`

Created from [config.template.json](config.template.json) by `/claudia-new`.

| Setting | Values | Effect |
|---|---|---|
| `mode` | `interactive`, `yolo` | `interactive` confirms each phase; `yolo` auto-proceeds |
| `model_profile` | `quality`, `balanced`, `budget` | which model each agent role uses |
| `agents.researcher` / `.planner` / `.verifier` | `true` / `false` | toggle quality agents on/off |
| `execution.parallel` | `true` / `false` | run executor tasks in waves (default `false`, sequential) |

The **review gate** and the **secret scan** are not configurable — they
always run.

## Safety model (GitHub)

- Read commands never mutate.
- Write commands always show a full draft and require explicit confirmation
  via `AskUserQuestion`. Editing the draft re-triggers the gate.
- `/gh-pr-review` and `pr-reviewer` **never post to GitHub**. No comment,
  review, approval, merge, or label change — output stays in chat.

## Install

Reference this repo as a marketplace and enable the `claudia` plugin. The
commands, agents, and skills register automatically. Then add the rule
`@`-imports to your project's `CLAUDE.md` (see Rules above) and install
`claudia_tools`.
