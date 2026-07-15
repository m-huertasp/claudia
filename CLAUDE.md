# Claude Code Instructions

This file provides guidance to Claude Code when working with files in this repository.

## Project Overview

This is **claudia** — a minimal, personal Claude Code plugin bundling six
skills for Python and Nextflow development, plus one agent. There is no
dispatcher command, no workflow engine, and no Python tooling. Everything
is a Markdown skill or agent file, discovered and triggered by Claude Code
directly.

> **This is a trimmed-down v3.** Earlier versions of this repo shipped a
> `/claudia` dispatcher command, a stdlib Python helper script
> (`scripts/claudia`), a `.planning/` workflow (understand → plan →
> execute → close), and a larger agent set (planner, executor, verifier,
> researcher, code-reviewer, nextflow-reviewer, domain-reviewer,
> code-explorer). All of that has been removed. If you're looking for any
> of it, it isn't coming back — the plugin is intentionally scoped down to
> the six skills and one agent listed below.

## Architecture

- **`claudia/`** — the Claude Code plugin. See [claudia/README.md](claudia/README.md).
  - **`claudia/skills/`** — the six skills, one folder each, containing a `SKILL.md`.
  - **`claudia/agents/`** — exactly one agent: `pr-reviewer.md`.
  - **`claudia/rules/`** — reference rule files (`common/`, `python/`), surfaced via the `rules` skill. Not auto-loaded into any project's `CLAUDE.md` automatically — the skill only prints them.
  - No `claudia/commands/`, no `claudia/scripts/`. Nothing in this plugin runs a script.

## Always-on rules

The plugin's rule files are inlined here via `@`-imports so they apply to every skill and agent execution in *this* repo.

@claudia/rules/common/review-gate.md
@claudia/rules/common/code-review.md
@claudia/rules/common/coding-style.md
@claudia/rules/common/commit-style.md
@claudia/rules/common/patterns.md
@claudia/rules/common/security.md
@claudia/rules/common/testing.md
@claudia/rules/python/coding-style.md
@claudia/rules/python/fastapi.md
@claudia/rules/python/patterns.md
@claudia/rules/python/security.md
@claudia/rules/python/tests.md

(In a *consuming* project, use the `rules` skill to print the same
`@`-import block for you to paste into that project's own `CLAUDE.md` —
the skill never writes it for you.)

## Skills

Plugin skills are namespaced `claudia:<name>`. There are six, in three categories:

**Auto-triggered only** (knowledge skills, fire by description match):

- `claudia:python-testing` — pytest TDD guidance
- `claudia:nextflow-testing` — nf-test patterns

**Auto-triggered, read-only utilities** (no dedicated command, no writes):

- `claudia:pr-review` — reviews a GitHub PR locally via the `pr-reviewer` agent; never posts to GitHub
- `claudia:rules` — prints the `claudia/rules/` content as a pasteable `@`-imports block; never edits any file

**Dual-mode** (auto-triggered from context; also directly nameable):

- `claudia:add-type-hints` — infers and adds Python type annotations
- `claudia:prepare-docstrings` — adds/rewrites NumPy/SciPy-format docstrings

There is no `/claudia` command and no dispatcher skill. Every skill is
discovered and triggered on its own `description` frontmatter.

## Agents

- `pr-reviewer` — used by `claudia:pr-review`; confidence-gated PR review, read-only, never posts to GitHub.

That is the only agent in this plugin.

## Development Notes

- Primary language: **Python** — rules, prompts, and examples assume Python unless stated otherwise.
- Rules format: one convention per file, with a clear title, explanation, and code example.
- Skills format: one folder per skill containing `SKILL.md` with `name` + `description` frontmatter.

## Editing Guidelines

Follow these formats when adding or editing files:

- **Agents** ([claudia/agents/](claudia/agents/)): YAML frontmatter with `name`, `description`, `model`; add `tools` only to restrict access — omit it when the agent needs MCP tools.
- **Skills** ([claudia/skills/](claudia/skills/)): one folder per skill containing `SKILL.md`; frontmatter with `name` and `description`. Since there is no dispatcher, the `description` is the *only* trigger surface — write it so Claude Code can match real user phrasing.
- **Rules** ([claudia/rules/](claudia/rules/)): focused on a single convention; use a short title, one-paragraph explanation, and a code example. Add new rule files to the `@`-imports block above so they become always-on in *this* repo. The `rules` skill picks up new files under `common/`/`python/`/`nextflow/` automatically the next time it runs — no registry to update.
- **Plugin manifest** ([claudia/.claude-plugin/plugin.json](claudia/.claude-plugin/plugin.json)): single source of truth for plugin metadata.
- **Marketplace config** ([.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)): repo-root file that registers this repo as a marketplace. Points to `./claudia`. Do not move it inside a subdirectory.

File naming: lowercase with hyphens.

## What NOT to do

- Do not add a dispatcher command or any `/claudia*` command. This plugin is command-free by design; skills trigger on their own descriptions.
- Do not add a Python script, CLI, or any executable tooling. That's the whole point of this trim — everything here is a Markdown skill/agent file.
- Do not add back `.planning/`, `config.json`, or any cross-session state file. Nothing in this plugin reads or writes project state.
- Do not make the `rules` skill write to any file. It is read-only by explicit design — see [claudia/rules/common/review-gate.md](claudia/rules/common/review-gate.md).
- Do not create deeply nested folder structures.
- Do not generate placeholder files — only create files with real content.
