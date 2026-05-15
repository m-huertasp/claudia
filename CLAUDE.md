# Claude Code Instructions

This file provides guidance to Claude Code when working with files in this repository.

## Project Overview

This is a **Claude Code setup repo** — a personal collection of instructions, agents, commands, and MCP configurations focused on Python development. It provides reusable Claude Code configurations that can be symlinked or copied into any project.

## Architecture

The project is organized into several core components:

- **`CLAUDE.md`** — this file; read automatically by Claude Code in every project that includes it
- **`.claude/agents/`** — subagent definitions (`code-explorer`, `code-reviewer`) for multi-step automated workflows
- **`.claude/rules/`** — always-follow coding conventions, split into `common/` and `python/`
- **`.claude/skills/`** — skills that guide Claude through specific tasks (testing, docstrings, language patterns)
- **`plugins/`** — bundled Claude Code plugins; each ships its own commands, agents, and MCP config

## Skills

Invokable as `/<skill-name>`, or triggered automatically when relevant:

- `prepare-docstrings` — write or homogenize docstrings (NumPy/SciPy format)
- `add-type-hints` — infer and add type annotations to every function, asking when a type is uncertain
- `python-testing` — write pytest tests using TDD
- `python-patterns` — non-obvious Python patterns (typed decorators, immutability, exception chaining)
- `nextflow-patterns` — production-ready Nextflow DSL2 habits
- `nextflow-testing` — Nextflow pipeline testing with nf-test

## Key Commands

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
