# claudia

> A personal Claude Code framework for Python and Nextflow development.

---

## What this is

**claudia** is a Claude Code framework bundled as a single plugin. It provides
a phased development **workflow** — understand, brief, plan, execute, verify,
ship — plus reusable agents, rules, and skills, all in one place.

As of now, it works with Claude Code in VS Code, and the rules are written to hold for any AI model.

Two principles run through everything:

- **Control-first.** Every direction-locking artifact (roadmap, plan, design
  decisions) and every outward action (issues, PRs, pushes) passes through a
  **review gate**: drafted, shown in full, and acted on only after you accept.
  "Edit" means you can rewrite anything — your text is used verbatim.
- **Safe to share.** The rules are model-agnostic and include guardrails for
  using AI on lab repositories — no secrets, no unpublished research data, a
  secret scan before anything is published.

---

## The deterministic engine — `claudia-tools`

The workflow's mechanical work — parsing and updating planning files,
validating config, transitioning phases, rendering templates, gating
review acceptance, detecting project type, capturing the tool environment,
tracking the human verification checklist — runs through a tested Python
CLI called `claudia`. The orchestrating model only reads and judges; it
never hand-edits planning files.

```bash
uv tool install ./claudia_tools     # or pipx install ./claudia_tools
claudia --help
```

See [claudia_tools/README.md](claudia_tools/README.md).

## The plugin — `plugins/claudia/`

Everything else lives here: commands, workflows, agents, skills, rules, and
templates.

### Entry point — `/claudia` dispatcher

Free-form natural-language routing into the framework. Examples:

- `/claudia prepare docstrings of pipeline.py` → `claudia:prepare-docstrings`
- `/claudia ship` → `/claudia-ship`
- `/claudia plan phase 2` → `/claudia-plan`

When intent is ambiguous, the dispatcher asks via `AskUserQuestion`. Direct
slash commands also work.

### Phased workflow

| Command | Phase |
|---|---|
| `/claudia-understand` | One-time codebase bootstrap → `CONTEXT.md`, `ENVIRONMENT.md`, `config.json`. Re-runnable as a refresh on drift. |
| `/claudia-brief` | Per-issue entry point → `ISSUE_BRIEF.md`, proposes a `{keyword}/{description}` branch, then chains into intent-mode discuss |
| `/claudia-plan` | Reads brief + decisions → drafts `ROADMAP.md`, chains into approach-mode discuss, initializes `STATE.md` task breakdown |
| `/claudia-execute` | Implement tasks via executor subagents (sequential by default) |
| `/claudia-verify` | Two-stage review + secret scan + `CONTEXT.md` drift check |
| `/claudia-ship` | Open a PR via `/claudia-draft-pr` (re-runs the drift check) |
| `/claudia-progress` | Where things stand / next step |
| `/claudia-settings` | View or edit `.planning/config.json` |

State persists in `.planning/` so work resumes cold across sessions. Each
`/claudia-*` command is a thin entry point pointing at a workflow file under
[plugins/claudia/workflows/](plugins/claudia/workflows/), which invokes the
`claudia` CLI for every deterministic op. See
[plugins/claudia/README.md](plugins/claudia/README.md).

---

## Folder structure

```
claudia/
├── CLAUDE.md                        # Project instructions; @-imports plugin rules
├── claudia_tools/                   # Python package: the `claudia` CLI (state, config, phase,
│                                    #   templates, gates, detect, env, verify)
├── plugins/
│   └── claudia/                     # The unified Claude Code plugin
│       ├── .claude-plugin/plugin.json
│       ├── commands/                # /claudia, /claudia-* entry points
│       ├── workflows/               # Orchestration text (calls the `claudia` CLI)
│       ├── agents/                  # researcher, planner, executor, verifier,
│       │                            #   code-explorer, code-reviewer, nextflow-reviewer,
│       │                            #   domain-reviewer, pr-reviewer
│       ├── skills/                  # prepare-docstrings, add-type-hints, python-testing,
│       │                            #   python-patterns, nextflow-patterns, nextflow-testing
│       ├── rules/                   # common/ + python/ (loaded via @-imports in CLAUDE.md)
│       ├── templates/               # ISSUE_BRIEF, ROADMAP, STATE, CONTEXT, DECISIONS, ENVIRONMENT
│       └── config.template.json
├── docs/                            # docs/INDEX.md — architecture overview
└── README.md                        # This file
```

---

## Skills

Plugin skills are namespaced `claudia:<name>`. Trigger them via `/claudia`,
invoke directly, or let them auto-trigger.

| Skill | Purpose |
|---|---|
| `claudia:prepare-docstrings` | Add or rewrite docstrings in NumPy/SciPy format |
| `claudia:add-type-hints` | Infer and add type annotations; asks when uncertain |
| `claudia:python-testing` | Write pytest tests using TDD |
| `claudia:python-patterns` | Non-obvious Python patterns |
| `claudia:nextflow-patterns` | Production-ready Nextflow DSL2 habits |
| `claudia:nextflow-testing` | Nextflow pipeline testing with nf-test |

---

## Agents

| Agent | Purpose |
|---|---|
| `code-explorer` | Deep codebase exploration — traces execution paths, maps architecture |
| `code-reviewer` | Security, correctness, and quality review |
| `nextflow-reviewer` | Nextflow DSL2 review — reproducibility, channel safety, resource directives, nf-test coverage |
| `domain-reviewer` | Bioinformatics output sanity — reference builds, coordinate systems, count-of-magnitude checks, multiple-testing |
| `pr-reviewer` | Confidence-gated PR review; **doesn't post to GitHub** |
| `researcher` / `planner` / `executor` / `verifier` | The four phased-workflow roles |

---

## GitHub commands

Require the [`gh` CLI](https://cli.github.com/) installed and authenticated
via `gh auth login`. Issues and PRs are created under the authenticated
GitHub account — i.e. attributed to the user, not to Claude. Every write
action is gated behind explicit confirmation.

| Command | Purpose |
|---|---|
| `/claudia-write-issue [owner/repo:] <description>` | Draft and create a structured issue (gated) |
| `/claudia-draft-pr [base:branch]` | Draft and create a PR (gated) |
| `/claudia-pr-review <num\|url>` | Structured PR review — never posts to GitHub |

---

## Rules

Plugin rule files live at [plugins/claudia/rules/](plugins/claudia/rules/) and
are made always-on by `@`-importing them from a project's `CLAUDE.md`. See
the **Always-on rules** block in this repo's [CLAUDE.md](CLAUDE.md) for the
canonical list — consumer projects can mirror it once on install.

---

## Documentation

Architecture overview: **[docs/INDEX.md](docs/INDEX.md)**.
