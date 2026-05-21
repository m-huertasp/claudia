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
- For GitHub commands (`/claudia-write-issue`, `/claudia-draft-pr`,
  `/claudia-pr-review`, `/claudia-ship`): the [`gh` CLI](https://cli.github.com/)
  installed and authenticated:
  ```bash
  gh auth login        # interactive OAuth or PAT
  gh auth status       # verify
  ```
  Issues and PRs are created under the authenticated GitHub account — i.e.
  attributed to the user, not to Claude. Without `gh`, GitHub commands fail
  at the first `gh` call.

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
| `/claudia-understand` | One-time codebase bootstrap (re-runnable on drift) | `CONTEXT.md`, `ENVIRONMENT.md`, `config.json` |
| `/claudia-brief` | Start a new issue; chains into intent discuss | `ISSUE_BRIEF.md`, `DECISIONS.md` (intent), `{keyword}/{slug}` branch |
| `/claudia-plan` | Draft per-issue roadmap; chains into approach discuss | `ROADMAP.md`, `DECISIONS.md` (approach), tasks in `STATE.md` |
| `/claudia-execute` | Implement tasks via subagents | code + atomic commits |
| `/claudia-verify` | Two-stage review + checklist + drift check | verification report |
| `/claudia-ship` | Open a PR (delegates to `/claudia-draft-pr`); re-runs drift check | pull request |
| `/claudia-progress` | Where am I / what's next (read-only) | reads `STATE.md` |
| `/claudia-settings` | Edit `.planning/config.json` | updated config |

The discuss step is **not user-callable**. It runs internally from
`/claudia-brief` (intent mode) and `/claudia-plan` (approach mode), both
appending to a single `.planning/DECISIONS.md`.

Each `/claudia-*` command is a thin pointer. Full orchestration lives in
[`workflows/`](workflows/) and calls the `claudia` CLI for every
deterministic op.

### GitHub commands

| Command | Action | Writes to GitHub? |
|---|---|---|
| `/claudia-write-issue [owner/repo:] <description>` | Draft a structured issue and create it | Yes — after a confirmation gate |
| `/claudia-draft-pr [base:branch]` | Draft a PR for the current branch and create it | Yes — after an accept/refuse gate |
| `/claudia-pr-review <num\|owner/repo#num\|url>` | Structured review classified URGENT/HIGH/MEDIUM/LOW | **Never** — output stays in chat |

`/claudia-draft-pr` defaults the base branch to `dev`; override with
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

**Project-level** (written by `/claudia-understand`, refreshed on drift):

- `CONTEXT.md` — codebase baseline (architecture, stack, conventions, sensitive areas)
- `ENVIRONMENT.md` — tool-version snapshot
- `config.json` — mode, model profile, agent toggles

**Per-issue** (replaced on each `/claudia-brief`; previous set is archived under `.planning/archive/<timestamp>/`):

- `ISSUE_BRIEF.md` — what we're tackling and why
- `ROADMAP.md` — the phases to tackle it
- `DECISIONS.md` — intent-mode and approach-mode design choices
- `STATE.md` — current position, task list, resume notes
- `VERIFICATION.md` — human checklist gating `/claudia-ship`
- `gates.json` — review-gate acceptance ledger

## Configuration — `config.json`

Created from [config.template.json](config.template.json) by `/claudia-understand` (one-time, on first run).

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
- `/claudia-pr-review` and `pr-reviewer` **never post to GitHub**. No comment,
  review, approval, merge, or label change — output stays in chat.

## Install

Reference this repo as a marketplace and enable the `claudia` plugin. The
commands, agents, and skills register automatically. Then add the rule
`@`-imports to your project's `CLAUDE.md` (see Rules above) and install
`claudia_tools`.
