# Claudia — Architecture Index

**Last Updated:** May 21, 2026

## Overview

**claudia** is a personal, control-first Claude Code framework for Python and
Nextflow development. It bundles commands, workflows, agents, skills, and
rules into a single Claude Code plugin (`plugins/claudia/`) plus a Python
CLI (`claudia_tools/`).

Two principles are framework-wide:

- **Control-first** — direction-locking artifacts and outward actions pass
  through a [review gate](../plugins/claudia/rules/common/review-gate.md)
  before being accepted.
- **Safe to share** — model-agnostic guardrails for AI use on lab
  repositories.

---

## Repository Structure

```
claudia/
├── CLAUDE.md                        # Project instructions; @-imports plugin rules so they
│                                    #   become always-on for every skill and agent
├── claudia_tools/                   # Python package — the `claudia` CLI; modules: output,
│                                    #   markers, state, config, phase, templates, gates,
│                                    #   detect, env, verification; pyproject.toml; pytest suite
├── plugins/
│   └── claudia/                     # The unified Claude Code plugin
│       ├── .claude-plugin/plugin.json
│       ├── config.template.json     # Config schema; defaults bundled in claudia_tools/data/
│       ├── commands/                # 10 thin entry points: /claudia (dispatcher),
│       │                            #   9 /claudia-* phase commands, 5 /gh-* GitHub commands
│       ├── workflows/               # Orchestration files; each calls the `claudia` CLI
│       ├── agents/                  # researcher, planner, executor, verifier,
│       │                            #   code-explorer, code-reviewer, nextflow-reviewer,
│       │                            #   domain-reviewer, pr-reviewer
│       ├── skills/                  # claudia:prepare-docstrings, claudia:add-type-hints,
│       │                            #   claudia:python-testing, claudia:python-patterns,
│       │                            #   claudia:nextflow-patterns, claudia:nextflow-testing
│       ├── rules/
│       │   ├── common/              # code-review, coding-style, patterns, security,
│       │   │                        #   testing, review-gate
│       │   └── python/              # coding-style, fastapi, patterns, security, tests
│       ├── templates/               # PROJECT, ROADMAP, STATE, CONTEXT, DECISIONS, ENVIRONMENT
│       └── README.md
├── docs/INDEX.md                    # This file
└── README.md
```

---

## Components

### Project instructions — `CLAUDE.md`

Auto-loaded by Claude Code. Inlines the plugin's rule files via `@`-imports
so every skill, agent, and workflow inherits them as always-on context — no
per-skill modification needed. Consumer projects mirror the same `@`-imports
block in their own `CLAUDE.md`.

### Rules — `plugins/claudia/rules/`

Conventions split into `common/` (language-agnostic) and `python/`
(Python-specific). The framework infrastructure rule:

| Rule | Role |
|------|------|
| `review-gate.md` | The control principle — draft → present → accept/edit/cancel for every outward or direction-locking action |

### Agents — `plugins/claudia/agents/`

| Agent | Model | Purpose |
|-------|-------|---------|
| `researcher` | Sonnet/Opus | Read-only investigation → findings brief |
| `planner` | Opus | Roadmap phase → ordered task breakdown |
| `executor` | Sonnet | Implements one task, one atomic commit |
| `verifier` | Sonnet | Two-stage review: spec compliance, then code quality |
| `code-explorer` | Sonnet | Deep codebase exploration |
| `code-reviewer` | Sonnet | Security, correctness, quality review |
| `nextflow-reviewer` | Sonnet | Nextflow DSL2 review — reproducibility, channels, resources, nf-test |
| `domain-reviewer` | Sonnet | Bioinformatics output sanity — reference builds, coordinates, counts |
| `pr-reviewer` | Sonnet | Confidence-gated PR review; never posts to GitHub |

### Skills — `plugins/claudia/skills/`

Namespaced `claudia:<name>`. Invoked through `/claudia`, directly, or by
auto-trigger on description match.

| Skill | Purpose |
|-------|---------|
| `claudia:prepare-docstrings` | NumPy/SciPy docstrings |
| `claudia:add-type-hints` | Infer type annotations |
| `claudia:python-testing` | pytest TDD |
| `claudia:python-patterns` | Non-obvious Python patterns |
| `claudia:nextflow-patterns` | Nextflow DSL2 habits |
| `claudia:nextflow-testing` | nf-test patterns |

---

## Engine — `claudia_tools` (the `claudia` CLI)

Tested Python package that owns every deterministic op the workflow needs:

| Module | Responsibility |
|---|---|
| `output` | `{ok, data, error}` envelope; `ClaudiaError` |
| `markers` | Read/replace HTML-comment-delimited regions in Markdown |
| `state` | STATE.md status fields and task checkboxes |
| `config` | Schema-validated `.planning/config.json` access; `config init` writes defaults |
| `phase` | ROADMAP.md phase listing and status transitions |
| `templates` | `{{var}}` template rendering; `render_to_file` for direct output |
| `gates` | Per-artifact review-gate acceptance ledger |
| `detect` | Project-type detection: Python lib vs Nextflow pipeline |
| `env` | Tool-version capture + ENVIRONMENT.md render |
| `verification` | Human verification checklist (gates `/claudia-ship`) |

Every CLI command emits the JSON envelope by default; `--text` for humans;
errors set a non-zero exit.

