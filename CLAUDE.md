# Claude Code Instructions

This file provides guidance to Claude Code when working with files in this repository.

## Project Overview

This is a **Claude Code setup repo** — a personal collection of instructions, agents, commands, and MCP configurations focused on Python development. It provides reusable Claude Code configurations that can be symlinked or copied into any project.

## Architecture

The project is organized into several core components:

- **`CLAUDE.md`** — this file; read automatically by Claude Code in every project that includes it
- **`.claude/agents/`** — subagent definitions (`code-reviewer`, `doc-updater`) for multi-step automated workflows
- **`.claude/commands/`** — slash command definitions invoked as `/command-name` in Claude Code chat
- **`rules/`** — always-follow coding conventions (type hints, docstrings, formatting, imports) *(planned)*
- **`mcp-servers/`** — MCP server configurations for extending Claude Code's context *(planned)*

## Key Commands

- `/python-review` — comprehensive Python code quality review
- `/pr-review` — pull request analysis and review
- `/prepare-docstrings` — write or improve docstrings (NumPy/SciPy format)
- `/nextflow-review` — Nextflow DSL pipeline review
- `/pytest-gen` — generate pytest unit and integration tests
- `/update-docs` — update all project documentation

## Development Notes

- Primary language: **Python** — all rules, prompts, and examples should assume Python unless stated otherwise
- Rules format: one convention per file, with a clear title, explanation, and code example
- Command format: Markdown with a `description` frontmatter field and `$ARGUMENTS` placeholder

## Editing Guidelines

Follow these formats when adding or editing files:

- **Agents** (`.claude/agents/`): YAML frontmatter with `name`, `description`, `model`, `tools`; agent system prompt in the body
- **Commands** (`.claude/commands/`): YAML frontmatter with `description`; prompt body with `$ARGUMENTS` for user input
- **Rules**: focused on a single convention; use a short title, one-paragraph explanation, and a code example
- **MCP servers**: one folder per server, with a `README.md` explaining what it does and how to configure it

File naming: lowercase with hyphens (e.g. `code-review.md`, `pr-review.md`, `docstrings.md`)

## What NOT to do

- Do not create deeply nested folder structures
- Do not generate placeholder files — only create files with real content
- Do not rewrite existing files unless explicitly asked
