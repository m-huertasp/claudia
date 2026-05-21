# Claude Code Instructions

This file provides guidance to Claude Code when working with files in this repository.

## Project Overview

This is **claudia** — a personal Claude Code framework for Python and Nextflow development. It provides a phased, control-first development workflow plus reusable instructions, agents, rules, and skills bundled in a single Claude Code plugin (`plugins/claudia/`).

The framework is **control-first**: every direction-locking artifact and every outward action passes through a review gate ([plugins/claudia/rules/common/review-gate.md](plugins/claudia/rules/common/review-gate.md)) before it is accepted.

## Architecture

The repo has two top-level pieces:

- **`plugins/claudia/`** — the unified Claude Code plugin. Holds commands, workflows, agents, skills, rules, templates, and the plugin manifest. See [plugins/claudia/README.md](plugins/claudia/README.md).
- **`claudia_tools/`** — Python package exposing the `claudia` CLI: the deterministic engine the workflow calls for every state/config/phase/template/gate/detect/env/verify operation. Install with `uv tool install ./claudia_tools`.

## Always-on rules

The plugin's rule files are inlined here via `@`-imports so they apply to
every skill, agent, and workflow execution without per-skill modification.

@plugins/claudia/rules/common/review-gate.md
@plugins/claudia/rules/common/code-review.md
@plugins/claudia/rules/common/coding-style.md
@plugins/claudia/rules/common/patterns.md
@plugins/claudia/rules/common/security.md
@plugins/claudia/rules/common/testing.md
@plugins/claudia/rules/python/coding-style.md
@plugins/claudia/rules/python/fastapi.md
@plugins/claudia/rules/python/patterns.md
@plugins/claudia/rules/python/security.md
@plugins/claudia/rules/python/tests.md

## Entry point — `/claudia` dispatcher

The primary entry point. `/claudia <natural-language request>` routes to the
right skill or workflow command. Examples:

- `/claudia prepare docstrings of pipeline.py` → `claudia:prepare-docstrings`
- `/claudia ship` → `/claudia-ship`
- `/claudia plan phase 2` → `/claudia-plan`

When intent is ambiguous, the dispatcher asks via `AskUserQuestion`. Direct
slash commands still work.

## Skills

Plugin skills are namespaced `claudia:<name>`. Triggered through `/claudia`,
invoked directly, or auto-triggered by description matching:

- `claudia:prepare-docstrings` — write or homogenize docstrings (NumPy/SciPy format)
- `claudia:add-type-hints` — infer and add type annotations
- `claudia:python-testing` — write pytest tests using TDD
- `claudia:python-patterns` — non-obvious Python patterns
- `claudia:nextflow-patterns` — production-ready Nextflow DSL2 habits
- `claudia:nextflow-testing` — nf-test patterns

## Key Commands

### Development workflow

A phased, control-first workflow. Each command is invoked explicitly; state persists in `.planning/`. See [plugins/claudia/README.md](plugins/claudia/README.md).

- `/claudia-map` — analyze an existing codebase → `.planning/CONTEXT.md`
- `/claudia-new` — start a project, build the roadmap → `PROJECT.md`, `ROADMAP.md`, `ENVIRONMENT.md`, `config.json`
- `/claudia-discuss` — pin down design decisions before planning → `DECISIONS.md`
- `/claudia-plan` — research + ordered task breakdown → `STATE.md`
- `/claudia-execute` — implement tasks via executor subagents (sequential by default)
- `/claudia-verify` — two-stage review + secret scan; for pipelines, generates a human checklist in `VERIFICATION.md`
- `/claudia-ship` — open a PR via `/gh-pr-draft`; blocked by `claudia verify ready` until the checklist is clear
- `/claudia-progress` — where the workflow stands / suggested next step (read-only)
- `/claudia-settings` — view or edit `.planning/config.json`

Every `/claudia-*` command is a thin entry point in [plugins/claudia/commands/](plugins/claudia/commands/) that points at the matching file in [plugins/claudia/workflows/](plugins/claudia/workflows/). The workflow file calls `claudia ...` (the `claudia-tools` CLI) for every deterministic operation; the orchestrating model never hand-edits `.planning/` files.

Workflow agents: `researcher`, `planner`, `executor`, `verifier`.
Review agents (pair with `code-reviewer` for pipelines/outputs): `nextflow-reviewer`, `domain-reviewer`.

### GitHub commands

Require a GitHub MCP server (the official `github` plugin) and `GITHUB_PERSONAL_ACCESS_TOKEN` set in the environment.

- `/gh-issue [owner/repo:] <description>` — draft a structured GitHub issue and create it in the target repo, **only after the user confirms the draft**
- `/gh-my-issues [filters]` — list issues assigned to me, grouped by repo (read-only)
- `/gh-my-prs [filters]` — list PRs I authored, was review-requested on, or am assigned (read-only)
- `/gh-pr-draft [base:branch]` — draft a PR for the current branch in a fixed, human-readable structure and create it **only after the user accepts the draft**
- `/gh-pr-review <num|owner/repo#num|url>` — structured PR review classified URGENT/HIGH/MEDIUM/LOW, confidence-gated, **never posts to GitHub** (delegates to the `pr-reviewer` subagent)

## Development Notes

- Primary language: **Python** — all rules, prompts, and examples should assume Python unless stated otherwise
- Rules format: one convention per file, with a clear title, explanation, and code example
- Command format: Markdown with a `description` frontmatter field and `$ARGUMENTS` placeholder

## Editing Guidelines

Follow these formats when adding or editing files:

- **Agents** ([plugins/claudia/agents/](plugins/claudia/agents/)): YAML frontmatter with `name`, `description`, `model`; add `tools` only to restrict access — omit it when the agent needs MCP tools
- **Commands** ([plugins/claudia/commands/](plugins/claudia/commands/)): YAML frontmatter with `description`; prompt body with `$ARGUMENTS` for user input
- **Skills** ([plugins/claudia/skills/](plugins/claudia/skills/)): one folder per skill containing `SKILL.md`; frontmatter with `name` and `description`
- **Rules** ([plugins/claudia/rules/](plugins/claudia/rules/)): focused on a single convention; use a short title, one-paragraph explanation, and a code example. Add new rule files to the `@`-imports block above so they become always-on.
- **Plugin manifest** ([plugins/claudia/.claude-plugin/plugin.json](plugins/claudia/.claude-plugin/plugin.json)): single source of truth for plugin metadata

File naming: lowercase with hyphens (e.g. `code-review.md`, `pr-review.md`, `docstrings.md`)

## What NOT to do

- Do not create deeply nested folder structures
- Do not generate placeholder files — only create files with real content
- Do not rewrite existing files unless explicitly asked
