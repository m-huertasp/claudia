# Claudia — Architecture Index

**Last Updated:** May 20, 2026

## Overview

**claudia** is a personal, control-first Claude Code framework for Python and
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
claudia/
├── CLAUDE.md                        # Global Claude Code instructions (auto-loaded per project)
├── .claude/
│   ├── agents/                      # code-explorer, code-reviewer, nextflow-reviewer,
│   │                                #   domain-reviewer
│   ├── rules/
│   │   ├── common/                  # code-review, coding-style, patterns, security,
│   │   │                            #   testing, review-gate, secure-ai-use
│   │   └── python/                  # coding-style, fastapi, patterns, security, tests
│   └── skills/                      # add-type-hints, prepare-docstrings, python-testing,
│                                    #   python-patterns, nextflow-patterns, nextflow-testing,
│                                    #   claudia-new-skill
├── claudia_tools/                   # Python package — the `claudia` CLI; modules: output,
│                                    #   markers, state, config, phase, templates, gates,
│                                    #   detect, env, verification; pyproject.toml; pytest suite
├── plugins/
│   ├── claudia-workflow/             # Phased development workflow
│   │   ├── .claude-plugin/plugin.json
│   │   ├── config.template.json     # Config schema; defaults bundled in claudia_tools/data/
│   │   ├── templates/               # PROJECT, ROADMAP, STATE, CONTEXT, DECISIONS, ENVIRONMENT
│   │   ├── agents/                  # researcher, planner, executor, verifier
│   │   ├── commands/                # 9 thin /claudia-* entry points
│   │   ├── workflows/               # Orchestration files; call the `claudia` CLI
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
| `nextflow-reviewer` | Sonnet | Nextflow DSL2 review — reproducibility, channels, resources, nf-test |
| `domain-reviewer` | Sonnet | Bioinformatics output sanity — reference builds, coordinates, counts |

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
| `claudia-new-skill` | Author a new skill (extensibility path) |

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

## Plugin — `claudia-workflow`

The phased development workflow. GSD-shaped: explicit phase commands,
persistent `.planning/` state, a `config.json` of toggles. Each
`/claudia-*` command file is a thin pointer; orchestration lives in
[`plugins/claudia-workflow/workflows/`](../plugins/claudia-workflow/workflows/)
and calls the `claudia` CLI for every deterministic op.

### Phase commands

| Command | Output |
|---------|--------|
| `/claudia-map` | `.planning/CONTEXT.md` |
| `/claudia-new` | `PROJECT.md`, `ROADMAP.md`, `config.json` |
| `/claudia-discuss` | `.planning/DECISIONS.md` |
| `/claudia-plan` | task breakdown in `STATE.md` |
| `/claudia-execute` | code + atomic commits |
| `/claudia-verify` | verification report |
| `/claudia-ship` | pull request (via `gh-workflow`) |
| `/claudia-progress` | status report (read-only) |
| `/claudia-settings` | updated `config.json` |

### Workflow agents

| Agent | Role |
|-------|------|
| `researcher` | Read-only investigation → findings brief |
| `planner` | Roadmap phase → ordered task breakdown |
| `executor` | Implements one task, one atomic commit |
| `verifier` | Two-stage review: spec compliance, then code quality |

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

## Plugin — `gh-workflow`

GitHub issue/PR automation. Requires the official `github` MCP plugin and
`GITHUB_PERSONAL_ACCESS_TOKEN`. Every write action is confirmation-gated;
`/gh-pr-review` never posts. Commands: `gh-issue`, `gh-my-issues`,
`gh-my-prs`, `gh-pr-draft`, `gh-pr-review`. Bundled agent: `pr-reviewer`.

---

## Data Flow — the workflow loop

```
/claudia-map      → CONTEXT.md       (existing repo only)
/claudia-new      → PROJECT.md, ROADMAP.md, config.json   [review gate: roadmap]
/claudia-discuss  → DECISIONS.md     [review gate: decisions]
/claudia-plan     → task breakdown   [review gate: plan]
/claudia-execute  → code + commits   (executor subagents, sequential)
/claudia-verify   → report           (two-stage review + secret scan)
/claudia-ship     → pull request     [review gate: PR draft, via gh-workflow]
                 ↑ /claudia-progress reads STATE.md at any point
```

---

## External Dependencies

| Dependency | Purpose |
|------------|---------|
| Claude Code (VS Code extension) | Chat interface and code generation |
| Official `github` MCP plugin | GitHub API access for `gh-workflow` / `/claudia-ship` |
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
`review-gate` / `secure-ai-use` rules; `claudia-workflow` plugin (9 commands,
4 agents, state files, config); `claudia-new-skill` meta-skill; helper-skill
auto-triggering.

### ✅ Phase 4 — `claudia-tools` engine
Tested Python `claudia` CLI: state/config/phase/template/gate operations
behind a `{ok,data,error}` JSON envelope. Workflow commands rewritten to
call it. Marker-delimited regions in shipped templates.

### ✅ Phase 5 — Project-type detection & environment capture
`claudia detect` recognises Python vs Nextflow. `claudia env capture`
snapshots tool versions for the bioinformatics stack and renders
`ENVIRONMENT.md`. `/claudia-verify` branches its automated runner on the
detected type.

### ✅ Phase 6 — Two-tier verification + review agents + this doc update
`claudia verify init/add/confirm/ready` tracks a human checklist (e.g. full
pipeline runs) that gates `/claudia-ship`. New `nextflow-reviewer` and
`domain-reviewer` agents pair with `code-reviewer` for pipeline / output
review. Documentation refreshed.

### 📋 Deferred
- [ ] Commit-validation and context-monitor hooks (originally Phase 5 of
      the roadmap).
- [ ] `rules/` → `references/` split (deferred from Phase 6 — kept the
      diff focused on capability).
- [ ] Parallel-wave execution refinement.
