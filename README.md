# copilot-setup

> Collection of GitHub Copilot configurations, rules, prompts, and commands — focused on Python development, powered by Claude through GitHub Copilot in VS Code.

---

## What this is

This repo is my personal toolkit for working with **GitHub Copilot (Claude)** in VS Code. It's a place to collect and refine:

- **Instructions** that tell Copilot how I like to work
- **Rules** for consistent Python code style and conventions
- **Prompts** for common tasks I do repeatedly
- **Commands** (slash commands) for quick workflows
- **MCP servers** and **agents** as things grow

---

## Folder structure

```
copilot-setup/
├── .github/
│   ├── copilot-instructions.md      # Global Copilot instructions
│   └── agents/                      # Agent configurations
├── docs/
├── prompts/                         # Reusable prompt templates for common tasks
├── rules/                           # Reusable coding rules and conventions (planned)
├── commands/                        # Slash command definitions (planned)
├── mcp-servers/                     # Custom MCP servers (planned)
└── README.md                        # This file
```

### Folder descriptions

| Folder | Purpose | Status |
|---|---|---|
| `.github/` | Contains `copilot-instructions.md` — the main file Copilot reads to understand how to behave in a project | ✅ Active |
| `.github/agents/` | Agent configurations (`code-reviewer`, `doc-updater`) — autonomous specialists for complex workflows | ✅ Active |
| `docs/` | Single consolidated architecture index (`docs/INDEX.md`) — components, data flow, phases | ✅ Active |
| `prompts/` | Reusable prompt templates for recurring tasks (Python review, PR review, docstrings, Nextflow review, update-docs) | ✅ Active |
| `rules/` | Short Markdown files with coding conventions (Python type hints, imports, formatting) | 📋 Planned |
| `commands/` | Slash command definitions (`/review`, `/test`, `/docstring`, `/refactor`) | 📋 Planned |
| `mcp-servers/` | Custom Model Context Protocol servers to extend Copilot's capabilities | 📋 Planned |

---

## Documentation

Architectural documentation lives in a single file: **[docs/INDEX.md](docs/INDEX.md)**.

It covers repository structure, all components (instructions, agents, prompts), data flows, external dependencies, and development phases.


