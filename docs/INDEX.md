# claude-setup — Architecture Index

**Last Updated:** May 15, 2026

## Overview

Personal toolkit for **Claude Code** in VS Code. Provides reusable instructions, agents, rules, skills, and plugins focused on Python development. Designed to be symlinked or copied into any project.

---

## Repository Structure

```
claude-setup/
├── CLAUDE.md                        # Global Claude Code instructions (auto-loaded per project)
├── .claude/
│   ├── agents/                      # Subagent definitions
│   │   ├── code-explorer.md         # Codebase exploration specialist
│   │   └── code-reviewer.md         # Code review specialist
│   ├── rules/                       # Coding conventions
│   │   ├── common/                  # Language-agnostic rules
│   │   │   ├── code-review.md
│   │   │   ├── coding-style.md
│   │   │   ├── patterns.md
│   │   │   ├── security.md
│   │   │   └── testing.md
│   │   └── python/                  # Python-specific rules
│   │       ├── coding-style.md
│   │       ├── fastapi.md
│   │       ├── patterns.md
│   │       ├── security.md
│   │       └── tests.md
│   └── skills/                      # Skill definitions
│       ├── add-type-hints/
│       ├── nextflow-patterns/
│       ├── nextflow-testing/
│       ├── prepare-docstrings/
│       ├── python-patterns/
│       └── python-testing/
├── plugins/
│   └── gh-workflow/                 # GitHub workflow plugin
│       ├── .claude-plugin/
│       │   └── plugin.json          # Plugin manifest
│       ├── agents/
│       │   └── pr-reviewer.md       # PR review specialist
│       ├── commands/                # Plugin slash commands
│       │   ├── gh-issue.md
│       │   ├── gh-my-issues.md
│       │   ├── gh-my-prs.md
│       │   ├── gh-pr-draft.md
│       │   └── gh-pr-review.md
│       └── README.md
├── docs/
│   └── INDEX.md                     # This file — architecture overview
└── README.md                        # User-facing documentation
```

---

## Components

### Instructions — `CLAUDE.md`

Auto-loaded by Claude Code in any project that includes this file (directly or via symlink). Sets global behavior: project overview, architecture description, available skills, editing conventions, and what not to do.

**Deployment:**
```bash
ln -s /path/to/claude-setup/CLAUDE.md CLAUDE.md
```

---

### Agents — `.claude/agents/`

Stateless autonomous specialists. Invoked as subagents within Claude Code.

| Agent | File | Model | Purpose |
|-------|------|-------|---------|
| **code-explorer** | `code-explorer.md` | Claude Sonnet 4.6 | Deep codebase exploration — traces execution paths, maps architecture layers, documents dependencies |
| **code-reviewer** | `code-reviewer.md` | Claude Sonnet 4.6 | Security, correctness, and quality review |

**code-reviewer** workflow:
1. Determine target (file, PR, git diff, or recent commit)
2. Read target file in full; follow local imports one level deep
3. Apply checklist: CRITICAL → HIGH → MEDIUM → LOW
4. Report findings with >80% confidence threshold
5. Emit verdict: Approve / Warning / Block

---

### Rules — `.claude/rules/`

Always-loaded coding conventions, split into language-agnostic (`common/`) and Python-specific (`python/`) rules. Each file covers one convention with a rationale and code example.

| Scope | Files |
|-------|-------|
| `common/` | `coding-style.md`, `code-review.md`, `patterns.md`, `security.md`, `testing.md` |
| `python/` | `coding-style.md`, `fastapi.md`, `patterns.md`, `security.md`, `tests.md` |

---

### Skills — `.claude/skills/`

Invokable as `/<skill-name>` in Claude Code chat. Each skill is a multi-phase workflow defined in a `SKILL.md` file.

