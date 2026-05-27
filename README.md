# claudia

> A "cautiously functional" framework for Python and Nextflow work.

---

## What this is

**claudia** is a single plugin that bundles a phased workflow
(understand → plan → execute → close), a set of rules, a small
set of agents, and a handful of skills. One plugin, one command, one place
to look when something goes sideways.

It currently runs in Claude Code (VS Code or terminal). The rules try to be
model-agnostic so they keep their meaning if you swap the model under them —
no promises, still working.

Two principles run through everything:

- **Control-first.** Every direction-locking artefact (plan files, PR
  drafts, issue drafts) and every outward action (push, PR open, issue
  create) goes through a **review gate**. claudia drafts; you accept, edit,
  or cancel. "Edit" means your text is used verbatim — no creative
  reinterpretation.
- **Safe-ish to share.** Rules include guardrails for using AI on lab
  repositories — no secrets in commits, secret scan before anything is
  published, and a healthy suspicion of anything the model wants to do on
  GitHub.

---

## The plugin — `plugins/claudia/`

Everything lives here. There is exactly one slash command: **`/claudia`**.
There is no second slash command. Please do not ask for a second slash
command.

### Entry point — `/claudia`

`/claudia` routes in two modes:

1. **Explicit verb** — `/claudia <verb> [args]` runs the matching skill
   directly. No NLP, no guessing, no `AskUserQuestion` round-trip.
2. **Natural language** — `/claudia <free-form>` matches your intent
   against a keyword table. One match → it runs; multiple matches → it
   asks; no matches → it shows the verb list and gives up gracefully.

Examples:

- `/claudia understand` → bootstrap the project
- `/claudia plan 42` → plan, seeded from GitHub issue 42
- `/claudia let's start a new feature` → routes to `plan`
- `/claudia prepare-docstrings src/foo.py` → runs the docstring skill
- `/claudia` (no args) → prints the verbs, branch, mode, and the most
  recent plan file

### Workflow verbs

| Verb | Purpose | Gate |
|---|---|---|
| `understand` | One-time codebase bootstrap → `.planning/CONTEXT.md` + `.planning/config.json`. Re-runnable as a `refresh` when the code drifts away from the notes. | summary only |
| `plan [issue-ref]` | Intent + design decisions + ordered task checklist in **one** file at `.planning/plans/YYYY-MM-DD-<slug>.md`. Optionally seeds from `gh issue view`. | **plan-accept** |
| `execute [T1 T2 …]` | Implement the plan, one task at a time, in a fresh executor context. Ticks the checkboxes as it goes. | per-commit (in `pair`) |
| `close [base:<branch>]` | Two-stage verification (with reviewers dispatched **in parallel**) + secret scan + draft PR. | **PR-accept** |

### Utility verbs

| Verb | Purpose |
|---|---|
| `rules` | Injects the `## Claudia Rules` section into the project's `CLAUDE.md` as `@`-imports. Idempotent and detect-aware. |
| `pr-review <num\|url>` | Structured, confidence-gated PR review. **Never posts to GitHub** — output stays in your terminal. |
| `write-issue <description>` | Draft a GitHub issue and create it via `gh`. Gated on explicit confirmation, even if you said "just do it" up front. |
| `add-type-hints <path>` | Add type annotations to a Python file. Also auto-triggers on relevant context. |
| `prepare-docstrings <path>` | Add/rewrite docstrings in NumPy/SciPy format. Also auto-triggers on relevant context. |

The authoritative routing table is in
[plugins/claudia/skills/claudia/SKILL.md](plugins/claudia/skills/claudia/SKILL.md).
That file is the source of truth; this table is a summary that will
inevitably drift first.

---

## State — `.planning/`

Persists across sessions; agents reload it cold. Kept out of git by default
(check your `.gitignore`).

**Project-level** (written by `/claudia understand`):

- `CONTEXT.md` — narrative baseline + a sentinel-bounded `## Environment`
  section managed by the shared script. Do not hand-edit the sentinel
  block; the script will overwrite it.
- `config.json` — `{ mode, agents }`. That's the whole schema.

**Per-task** (one file per task; old files stay in place):

- `plans/YYYY-MM-DD-<slug>.md` — four sections: `## Intent`,
  `## Design decisions`, `## Tasks` (checkboxes — this *is* the persistence
  for execution progress), `## Notes`.

That's the entire on-disk surface. No `STATE.md`, no `VERIFICATION.md`,
no `ISSUE_BRIEF.md`, no `ROADMAP.md`, no `DECISIONS.md`, no
`ENVIRONMENT.md`. v2 deliberately collapsed all of those.

---

## Configuration — `config.json`

```json
{
  "mode": "pair",
  "agents": {
    "domain_reviewer": false,
    "nextflow_reviewer": true
  }
}
```

| Setting | Values | Effect |
|---|---|---|
| `mode` | `pair`, `yolo` | `pair` (default): executor stops after each task so you can review and commit; `close` hands you the PR draft. `yolo`: executor commits autonomously following `commit-style`; `close` pushes and opens the PR via `gh`. |
| `agents.domain_reviewer` | `true`, `false` | Toggle the bioinformatics output reviewer for `close`. |
| `agents.nextflow_reviewer` | `true`, `false` | Toggle the Nextflow DSL2 reviewer for `close`. (Fires automatically when `.nf` is in the diff, if `true`.) |

