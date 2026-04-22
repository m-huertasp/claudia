# copilot-setup — Architecture Index

**Last Updated:** April 22, 2026

## Overview

Personal toolkit for **GitHub Copilot (Claude)** in VS Code. Provides reusable instructions, agents, and prompt templates focused on Python development. Designed to be symlinked or copied into any project.

---

## Repository Structure

```
copilot-setup/
├── .github/
│   ├── copilot-instructions.md      # Global Copilot instructions (auto-loaded per project)
│   └── agents/                      # Agent configurations
│       ├── code-reviewer.agent.md   # Code review specialist
│       └── doc-updater.agent.md     # Documentation specialist
├── docs/
│   └── INDEX.md                     # This file — architecture overview
├── prompts/                         # Reusable prompt templates
│   ├── python-review.prompt.md      # Python code review
│   ├── pr-review.prompt.md          # Pull request analysis
│   ├── prepare-docstrings.prompt.md # Docstring generation
│   └── nextflow-review.prompt.md    # Nextflow DSL review
└── README.md                        # User-facing documentation
```

---

## Components

### Instructions — `.github/copilot-instructions.md`

Auto-loaded by Copilot in any project that includes this file (directly or via symlink). Sets global behavior: project overview, architecture description, key commands, editing conventions, and what not to do.

**Deployment:**
```bash
# Symlink into a target project (recommended)
ln -s /path/to/copilot-setup/.github/copilot-instructions.md \
      .github/copilot-instructions.md
```

---

### Agents — `.github/agents/`

Stateless autonomous specialists. Invoked with `@agent-name` in Copilot chat.

| Agent | File | Model | Purpose |
|-------|------|-------|---------|
| **code-reviewer** | `code-reviewer.agent.md` | Claude Sonnet 4.6 | Security, correctness, and quality review |
| **doc-updater** | `doc-updater.agent.md` | Claude Haiku 4.5 | README, docs/INDEX.md, and copilot-instructions.md updates |

**code-reviewer** workflow:
1. Determine target (file, PR, git diff, or recent commit)
2. Read target file in full; follow local imports one level deep
3. Apply checklist: CRITICAL → HIGH → MEDIUM → LOW
4. Report findings with >80% confidence threshold
5. Emit verdict: Approve / Warning / Block

**doc-updater** workflow:
1. Analyze repository structure and entry points
2. Update `README.md` (required sections + verified run instructions)
3. Update `docs/INDEX.md` (this file — single consolidated architecture doc)
4. Validate and update any other files in `docs/`
5. Update `.github/copilot-instructions.md` if present

---

### Prompts — `prompts/`

Reusable prompt templates. Each pairs with an agent and defines a multi-phase workflow.

| Prompt | Agent | Invocation | Purpose |
|--------|-------|-----------|---------|
| `python-review.prompt.md` | code-reviewer | `@code-reviewer /python-review <path>` | Full Python review (PARSE → LINT → SECURITY → CORRECTNESS) |
| `pr-review.prompt.md` | code-reviewer | `@code-reviewer /pr-review` | PR analysis and test generation |
| `prepare-docstrings.prompt.md` | code-reviewer | `@code-reviewer /docstring <file>` | Docstring generation or improvement |
| `nextflow-review.prompt.md` | code-reviewer | `@code-reviewer /nextflow-review <file>` | Nextflow DSL syntax and best practices review |

---

## Data Flow

### Code Review

```
User: @code-reviewer /python-review src/
  → code-reviewer loads copilot-instructions.md
  → python-review.prompt.md defines phases
  → Agent reads files, follows imports
  → Findings filtered by confidence (>80%)
  → Report saved as code-review_DDMMYY.md
```

### Documentation Update

```
User: @doc-updater
  → doc-updater analyzes repository structure
  → README.md updated (sections + run instructions verified)
  → docs/INDEX.md updated (this file)
  → docs/ files validated for accuracy and link integrity
  → .github/copilot-instructions.md updated if present
```

---

## External Dependencies

| Dependency | Purpose |
|------------|---------|
| GitHub Copilot (VS Code extension) | Chat interface and code generation |
| Claude Haiku 4.5 | doc-updater model backend |
| Claude Sonnet 4.6 | code-reviewer model backend |

No runtime dependencies — this is a configuration/template repository with no executable code.

---

## Development Phases

### ✅ Phase 1 — Basics
- Global Copilot instructions (`copilot-instructions.md`)
- Agents: `code-reviewer`, `doc-updater`
- Prompts: `python-review`, `pr-review`, `prepare-docstrings`, `nextflow-review`
- Architecture documentation (`docs/INDEX.md`)

### 🚧 Phase 2 — Commands and Workflows
- [ ] Slash commands: `/review`, `/test`, `/docstring`, `/refactor`
- [ ] Rules: type hints, docstring conventions, formatting guidelines
- [ ] Workflow prompts: commit message, changelog

### 📋 Phase 3 — Extended Capabilities
- [ ] Per-language rule sets (JavaScript, TypeScript, etc.)
- [ ] Custom MCP servers for project-local context
- [ ] Additional specialized agents