| Skill | Purpose |
|-------|---------|
| `/prepare-docstrings <file>` | Add or rewrite docstrings in NumPy/SciPy format |
| `/add-type-hints <file>` | Infer and add type annotations; asks when uncertain |
| `/python-testing <path>` | Write pytest tests using TDD |
| `/python-patterns` | Non-obvious Python patterns (typed decorators, immutability, exception chaining) |
| `/nextflow-patterns` | Production-ready Nextflow DSL2 habits |
| `/nextflow-testing` | Nextflow pipeline testing with nf-test |

---

### Plugin — `plugins/gh-workflow/`

Bundles GitHub workflow automation into a single installable plugin. Requires the official `github` MCP plugin and `GITHUB_PERSONAL_ACCESS_TOKEN` in the environment.

**Commands:**

| Command | File | Purpose |
|---------|------|---------|
| `/gh-issue [owner/repo:] <description>` | `gh-issue.md` | Draft and create a structured GitHub issue (confirmation-gated) |
| `/gh-my-issues [filters]` | `gh-my-issues.md` | List issues assigned to me, grouped by repo |
| `/gh-my-prs [filters]` | `gh-my-prs.md` | List PRs I authored, review-requested, or assigned |
| `/gh-pr-draft [base:branch]` | `gh-pr-draft.md` | Draft and create a PR with fixed structure (accept/refuse gate) |
| `/gh-pr-review <num\|url>` | `gh-pr-review.md` | Structured PR review (URGENT/HIGH/MEDIUM/LOW) — never posts |

**Bundled agent:**

| Agent | File | Model | Purpose |
|-------|------|-------|---------|
| **pr-reviewer** | `agents/pr-reviewer.md` | Claude Sonnet 4.6 | Fetches PR data via GitHub MCP, classifies findings, confidence-gated |

---

## Data Flow

### Issue creation

```
User: /gh-issue owner/repo: <description>
  → Resolve repo from argument or active context
  → Fetch existing labels + duplicate check via GitHub MCP
  → Draft structured issue (Summary / Context / Repro / Expected-Actual / Scope / Acceptance Criteria)
  → Show draft via AskUserQuestion (confirm / edit / cancel)
  → Create issue via mcp__github__create_issue ONLY after confirmation
```

### PR review

```
User: /gh-pr-review <num>
  → Delegate to pr-reviewer subagent
  → Agent fetches PR metadata, diff, and comments via GitHub MCP
  → Classify findings URGENT / HIGH / MEDIUM / LOW (confidence ≥ 80%)
  → Surface Markdown report verbatim — no GitHub writes
```

### PR draft

```
User: /gh-pr-draft [base:branch]
  → Read git log for commits since base branch
  → Draft PR body: What this does / Changes / What to review / Testing
  → Show draft via AskUserQuestion (accept / edit / refuse)
  → Push branch if needed, create PR via GitHub MCP ONLY after accept
```

---

## External Dependencies

| Dependency | Purpose |
|------------|---------|
| Claude Code (VS Code extension) | Chat interface and code generation |
| Claude Sonnet 4.6 | Model backend for agents and skills |
| Official `github` MCP plugin | GitHub API access for gh-workflow commands |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Auth for GitHub MCP (stored outside this repo) |

No runtime dependencies — this is a configuration/template repository with no executable code.

---

## Development Phases

### ✅ Phase 1 — Core setup
- Global Claude Code instructions (`CLAUDE.md`)
- Agents: `code-reviewer`, `code-explorer`
- Rules: `common/` and `python/` convention files
- Architecture documentation (`docs/INDEX.md`)

### ✅ Phase 2 — Skills and plugins
- Skills: `prepare-docstrings`, `add-type-hints`, `python-testing`, `python-patterns`, `nextflow-patterns`, `nextflow-testing`
- Plugin `gh-workflow`: issue creation, PR drafting, PR review, issue/PR listing

### 📋 Phase 3 — Extended capabilities
- [ ] Per-language rule sets (JavaScript, TypeScript)
- [ ] Custom MCP servers for project-local context
- [ ] Additional specialized agents
