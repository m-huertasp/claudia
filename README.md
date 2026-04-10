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
│   └── copilot-instructions.md   # Global Copilot instructions
├── rules/                        # Reusable coding rules and conventions
├── prompts/                      # Reusable prompt templates for common tasks
├── commands/                     # Slash command definitions
├── mcp-servers/                  # Custom MCP servers
└── agents/                       # Agent configurations
```

### Folder descriptions

| Folder | Purpose |
|---|---|
| `.github/` | Contains `copilot-instructions.md` — the main file Copilot reads to understand how to behave in a project |
| `rules/` | Short Markdown files with coding conventions (e.g. "always use type hints", "prefer `pathlib` over `os.path`") |
| `prompts/` | Reusable prompt templates for recurring tasks like writing tests, docstrings, or refactoring |
| `commands/` | Slash command definitions (`/review`, `/test`, etc.) for quick in-editor workflows |
| `mcp-servers/` | Custom Model Context Protocol servers that extend Copilot's capabilities *(future)* |
| `agents/` | Agent configurations for multi-step automated workflows *(future)* |

---

## Reuse in other projects

### Option 1 — Manual symlink

```bash
# From the root of your project
ln -s /path/to/copilot-setup/.github/copilot-instructions.md .github/copilot-instructions.md
```

This keeps the instructions in sync: any edit in this repo is reflected immediately in all projects that symlink to it.

---

## Roadmap

### Phase 1 — Basics *(current)*
- [ ] `copilot-instructions.md` — initial Python-focused instructions
- [ ] First rules: type hints, docstrings, formatting conventions
- [ ] First prompts: write tests, write docstring, explain code

### Phase 2 — Commands and workflows
- [ ] Slash commands: `/review`, `/test`, `/docstring`, `/refactor`
- [ ] Workflow prompts: PR description, commit message, code review checklist

### Phase 3 — MCP servers and agents
- [ ] First custom MCP server (e.g. project-local context lookup)
- [ ] Agent definitions for common multi-step tasks
- [ ] Per-language rule sets (beyond Python)

