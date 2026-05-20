# Claude Code Instructions

This file provides guidance to Claude Code when working with files in this repository.

## Project Overview

This is **claudia** — a personal Claude Code framework for Python and Nextflow development. It provides a phased, control-first development workflow plus reusable instructions, agents, rules, and skills that can be symlinked or copied into any project.

The framework is **control-first**: every direction-locking artifact and every outward action passes through a review gate ([.claude/rules/common/review-gate.md](.claude/rules/common/review-gate.md)) before it is accepted. It is also **model-agnostic and safe to share** — see [.claude/rules/common/secure-ai-use.md](.claude/rules/common/secure-ai-use.md).

## Architecture

The project is organized into several core components:

- **`CLAUDE.md`** — this file; read automatically by Claude Code in every project that includes it
- **`.claude/agents/`** — subagent definitions (`code-explorer`, `code-reviewer`, `nextflow-reviewer`, `domain-reviewer`)
- **`.claude/rules/`** — always-follow conventions, split into `common/` and `python/`; `common/` includes the framework's `review-gate.md` and `secure-ai-use.md`
- **`.claude/skills/`** — skills that guide Claude through specific tasks (testing, docstrings, language patterns, authoring new skills)
- **`claudia_tools/`** — Python package exposing the `claudia` CLI: the deterministic engine the workflow calls for every state/config/phase/template/gate/detect/env/verify operation. Install with `uv tool install ./claudia_tools`.
- **`plugins/`** — bundled Claude Code plugins: `claudia-workflow` (thin commands + a `workflows/` orchestration layer that invokes `claudia ...`) and `gh-workflow` (GitHub commands)

## Skills

Invokable as `/<skill-name>`, or triggered automatically when relevant:

- `prepare-docstrings` — write or homogenize docstrings (NumPy/SciPy format)
- `add-type-hints` — infer and add type annotations to every function, asking when a type is uncertain
- `python-testing` — write pytest tests using TDD
- `python-patterns` — non-obvious Python patterns (typed decorators, immutability, exception chaining)
- `nextflow-patterns` — production-ready Nextflow DSL2 habits
- `nextflow-testing` — Nextflow pipeline testing with nf-test
- `claudia-new-skill` — author a new skill following repo conventions (the framework's extensibility path)

## Key Commands

### Development workflow — `claudia-workflow` plugin (`plugins/claudia-workflow/`)

A phased, control-first workflow. Each command is invoked explicitly; state persists in `.planning/`. See `plugins/claudia-workflow/README.md`.

- `/claudia-map` — analyze an existing codebase → `.planning/CONTEXT.md`
- `/claudia-new` — start a project, build the roadmap → `PROJECT.md`, `ROADMAP.md`, `ENVIRONMENT.md`, `config.json`
- `/claudia-discuss` — pin down design decisions before planning → `DECISIONS.md`
- `/claudia-plan` — research + ordered task breakdown → `STATE.md`
- `/claudia-execute` — implement tasks via executor subagents (sequential by default)
- `/claudia-verify` — two-stage review + secret scan; for pipelines, generates a human checklist in `VERIFICATION.md`
- `/claudia-ship` — open a PR via `/gh-pr-draft`; blocked by `claudia verify ready` until the checklist is clear
- `/claudia-progress` — where the workflow stands / suggested next step (read-only)
- `/claudia-settings` — view or edit `.planning/config.json`

Every command is a thin entry point in `plugins/claudia-workflow/commands/`
that points at the matching file in `plugins/claudia-workflow/workflows/`.
The workflow file calls `claudia ...` (the `claudia-tools` CLI) for every
deterministic operation; the orchestrating model never hand-edits
`.planning/` files.

Workflow agents: `researcher`, `planner`, `executor`, `verifier`.
Review agents (pair with `code-reviewer` for pipelines/outputs):
`nextflow-reviewer`, `domain-reviewer`.

### GitHub workflow — `gh-workflow` plugin (`plugins/gh-workflow/`)

Requires a GitHub MCP server (the official `github` plugin) and `GITHUB_PERSONAL_ACCESS_TOKEN` set in the environment. See `plugins/gh-workflow/README.md`.

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

- **Agents** (`.claude/agents/` or a plugin's `agents/`): YAML frontmatter with `name`, `description`, `model`; add `tools` only to restrict access — omit it when the agent needs MCP tools
- **Commands** (a plugin's `commands/`): YAML frontmatter with `description`; prompt body with `$ARGUMENTS` for user input
- **Rules**: focused on a single convention; use a short title, one-paragraph explanation, and a code example
- **Plugins** (`plugins/<name>/`): `.claude-plugin/plugin.json` manifest, plus `commands/`, `agents/`, and a `README.md` covering prerequisites and setup

File naming: lowercase with hyphens (e.g. `code-review.md`, `pr-review.md`, `docstrings.md`)

## What NOT to do

- Do not create deeply nested folder structures
- Do not generate placeholder files — only create files with real content
- Do not rewrite existing files unless explicitly asked
