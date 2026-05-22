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
| `verification` | Human verification checklist (gates `/claudia-close`) |

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
| `/claudia-understand` | `CONTEXT.md`, `ENVIRONMENT.md`, `config.json` (one-time; refreshable on drift) |
| `/claudia-brief` | `ISSUE_BRIEF.md` + `DECISIONS.md` (intent) + `{keyword}/{slug}` branch |
| `/claudia-plan` | `ROADMAP.md` + `DECISIONS.md` (approach) + task breakdown in `STATE.md` |
| `/claudia-execute` | code + atomic commits (`yolo`) or staged diffs you commit (`pair`) |
| `/claudia-verify` | verification report + `CONTEXT.md` drift check; fix-loop branches on `mode` |
| `/claudia-close` | PR drafted via internal draft-pr workflow; created via `gh` (`yolo`) or handed to user to open (`pair`); re-runs drift check |
| `/claudia-progress` | status report (read-only) |
| `/claudia-settings` | updated `config.json` |

The discuss and draft-pr steps are internal — discuss runs in **intent mode** from `/claudia-brief` and **approach mode** from `/claudia-plan`, both appending to a single `.planning/DECISIONS.md`. draft-pr runs from `/claudia-close`.

### GitHub commands

| Command | Purpose | Writes? |
|---|---|---|
| `/claudia-write-issue` | Draft + create structured issue | Yes (gated) |
| `/claudia-pr-review` | Structured PR review | **Never** |

PR drafting/creation is no longer a standalone command — `/claudia-close` runs `workflows/draft-pr.md` internally and gates accept before either `gh pr create` (yolo) or handing the title + body back to the user (pair).

Requires the [`gh` CLI](https://cli.github.com/) authenticated via `gh auth login`. Issues and PRs are attributed to the authenticated user, not to Claude.

### State — `.planning/`

**Project-level** (written by `/claudia-understand`, refreshed on drift):
`CONTEXT.md`, `ENVIRONMENT.md`, `config.json`.

**Per-issue** (rotated on each `/claudia-brief`; prior set archived under
`.planning/archive/<timestamp>/`): `ISSUE_BRIEF.md`, `ROADMAP.md`,
`DECISIONS.md`, `STATE.md`, `VERIFICATION.md`, `gates.json`.

Persists across sessions; gitignored by default. `ISSUE_BRIEF.md`,
`ROADMAP.md`, `DECISIONS.md`, and the plan task breakdown are
direction-locking — changes pass through the review gate.
`VERIFICATION.md` holds the human checklist that gates `/claudia-close`.

### Config — `.planning/config.json`

`mode` (`pair` default / `yolo`) drives executor commit behavior,
verify's fix-loop, and close's PR-creation step. `model_profile`
(quality/balanced/budget), per-agent toggles, `execution.parallel`
(default false; ignored in pair). The review gate and secret scan are
not configurable.

---

## Data Flow — the workflow loop

```
/claudia-understand → CONTEXT.md, ENVIRONMENT.md, config.json   (one-time; refreshable on drift)
/claudia-brief      → ISSUE_BRIEF.md + branch                  [review gate: brief]
                    │   └── chains into intent-mode discuss    → DECISIONS.md (intent)  [gate: decisions]
/claudia-plan       → ROADMAP.md                              [review gate: roadmap]
                    │   └── chains into approach-mode discuss → DECISIONS.md (approach) [gate: decisions]
                    └── task breakdown in STATE.md            [review gate: plan]
/claudia-execute    → per-task loop branched on mode:
                       yolo: executor writes + commits + claudia state task-done
                       pair: executor writes, user reviews and commits, then
                             AskUserQuestion done/skip/abort → task-done on done
/claudia-verify     → report (two-stage review + secret scan + drift check);
                       fix-loop also branches on mode
/claudia-close      → drafts PR via workflows/draft-pr.md [review gate: PR draft]
                       yolo: push + gh pr create
                       pair: push + print title/body for user to open the PR
                   ↑ /claudia-progress reads STATE.md at any point
                   ↑ /claudia <natural-language> dispatches into any of the above
```

---

## External Dependencies

| Dependency | Purpose |
|------------|---------|
| Claude Code (VS Code extension) | Chat interface and code generation |
| [`gh` CLI](https://cli.github.com/) | GitHub API access for `/claudia-write-issue`, `/claudia-pr-review`, and `/claudia-close` in `yolo` mode (authenticated via `gh auth login`) |
| `claudia_tools` Python CLI | Deterministic state/config/phase/template/gate ops |
