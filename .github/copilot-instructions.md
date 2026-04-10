# Copilot Instructions

This file provides guidance to GitHub Copilot when working with files in this repository.

## Project Overview

This is a **GitHub Copilot setup repo** — a personal collection of instructions, rules, prompts, commands, and MCP configurations focused on Python development. It provides reusable Copilot configurations that can be symlinked or copied into any project.

## Architecture

The project is organized into several core components:

- **`.github/`** — `copilot-instructions.md` read automatically by Copilot in every project that includes it
- **`rules/`** — Always-follow coding conventions (type hints, docstrings, formatting, imports)
- **`prompts/`** — Reusable prompt templates for recurring tasks (write tests, write docstring, refactor)
- **`commands/`** — Slash command definitions invoked by users (`/review`, `/test`, `/docstring`, `/refactor`)
- **`mcp-servers/`** — MCP server configurations for extending Copilot's context *(future)*
- **`agents/`** — Agent configurations for multi-step automated workflows *(future)*

## Key Commands

- `/code-review` — Code quality review
- `/pr-review` — Generate tests for a function or module
- `/docstring` — Write or improve a docstring
- `/refactor` — Suggest refactoring improvements

## Development Notes

- Primary language: **Python** — all rules, prompts, and examples should assume Python unless stated otherwise
- Rules format: one convention per file, with a clear title, explanation, and code example.
- Skill format: Markdown with clear sections for when to use, how it works, examples

## Editing Guidelines

Follow these formats when adding or editing files:

- **Rules**: focused on a single convention; use a short title, one-paragraph explanation, and a code example
- **Prompts**: include a clear task description and any constraints (e.g. "use `pytest`", "add type hints")
- **Commands**: include a `description` line at the top and a short usage example
- **MCP servers**: one folder per server, with a `README.md` explaining what it does and how to configure it

File naming: lowercase with hyphens (e.g. `code-review.md`, `pr-review.md`, `docstring.md`)

## What NOT to do

- Do not create deeply nested folder structures
- Do not generate placeholder files — only create files with real content
- Do not rewrite existing files unless explicitly asked