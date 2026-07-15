# claudia (plugin)

A minimal Claude Code plugin: six skills and one agent for Python and
Nextflow development. No commands, no dispatcher, no Python tooling —
every capability is a Markdown skill or agent file that Claude Code
discovers and triggers on its own.

## Prerequisites

- Claude Code with this plugin enabled — skills and the agent are
  auto-discovered from `skills/` and `agents/`.
- For `pr-review`: the [`gh` CLI](https://cli.github.com/), authenticated:
  ```bash
  gh auth login
  gh auth status
  ```

## How this differs from earlier versions

There is no `/claudia` command, no `.planning/` workflow, no
`understand`/`plan`/`execute`/`close` phases, and no Python script.
Every skill fires either automatically (Claude Code matches its
`description` against the conversation) or because you named it
directly in your request — there is no explicit-verb router anymore.

## Skills (`skills/`)

| Skill | Triggers | What it does |
|---|---|---|
| `add-type-hints` | Auto (context) or "add type hints to this file" | Infers and adds Python type annotations; asks before guessing on low-confidence slots. |
| `prepare-docstrings` | Auto (context) or "document this file" | Adds/rewrites NumPy/SciPy-format docstrings. |
| `python-testing` | Auto (context) — "write tests", "add coverage" | pytest TDD guidance: fixtures, parametrization, mocking, coverage targets. |
| `nextflow-testing` | Auto (context) — writing/reviewing `.nf` tests | nf-test patterns: snapshot testing, process/workflow/function tests, config. |
| `pr-review` | "review PR 123", "check this pull request" | Local-only structured review of someone else's GitHub PR via the `pr-reviewer` agent. **Never posts to GitHub.** |
| `rules` | "show me the claudia rules", "set up rules" | Prints the rule files under `rules/` as a pasteable `@`-imports block. **Read-only — never edits any file.** |

## Agents (`agents/`)

| Agent | Called by | Role |
|---|---|---|
| `pr-reviewer` | `pr-review` skill | Confidence-gated PR review, classified URGENT/HIGH/MEDIUM/LOW. Read-only `gh` commands only; never posts, comments, approves, or merges. |

This is the only agent in the plugin.

## Rules (`rules/`)

`common/` and `python/` rule files — coding style, patterns, security,
testing, commit style, code review, and the review-gate principle.
**Not auto-loaded.** They only reach a project's `CLAUDE.md` if you ask
the `rules` skill to show them and paste the result in yourself. The
skill will never write to `CLAUDE.md` on its own.

To add a new rule, drop a `.md` file under the right subdirectory —
the `rules` skill picks it up automatically the next time it runs.

## Install

Add this repo as a Claude Code marketplace and enable the `claudia`
plugin. There is no bootstrap step — the skills are available
immediately; just work normally and they'll fire when relevant, or ask
for one by name (e.g. "add type hints to `foo.py`", "review PR 42").
