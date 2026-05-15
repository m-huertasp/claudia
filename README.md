# claude-setup

> Collection of Claude Code configurations, agents, skills, and plugins.

---

## What this is

This repo is my personal toolkit for working with **Claude Code** in VS Code. It's a place to collect and refine:

- **Instructions** (`CLAUDE.md`) that tell Claude Code how I like to work
- **Agents** for complex multi-step workflows
- **Rules** for consistent code style and conventions
- **Skills** (slash commands) for recurring tasks
- **Plugins** that bundle related commands and agents

---

## Folder structure

```
claude-setup/
├── CLAUDE.md                        # Global Claude Code instructions (auto-loaded per project)
├── .claude/
│   ├── agents/                      # Subagent definitions
│   ├── rules/                       # Coding conventions (common/ and python/)
│   └── skills/                      # Skill definitions (invokable as slash commands)
├── plugins/
│   └── gh-workflow/                 # GitHub workflow plugin
├── docs/
└── README.md                        # This file
```

### Folder descriptions

| Folder / File | Purpose |
|---|---|
| `CLAUDE.md` | Main file Claude Code reads to understand how to behave in a project |
| `.claude/agents/` | Subagent configurations (`code-explorer`, `code-reviewer`) |
| `.claude/rules/` | Short Markdown files with coding conventions, split into `common/` and `python/` |
| `.claude/skills/` | Skills invokable as `/<skill-name>` in Claude Code chat |
| `plugins/gh-workflow/` | GitHub workflow plugin — issues, PRs, and review |
| `docs/` | Single consolidated architecture index (`docs/INDEX.md`) |

---

## Available agents

| Agent | Model | Purpose |
|---|---|---|
| `code-explorer` | Claude Sonnet 4.6 | Deep codebase exploration — traces execution paths, maps architecture |
| `code-reviewer` | Claude Sonnet 4.6 | Security, correctness, and quality review |

---

## Available skills

Invokable as `/<skill-name>` in Claude Code chat.

| Skill | Purpose |
|---|---|
| `/prepare-docstrings <file>` | Add or rewrite docstrings in NumPy/SciPy format |
| `/add-type-hints <file>` | Infer and add type annotations; asks when uncertain |
| `/python-testing <path>` | Write pytest tests using TDD |
| `/python-patterns` | Non-obvious Python patterns (typed decorators, immutability, exception chaining) |
| `/nextflow-patterns` | Production-ready Nextflow DSL2 habits |
| `/nextflow-testing` | Nextflow pipeline testing with nf-test |

---

## Plugins

### `gh-workflow` — `plugins/gh-workflow/`

GitHub workflow automation. Requires the official `github` MCP plugin and `GITHUB_PERSONAL_ACCESS_TOKEN` set in the environment. See [plugins/gh-workflow/README.md](plugins/gh-workflow/README.md) for setup.

| Command | Purpose |
|---|---|
| `/gh-issue [owner/repo:] <description>` | Draft and create a structured GitHub issue (confirmation-gated) |
| `/gh-my-issues [filters]` | List issues assigned to me, grouped by repo |
| `/gh-my-prs [filters]` | List PRs I authored, was review-requested on, or am assigned |
| `/gh-pr-draft [base:branch]` | Draft and create a PR in a fixed human-readable structure (accept/refuse gate) |
| `/gh-pr-review <num\|url>` | Structured PR review (URGENT/HIGH/MEDIUM/LOW) — never posts to GitHub |

---

## Documentation

Architectural documentation lives in a single file: **[docs/INDEX.md](docs/INDEX.md)**.
