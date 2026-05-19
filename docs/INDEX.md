# clavia — Architecture Index

**Last Updated:** May 19, 2026

## Overview

**clavia** is a personal, control-first Claude Code framework for Python and
Nextflow development. It provides a phased development workflow plus reusable
instructions, agents, rules, and skills, designed to be symlinked or copied
into any project.

Two principles are framework-wide:

- **Control-first** — direction-locking artifacts and outward actions pass
  through a [review gate](../.claude/rules/common/review-gate.md) before
  being accepted.
- **Safe to share** — model-agnostic guardrails for AI use on lab
  repositories ([secure-ai-use](../.claude/rules/common/secure-ai-use.md)).

---

## Repository Structure

```
clavia/
├── CLAUDE.md                        # Global Claude Code instructions (auto-loaded per project)
├── .claude/
│   ├── agents/                      # code-explorer, code-reviewer
│   ├── rules/
│   │   ├── common/                  # code-review, coding-style, patterns, security,
│   │   │                            #   testing, review-gate, secure-ai-use
│   │   └── python/                  # coding-style, fastapi, patterns, security, tests
│   └── skills/                      # add-type-hints, prepare-docstrings, python-testing,
│                                    #   python-patterns, nextflow-patterns, nextflow-testing,
│                                    #   clavia-new-skill
├── plugins/
│   ├── clavia-workflow/             # Phased development workflow
│   │   ├── .claude-plugin/plugin.json
│   │   ├── config.template.json     # Config schema, copied to .planning/config.json
│   │   ├── templates/               # State-file skeletons (PROJECT, ROADMAP, STATE,
│   │   │                            #   CONTEXT, DECISIONS)
│   │   ├── agents/                  # researcher, planner, executor, verifier
│   │   ├── commands/                # 9 /clavia-* phase commands
│   │   └── README.md
│   └── gh-workflow/                 # GitHub issue / PR commands
├── docs/INDEX.md                    # This file
└── README.md
```

---

## Components

### Instructions — `CLAUDE.md`

Auto-loaded by Claude Code in any project that includes it. Sets global
behavior and points at the framework's two core rules.

### Rules — `.claude/rules/`

Always-loaded conventions. `common/` is language-agnostic, `python/` is
Python-specific. Two `common/` rules are framework infrastructure:

| Rule | Role |
|------|------|
| `review-gate.md` | The control principle — draft → present → accept/edit/cancel for every outward or direction-locking action |
| `secure-ai-use.md` | Model-agnostic guardrails — never send secrets or unpublished data; pre-publish secret scan |

### Agents — `.claude/agents/`

| Agent | Model | Purpose |
|-------|-------|---------|
| `code-explorer` | Sonnet | Deep codebase exploration |
| `code-reviewer` | Sonnet | Security, correctness, quality review |

### Skills — `.claude/skills/`

Invokable as `/<skill-name>`; helper skills auto-trigger on file context.

| Skill | Purpose |
|-------|---------|
| `prepare-docstrings` | NumPy/SciPy docstrings |
| `add-type-hints` | Infer type annotations |
| `python-testing` | pytest TDD |
| `python-patterns` | Non-obvious Python patterns |
| `nextflow-patterns` | Nextflow DSL2 habits |
| `nextflow-testing` | nf-test patterns |
| `clavia-new-skill` | Author a new skill (extensibility path) |

---

## Plugin — `clavia-workflow`

The phased development workflow. GSD-shaped: explicit phase commands,
persistent `.planning/` state, a `config.json` of toggles.

### Phase commands

| Command | Output |
|---------|--------|
| `/clavia-map` | `.planning/CONTEXT.md` |
| `/clavia-new` | `PROJECT.md`, `ROADMAP.md`, `config.json` |
| `/clavia-discuss` | `.planning/DECISIONS.md` |
| `/clavia-plan` | task breakdown in `STATE.md` |
| `/clavia-execute` | code + atomic commits |
| `/clavia-verify` | verification report |
| `/clavia-ship` | pull request (via `gh-workflow`) |
| `/clavia-progress` | status report (read-only) |
| `/clavia-settings` | updated `config.json` |

### Workflow agents

| Agent | Role |
|-------|------|
| `researcher` | Read-only investigation → findings brief |
| `planner` | Roadmap phase → ordered task breakdown |
| `executor` | Implements one task, one atomic commit |
| `verifier` | Two-stage review: spec compliance, then code quality |

### State — `.planning/`

`PROJECT.md`, `ROADMAP.md`, `CONTEXT.md`, `DECISIONS.md`, `STATE.md`,
`config.json`. Persists across sessions; gitignored by default.
`ROADMAP.md`, `DECISIONS.md`, and the plan task breakdown are
direction-locking — changes pass through the review gate.

### Config — `.planning/config.json`

`mode` (interactive/yolo), `model_profile` (quality/balanced/budget), per-agent
toggles, `execution.parallel` (default false). The review gate and secret scan
are not configurable.

---

## Plugin — `gh-workflow`

GitHub issue/PR automation. Requires the official `github` MCP plugin and
`GITHUB_PERSONAL_ACCESS_TOKEN`. Every write action is confirmation-gated;
`/gh-pr-review` never posts. Commands: `gh-issue`, `gh-my-issues`,
`gh-my-prs`, `gh-pr-draft`, `gh-pr-review`. Bundled agent: `pr-reviewer`.

---

## Data Flow — the workflow loop

```
/clavia-map      → CONTEXT.md       (existing repo only)
/clavia-new      → PROJECT.md, ROADMAP.md, config.json   [review gate: roadmap]
/clavia-discuss  → DECISIONS.md     [review gate: decisions]
/clavia-plan     → task breakdown   [review gate: plan]
/clavia-execute  → code + commits   (executor subagents, sequential)
/clavia-verify   → report           (two-stage review + secret scan)
/clavia-ship     → pull request     [review gate: PR draft, via gh-workflow]
                 ↑ /clavia-progress reads STATE.md at any point
```

---

## External Dependencies

| Dependency | Purpose |
|------------|---------|
| Claude Code (VS Code extension) | Chat interface and code generation |
| Official `github` MCP plugin | GitHub API access for `gh-workflow` / `/clavia-ship` |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Auth for GitHub MCP |

No runtime dependencies — this is a configuration/template repository.

---

## Development Phases

### ✅ Phase 1 — Core setup
Global instructions, `code-reviewer` / `code-explorer` agents, `common/` and
`python/` rules.

### ✅ Phase 2 — Skills and gh-workflow
Python and Nextflow skills; `gh-workflow` plugin.

### ✅ Phase 3 — Workflow framework foundation
`review-gate` / `secure-ai-use` rules; `clavia-workflow` plugin (9 commands,
4 agents, state files, config); `clavia-new-skill` meta-skill; helper-skill
auto-triggering.

### 📋 Phase 4 — Extended capabilities
- [ ] Bioinformatics skills — reproducibility (conda/containers), HPC/SLURM
- [ ] Nextflow-tier rules (`.claude/rules/nextflow/`)
- [ ] One-command installer for sharing across the lab
- [ ] Parallel-wave execution refinement