---

## Plugin — `claudia`

The unified Claude Code plugin. One manifest, one folder. Every
`/claudia-*` and `/gh-*` command file is a thin pointer; orchestration lives
in [`plugins/claudia/workflows/`](../plugins/claudia/workflows/) and calls
the `claudia` CLI for every deterministic op.

### Entry point — `/claudia` dispatcher

Free-form natural-language router. Parses intent from `$ARGUMENTS` and
invokes the matching skill or workflow command. Ambiguous intent triggers
`AskUserQuestion` rather than a silent pick.

### Phase commands

| Command | Output |
|---------|--------|
| `/claudia-map` | `.planning/CONTEXT.md` |
| `/claudia-new` | `PROJECT.md`, `ROADMAP.md`, `config.json` |
| `/claudia-discuss` | `.planning/DECISIONS.md` |
| `/claudia-plan` | task breakdown in `STATE.md` |
| `/claudia-execute` | code + atomic commits |
| `/claudia-verify` | verification report |
| `/claudia-ship` | pull request (via `/gh-pr-draft`) |
| `/claudia-progress` | status report (read-only) |
| `/claudia-settings` | updated `config.json` |

### GitHub commands

| Command | Purpose | Writes? |
|---|---|---|
| `/gh-issue` | Draft + create structured issue | Yes (gated) |
| `/gh-my-issues` | List assigned issues | No |
| `/gh-my-prs` | List my PRs | No |
| `/gh-pr-draft` | Draft + create PR | Yes (gated) |
| `/gh-pr-review` | Structured PR review | **Never** |

Requires the official `github` MCP plugin and `GITHUB_PERSONAL_ACCESS_TOKEN`.

### State — `.planning/`

`PROJECT.md`, `ROADMAP.md`, `CONTEXT.md`, `DECISIONS.md`, `STATE.md`,
`ENVIRONMENT.md`, `VERIFICATION.md`, `config.json`, `gates.json`. Persists
across sessions; gitignored by default. `ROADMAP.md`, `DECISIONS.md`, and
the plan task breakdown are direction-locking — changes pass through the
review gate. `VERIFICATION.md` holds the human checklist that gates
`/claudia-ship`.

### Config — `.planning/config.json`

`mode` (interactive/yolo), `model_profile` (quality/balanced/budget), per-agent
toggles, `execution.parallel` (default false). The review gate and secret scan
are not configurable.

---

## Data Flow — the workflow loop

```
/claudia-map      → CONTEXT.md       (existing repo only)
/claudia-new      → PROJECT.md, ROADMAP.md, config.json   [review gate: roadmap]
/claudia-discuss  → DECISIONS.md     [review gate: decisions]
/claudia-plan     → task breakdown   [review gate: plan]
/claudia-execute  → code + commits   (executor subagents, sequential)
/claudia-verify   → report           (two-stage review + secret scan)
/claudia-ship     → pull request     [review gate: PR draft, via /gh-pr-draft]
                 ↑ /claudia-progress reads STATE.md at any point
                 ↑ /claudia <natural-language> dispatches into any of the above
```

---

## External Dependencies

| Dependency | Purpose |
|------------|---------|
| Claude Code (VS Code extension) | Chat interface and code generation |
| Official `github` MCP plugin | GitHub API access for `/gh-*` and `/claudia-ship` |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Auth for GitHub MCP |
| `claudia_tools` Python CLI | Deterministic state/config/phase/template/gate ops |

---

## Development Phases

### ✅ Phase 1 — Core setup
Global instructions, `code-reviewer` / `code-explorer` agents, `common/` and
`python/` rules.

### ✅ Phase 2 — Skills and GitHub commands
Python and Nextflow skills; GitHub commands.

### ✅ Phase 3 — Workflow framework foundation
`review-gate` rule; phased-workflow commands (9), agents (4), state files,
config; helper-skill auto-triggering.

### ✅ Phase 4 — `claudia-tools` engine
Tested Python `claudia` CLI: state/config/phase/template/gate operations
behind a `{ok,data,error}` JSON envelope. Workflow commands rewritten to
call it. Marker-delimited regions in shipped templates.

### ✅ Phase 5 — Project-type detection & environment capture
`claudia detect` recognises Python vs Nextflow. `claudia env capture`
snapshots tool versions for the bioinformatics stack and renders
`ENVIRONMENT.md`. `/claudia-verify` branches its automated runner on the
detected type.

### ✅ Phase 6 — Two-tier verification + review agents
`claudia verify init/add/confirm/ready` tracks a human checklist (e.g. full
pipeline runs) that gates `/claudia-ship`. `nextflow-reviewer` and
`domain-reviewer` agents pair with `code-reviewer` for pipeline / output
review.

### ✅ Phase 7 — Plugin consolidation
`.claude/{agents,rules,skills}/`, `plugins/claudia-workflow/`, and
`plugins/gh-workflow/` merged into a single `plugins/claudia/` plugin.
`/claudia` natural-language dispatcher added as the primary entry point.
Rules made always-on via `@`-imports in `CLAUDE.md`.

### 📋 Deferred
- [ ] Commit-validation and context-monitor hooks.
- [ ] `rules/` → `references/` split.
- [ ] Parallel-wave execution refinement.
