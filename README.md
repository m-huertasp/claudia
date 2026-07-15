# claudia

> A minimal Claude Code plugin for Python and Nextflow work.

---

## What this is

**claudia** is a small plugin bundling six skills and one agent. No
commands, no dispatcher, no workflow engine, no Python tooling — every
capability is a Markdown skill or agent file that Claude Code discovers
and triggers on its own, either automatically from context or because
you named it directly.

It currently runs in Claude Code (VS Code or terminal).

---

## The plugin — `claudia/`

### Skills

| Skill | Triggers | What it does |
|---|---|---|
| `add-type-hints` | Auto (context) or explicit request | Infers and adds Python type annotations; asks before guessing on low-confidence slots. |
| `prepare-docstrings` | Auto (context) or explicit request | Adds/rewrites NumPy/SciPy-format docstrings. |
| `python-testing` | Auto (context) | pytest TDD guidance — fixtures, parametrization, mocking, coverage. |
| `nextflow-testing` | Auto (context) | nf-test patterns — snapshot testing, process/workflow/function tests. |
| `pr-review` | "review PR 123" | Local-only, read-only review of a GitHub PR. **Never posts to GitHub.** |
| `rules` | "show me the claudia rules" | Prints the bundled rule files as a pasteable `@`-imports block. **Read-only.** |

### Agent

| Agent | Used by | Role |
|---|---|---|
| `pr-reviewer` | `pr-review` skill | Confidence-gated PR review, classified URGENT/HIGH/MEDIUM/LOW. Read-only; never mutates GitHub state. |

That's the entire plugin surface — no other agents, no commands.

---

## Rules

Rule files live at [claudia/rules/](claudia/rules/) under `common/` and
`python/`. They are **not** auto-loaded into any project. The `rules`
skill only prints them as an `@`-imports block for you to paste into
your own project's `CLAUDE.md` — it never writes the file for you.

---

## Prerequisites

- Claude Code, with this plugin enabled.
- For `pr-review`: the [`gh` CLI](https://cli.github.com/), authenticated via `gh auth login`.

## Install

Add this repo as a Claude Code marketplace and enable the `claudia`
plugin. There's no bootstrap step — just work normally; the relevant
skills fire on their own, or ask for one by name.

---

## Folder structure

```
claudia/
├── CLAUDE.md                        # Project instructions; @-imports the rule files below
├── .claude-plugin/marketplace.json  # Registers this repo as a marketplace
├── claudia/                         # The plugin
│   ├── .claude-plugin/plugin.json
│   ├── agents/                      # pr-reviewer.md — the only agent
│   ├── skills/                      # add-type-hints, prepare-docstrings, python-testing,
│   │                                #   nextflow-testing, pr-review, rules
│   └── rules/                       # common/ + python/ reference rule files
└── README.md                        # You are here
```

---

## What this isn't

- It's not a general-purpose framework. It's tuned for Python and
  Nextflow work on small-to-medium repos.
- It's not a workflow system. There is no phased process, no state file,
  no dispatcher — just skills that fire when relevant.
- It doesn't write to your `CLAUDE.md`, or any file, unless the skill's
  explicit job is to edit source code (`add-type-hints`,
  `prepare-docstrings`) — and even then, only after resolving
  uncertainty with you first.
