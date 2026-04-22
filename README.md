# claude-setup

> Collection of Claude Code configurations, agents, and commands — focused on Python development, powered by Claude Code in VS Code.

---

## What this is

This repo is my personal toolkit for working with **Claude Code** in VS Code. It's a place to collect and refine:

- **Instructions** (`CLAUDE.md`) that tell Claude Code how I like to work
- **Agents** for complex multi-step workflows
- **Commands** (slash commands) for quick recurring tasks
- **Rules** for consistent Python code style and conventions
- **MCP servers** as things grow

---

## Folder structure

```
claude-setup/
├── CLAUDE.md                        # Global Claude Code instructions (auto-loaded per project)
├── .claude/
│   ├── agents/                      # Subagent definitions
│   └── commands/                    # Slash command definitions
├── docs/
├── rules/                           # Reusable coding rules and conventions (planned)
├── mcp-servers/                     # Custom MCP servers (planned)
└── README.md                        # This file
```

### Folder descriptions

| Folder / File | Purpose | Status |
|---|---|---|
| `CLAUDE.md` | Main file Claude Code reads to understand how to behave in a project | ✅ Active |
| `.claude/agents/` | Subagent configurations (`code-reviewer`, `doc-updater`) — autonomous specialists for complex workflows | ✅ Active |
| `.claude/commands/` | Slash commands (`/python-review`, `/pr-review`, `/prepare-docstrings`, `/nextflow-review`, `/pytest-gen`, `/update-docs`) | ✅ Active |
| `docs/` | Single consolidated architecture index (`docs/INDEX.md`) — components, data flow, phases | ✅ Active |
| `rules/` | Short Markdown files with coding conventions (Python type hints, imports, formatting) | 📋 Planned |
| `mcp-servers/` | Custom Model Context Protocol servers to extend Claude Code's capabilities | 📋 Planned |

---

## Deployment

To use this setup in any project, symlink `CLAUDE.md` into the project root:

```bash
ln -s /path/to/claude-setup/CLAUDE.md CLAUDE.md
```

Claude Code auto-loads `CLAUDE.md` from the project root. Agents and commands in `.claude/` live in this repo and can be invoked directly from any Claude Code session pointed at this directory.

---

## Available agents

| Agent | Model | Invocation | Purpose |
|---|---|---|---|
| `code-reviewer` | Claude Sonnet 4.6 | subagent | Security, correctness, and quality review |
| `doc-updater` | Claude Haiku 4.5 | subagent via `/update-docs` | README, docs/INDEX.md, and CLAUDE.md updates |

---

## Available commands

| Command | Purpose |
|---|---|
| `/python-review <path>` | Comprehensive Python code review with static analysis |
| `/pr-review <PR#\|URL\|branch>` | GitHub PR analysis and review |
| `/prepare-docstrings <file>` | Add/rewrite docstrings in NumPy/SciPy format |
| `/nextflow-review <path>` | Nextflow DSL pipeline review |
| `/pytest-gen <path>` | Generate pytest unit and integration tests |
| `/update-docs` | Update all project documentation |

---

## Documentation

Architectural documentation lives in a single file: **[docs/INDEX.md](docs/INDEX.md)**.

It covers repository structure, all components (instructions, agents, commands), data flows, external dependencies, and development phases.
