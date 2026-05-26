# Claude Code Instructions

This file provides guidance to Claude Code when working with files in this repository.

## Project Overview

This is **claudia** — a personal Claude Code framework for Python and Nextflow development. It bundles reusable instructions, agents, rules, and skills in a single Claude Code plugin (`plugins/claudia/`).

The framework is **control-first**: every direction-locking artifact and every outward action passes through a review gate ([plugins/claudia/rules/common/review-gate.md](plugins/claudia/rules/common/review-gate.md)) before it is accepted.

> **Migrating from claudia v1.** The v2 layout is a breaking redesign. The old `claudia_tools` package, per-task `.planning/` files (ISSUE_BRIEF/ROADMAP/DECISIONS/STATE/VERIFICATION/ENVIRONMENT), and the `/claudia-*` command set are gone. Re-run `/claudia understand` to regenerate `CONTEXT.md` in the new shape (merged with the env section).

## Architecture

The repo has one top-level piece worth knowing about:

- **`plugins/claudia/`** — the Claude Code plugin. Holds the single `/claudia` command, the skill set, the agent set, the rule set, and a tiny shared script. See [plugins/claudia/README.md](plugins/claudia/README.md).

Inside the plugin:

- **`plugins/claudia/scripts/claudia`** — a single-file Python script (~250 LOC, stdlib-only) exposing four subcommands: `detect`, `config (init|get|set)`, `env capture`, and `rules inject`. Invoked as `python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia <cmd>`.
- **`plugins/claudia/skills/`** — every workflow step is a skill. There is no separate `workflows/` directory.
- **`plugins/claudia/agents/`** — specialised subagents (planner, executor, verifier, researcher, code-reviewer, nextflow-reviewer, domain-reviewer, pr-reviewer, code-explorer).
- **`plugins/claudia/commands/`** — exactly **one** file: `claudia.md`. Everything else routes through the dispatcher skill.

## Always-on rules

The plugin's rule files are inlined here via `@`-imports so they apply to every skill, agent, and command execution.

@plugins/claudia/rules/common/review-gate.md
@plugins/claudia/rules/common/code-review.md
@plugins/claudia/rules/common/coding-style.md
@plugins/claudia/rules/common/commit-style.md
@plugins/claudia/rules/common/patterns.md
@plugins/claudia/rules/common/security.md
@plugins/claudia/rules/common/testing.md
@plugins/claudia/rules/python/coding-style.md
@plugins/claudia/rules/python/fastapi.md
@plugins/claudia/rules/python/patterns.md
@plugins/claudia/rules/python/security.md
@plugins/claudia/rules/python/tests.md