The **review gate** and the **secret scan** are not configurable. They
always run. This is intentional.

---

## Agents

Workflow agents (called by skills):

| Agent | Role |
|---|---|
| `planner` | Task breakdown for `plan`. |
| `executor` | Implements one task in a fresh context for `execute`. |
| `verifier` | Orchestrates the two-stage review for `close`; dispatches reviewers **in parallel** (not sequentially — this matters for wall time). |
| `researcher` | Read-only investigation, used by `plan` and `understand`. |

Review agents (dispatched by `verifier`):

| Agent | When |
|---|---|
| `code-reviewer` | Always. |
| `nextflow-reviewer` | When `.nf` / `nextflow.config` is in the diff and the toggle is on. |
| `domain-reviewer` | When `agents.domain_reviewer == true` *and* the diff touches pipeline code. |

Utility agents:

| Agent | Used by |
|---|---|
| `pr-reviewer` | `pr-review` skill (never posts to GitHub). |
| `code-explorer` | `understand` skill, only when concrete dispatch triggers fire (subsystem focus, mixed/layered project, explicit `trace` arg). Complementary to `researcher`, not a replacement. |

---

## Skills

Plugin skills are namespaced `claudia:<name>`.

**Auto-triggered only** (knowledge skills — they fire when the description matches):

- `claudia:python-testing`, `claudia:python-patterns`
- `claudia:nextflow-testing`, `claudia:nextflow-patterns`

**Callable only** (workflow + utility skills — fire only via `/claudia <verb>`):

- `claudia:understand`, `claudia:plan`, `claudia:execute`, `claudia:close`
- `claudia:rules`, `claudia:pr-review`, `claudia:write-issue`

**Dual-mode** (both):

- `claudia:add-type-hints`, `claudia:prepare-docstrings`

---

## Shared script — `plugins/claudia/scripts/claudia`

One Python file, stdlib-only, no install step. Invoked from skills as
`python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia <cmd>`.

| Subcommand | Purpose |
|---|---|
| `detect` | Report project type: `python` / `nextflow` / `mixed` / `unknown`. |
| `config init \| get \| set` | Manage `.planning/config.json`. |
| `env capture [--section]` | Probe local tool versions. With `--section`, rewrite the sentinel-bounded `## Environment` section of `CONTEXT.md`. |
| `rules inject [--dry-run]` | Idempotently inject the `## Claudia Rules` block into `CLAUDE.md`. |

All subcommands emit a JSON envelope: `{ok, data}` on success,
`{ok, error}` on failure. Some accept `--text` if you want human output.

---

## Rules

Rule files live at [plugins/claudia/rules/](plugins/claudia/rules/) under
`common/`, `python/`, and `nextflow/`. They are **not** auto-loaded by the
plugin — consuming projects opt in by running `/claudia rules`, which
`@`-imports the right subset into the project's `CLAUDE.md` based on
`claudia detect`:

| Project type | Subsets included |
|---|---|
| `python` | `common`, `python` |
| `nextflow` | `common`, `nextflow` |
| `mixed` | `common`, `python`, `nextflow` |
| `unknown` | `common` |

To add a new rule, drop a `.md` file in the right subdirectory and the
injector will pick it up the next time `/claudia rules` runs. No registry
to update, no list to maintain.

---

## Prerequisites

- Claude Code, with this plugin enabled.
- Python 3.9+ on `PATH` (for the shared script — no `pip install`, no `uv`,
  nothing to build).
- For `pr-review`, `write-issue`, and `close` in `yolo` mode: the
  [`gh` CLI](https://cli.github.com/), authenticated via `gh auth login`.
  Issues and PRs are created under your account — attributed to you, not
  to the model.

## Install

Add this repo as a Claude Code marketplace and enable the `claudia` plugin.
Then, in a project:

```text
/claudia understand    # writes .planning/CONTEXT.md + .planning/config.json
/claudia rules         # injects the Claudia Rules section into CLAUDE.md
```

`understand` is one-shot (re-runnable as a refresh on drift). `rules` is
idempotent — running it twice on the same repo produces no diff.

---

## Folder structure

```
claudia/
├── CLAUDE.md                        # Project instructions; @-imports plugin rules
├── plugins/
│   └── claudia/                     # The plugin — one command, many skills
│       ├── .claude-plugin/plugin.json
│       ├── commands/                # Exactly one file: claudia.md
│       ├── agents/                  # planner, executor, verifier, researcher,
│       │                            #   code-reviewer, nextflow-reviewer,
│       │                            #   domain-reviewer, pr-reviewer, code-explorer
│       ├── skills/                  # All workflow + utility + knowledge skills
│       ├── rules/                   # common/ + python/ + nextflow/
│       └── scripts/claudia          # Stdlib-only Python helper (~250 LOC)
├── docs/                            # Architecture notes (may lag behind reality)
└── README.md                        # You are here
```

---

## What this isn't

- It's not a general-purpose framework. It's tuned for Python and Nextflow
  on small-to-medium repos, and the rules will probably feel wrong in
  other contexts.
- It's not autonomous by default. `pair` mode exists because trusting an
  LLM to push to your repo without looking at the diff is a choice, and
  it should be a deliberate one.
- It's not done. The "cautiously functional" tagline is load-bearing.
