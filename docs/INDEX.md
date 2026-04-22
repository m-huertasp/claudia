# claude-setup — Architecture Index

**Last Updated:** April 22, 2026

## Overview

Personal toolkit for **Claude Code** in VS Code. Provides reusable instructions, agents, and slash commands focused on Python development. Designed to be symlinked or copied into any project.

---

## Repository Structure

```
claude-setup/
├── CLAUDE.md                        # Global Claude Code instructions (auto-loaded per project)
├── .claude/
│   ├── agents/                      # Subagent definitions
│   │   ├── code-reviewer.md         # Code review specialist
│   │   └── doc-updater.md           # Documentation specialist
│   └── commands/                    # Slash command definitions
│       ├── python-review.md         # Python code review
│       ├── pr-review.md             # Pull request analysis
│       ├── prepare-docstrings.md    # Docstring generation
│       ├── nextflow-review.md       # Nextflow DSL review
│       ├── pytest-gen.md            # Pytest test generation
│       └── update-docs.md           # Documentation update
├── docs/
│   └── INDEX.md                     # This file — architecture overview
└── README.md                        # User-facing documentation
```

---

## Components

### Instructions — `CLAUDE.md`

Auto-loaded by Claude Code in any project that includes this file (directly or via symlink). Sets global behavior: project overview, architecture description, key commands, editing conventions, and what not to do.

**Deployment:**
```bash
# Symlink into a target project (recommended)
ln -s /path/to/claude-setup/CLAUDE.md CLAUDE.md
```

---

### Agents — `.claude/agents/`

Stateless autonomous specialists. Invoked as subagents within Claude Code.

| Agent | File | Model | Purpose |
|-------|------|-------|---------|
| **code-reviewer** | `code-reviewer.md` | Claude Sonnet 4.6 | Security, correctness, and quality review |
| **doc-updater** | `doc-updater.md` | Claude Haiku 4.5 | README, docs/INDEX.md, and CLAUDE.md updates |

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
5. Update `CLAUDE.md` if present

---

### Commands — `.claude/commands/`

Slash commands invoked as `/command-name` in Claude Code chat. Each defines a multi-phase workflow.

| Command | File | Purpose |
|---------|------|---------|
| `/python-review <path>` | `python-review.md` | Full Python review (PARSE → LINT → SECURITY → CORRECTNESS) |
| `/pr-review <PR#\|URL>` | `pr-review.md` | PR analysis and review |
| `/prepare-docstrings <file>` | `prepare-docstrings.md` | NumPy/SciPy docstring generation or improvement |
| `/nextflow-review <path>` | `nextflow-review.md` | Nextflow DSL syntax and best practices review |
| `/pytest-gen <path>` | `pytest-gen.md` | Interactive pytest unit/integration test generation |
| `/update-docs` | `update-docs.md` | Update all project documentation via doc-updater |

---

## Data Flow

### Code Review

```
User: /python-review src/
  → Claude Code loads CLAUDE.md
  → python-review.md defines phases
  → Claude reads files, follows imports
  → Findings filtered by confidence (>80%)
  → Report saved as .github/py-src-review.md
```

### Documentation Update

```
User: /update-docs
  → doc-updater subagent analyzes repository structure
  → README.md updated (sections + run instructions verified)
  → docs/INDEX.md updated (this file)
  → docs/ files validated for accuracy and link integrity
  → CLAUDE.md updated if present
```

---

## External Dependencies

| Dependency | Purpose |
|------------|---------|
| Claude Code (VS Code extension) | Chat interface and code generation |
| Claude Haiku 4.5 | doc-updater model backend |
| Claude Sonnet 4.6 | code-reviewer model backend |

No runtime dependencies — this is a configuration/template repository with no executable code.

---

## Development Phases

### ✅ Phase 1 — Basics
- Global Claude Code instructions (`CLAUDE.md`)
- Agents: `code-reviewer`, `doc-updater`
- Commands: `python-review`, `pr-review`, `prepare-docstrings`, `nextflow-review`, `pytest-gen`, `update-docs`
- Architecture documentation (`docs/INDEX.md`)

### 🚧 Phase 2 — Rules and Workflows
- [ ] Rules: type hints, docstring conventions, formatting guidelines
- [ ] Workflow commands: commit message, changelog

### 📋 Phase 3 — Extended Capabilities
- [ ] Per-language rule sets (JavaScript, TypeScript, etc.)
- [ ] Custom MCP servers for project-local context
- [ ] Additional specialized agents