(In a consuming project, run `/claudia rules` to inject the same `@`-import block into the project's own `CLAUDE.md`.)

## Entry point — `/claudia`

`/claudia` is the **only** command exposed by the plugin. It routes in two modes:

1. **Explicit verb** — `/claudia <verb> [args]` invokes the matching skill directly, no NLP.
2. **Natural language** — `/claudia <free-form>` matches against a keyword table; ambiguous matches surface as `AskUserQuestion`.

The known verbs are:

| Verb | Skill | Purpose |
|---|---|---|
| `understand` | `claudia:understand` | One-time bootstrap → writes `.planning/CONTEXT.md` + `.planning/config.json`. Re-runnable as `refresh`. |
| `plan` | `claudia:plan` | Plan a task; optionally seed from a GitHub issue. Writes `.planning/plans/YYYY-MM-DD-<slug>.md`. |
| `execute` | `claudia:execute` | Implement the plan's tasks, one at a time. Branches on `mode` (`pair`/`yolo`). |
| `close` | `claudia:close` | Verify + draft + open (or hand off) a PR. Verifier dispatches `code-reviewer` + conditional `nextflow-reviewer`/`domain-reviewer` in parallel. |
| `rules` | `claudia:rules` | Inject the Claudia Rules section into the project's `CLAUDE.md` (idempotent, detect-aware). |
| `pr-review` | `claudia:pr-review` | Local-only structured GitHub PR review (delegates to `pr-reviewer` agent). |
| `write-issue` | `claudia:write-issue` | Draft + create a GitHub issue, gated on user confirmation. |
| `add-type-hints` | `claudia:add-type-hints` | Dual-mode: explicit verb AND auto-triggered by description. |
| `prepare-docstrings` | `claudia:prepare-docstrings` | Dual-mode: explicit verb AND auto-triggered by description. |

`/claudia` with no args prints the available verbs, the current branch, the current `mode`, and the most recent plan file — replacing what used to be `/claudia-progress`.

The authoritative routing table lives in [plugins/claudia/skills/claudia/SKILL.md](plugins/claudia/skills/claudia/SKILL.md).

## Skills

Plugin skills are namespaced `claudia:<name>`. Three categories:

**Auto-triggered only** (knowledge skills, fire by description match):

- `claudia:python-testing` — pytest TDD guidance
- `claudia:python-patterns` — non-obvious Python patterns
- `claudia:nextflow-testing` — nf-test patterns
- `claudia:nextflow-patterns` — production-ready DSL2 habits

**Callable only** (workflow + utility skills, fire via `/claudia <verb>`):

- `claudia:understand`, `claudia:plan`, `claudia:execute`, `claudia:close`
- `claudia:rules`, `claudia:pr-review`, `claudia:write-issue`

**Dual-mode** (auto-triggered AND callable):

- `claudia:add-type-hints` — `/claudia add-type-hints <path>` or auto-trigger from context
- `claudia:prepare-docstrings` — `/claudia prepare-docstrings <path>` or auto-trigger from context

## Per-task artifacts

Each task produces **one file** at `.planning/plans/YYYY-MM-DD-<slug>.md` with four sections: `## Intent`, `## Design decisions`, `## Tasks` (checkboxes), `## Notes`. TodoWrite tracks in-session progress; the checkbox state in `## Tasks` is the only on-disk persistence for execution. There is no `STATE.md`, no `VERIFICATION.md`.

Project-level artefacts are `.planning/CONTEXT.md` (narrative + an env section managed by `claudia env capture --section`) and `.planning/config.json` (`{ mode, agents }`).

## Agents

Workflow agents (called by skills):

- `planner` — task breakdown for `claudia:plan`
- `executor` — implement one task in a fresh context, called by `claudia:execute`
- `verifier` — orchestrates two-stage review for `claudia:close`; **must dispatch `code-reviewer` + conditional reviewers in parallel**
- `researcher` — read-only investigation, called by `claudia:plan` and `claudia:understand`

Review agents (dispatched by `verifier`):

- `code-reviewer` — always
- `nextflow-reviewer` — when `.nf` / `nextflow.config` in the diff
- `domain-reviewer` — when `agents.domain_reviewer == true` AND pipeline diff

Utility agents:

- `pr-reviewer` — used by `claudia:pr-review`
- `code-explorer` — used by `claudia:understand` for deep architecture / call-chain tracing, only when concrete dispatch triggers fire (focus hint names a subsystem; mixed/nextflow project with layered structure; explicit `trace` arg). Complementary to `researcher`, not a substitute.

## Shared script — `plugins/claudia/scripts/claudia`

| Subcommand | Purpose |
|---|---|
| `claudia detect` | Report project type: `python` / `nextflow` / `mixed` / `unknown`. |
| `claudia config init|get|set` | Manage `.planning/config.json`. Schema: `{ mode, agents }`. |
| `claudia env capture [--section]` | Probe local tool versions. With `--section`, rewrites the sentinel-bounded `## Environment` section of `.planning/CONTEXT.md`. |
| `claudia rules inject [--dry-run]` | Idempotently inject the `## Claudia Rules` section into the project's `CLAUDE.md`. Sentinel-bounded; detect-aware. |

All subcommands emit a JSON envelope: `{ok, data}` on success, `{ok, error}` on failure. No `uv tool install` — invoke directly with `python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia <cmd>`.

## Development Notes

- Primary language: **Python** — all rules, prompts, and examples assume Python unless stated otherwise.
- Rules format: one convention per file, with a clear title, explanation, and code example.
- Skills format: one folder per skill containing `SKILL.md` with `name` + `description` frontmatter.

## Editing Guidelines

Follow these formats when adding or editing files:

- **Agents** ([plugins/claudia/agents/](plugins/claudia/agents/)): YAML frontmatter with `name`, `description`, `model`; add `tools` only to restrict access — omit it when the agent needs MCP tools.
- **Skills** ([plugins/claudia/skills/](plugins/claudia/skills/)): one folder per skill containing `SKILL.md`; frontmatter with `name` and `description`. Workflow skills add `Do NOT auto-trigger; callable-only` to the description so the dispatcher does not auto-fire them.
- **Rules** ([plugins/claudia/rules/](plugins/claudia/rules/)): focused on a single convention; use a short title, one-paragraph explanation, and a code example. Add new rule files to the `@`-imports block above so they become always-on. The injector at `claudia rules inject` will pick them up automatically based on directory name (`common/`, `python/`, `nextflow/`).
- **Plugin manifest** ([plugins/claudia/.claude-plugin/plugin.json](plugins/claudia/.claude-plugin/plugin.json)): single source of truth for plugin metadata. The `commands` array must remain exactly `[claudia]`.

File naming: lowercase with hyphens.

## What NOT to do

- Do not add new commands. The plugin exposes only `/claudia`; new capabilities are skills routed by the dispatcher.
- Do not re-introduce a workflows directory. Skills carry the procedures directly.
- Do not hand-edit the sentinel-bounded `## Environment` or `## Claudia Rules` sections — always go through the deterministic script.
- Do not create deeply nested folder structures.
- Do not generate placeholder files — only create files with real content.
