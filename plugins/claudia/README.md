# claudia (plugin)

The Claude Code plugin for Python and Nextflow development. One plugin
holds everything: the dispatcher, the workflow skills, the bioinformatics
agents, the rule set, and a tiny shared script.

It is **control-first**: every direction-locking artefact and every
outward action passes through a review gate before it is accepted.

## Prerequisites

- Claude Code with this plugin enabled (the single `/claudia` command,
  every skill, every agent are auto-discovered from the plugin's
  subfolders).
- Python 3.9+ on PATH (the shared script is stdlib-only; no install step).
- For GitHub helpers (`/claudia pr-review`, `/claudia write-issue`) and
  for `/claudia close` in `yolo` mode: the [`gh` CLI](https://cli.github.com/)
  installed and authenticated:
  ```bash
  gh auth login
  gh auth status
  ```
  Issues and PRs are created under the authenticated GitHub account —
  attributed to the user, not to Claude.

## Bootstrapping a project

Once the plugin is enabled, set up a project in two steps:

```text
/claudia understand    # writes .planning/CONTEXT.md + .planning/config.json
/claudia rules         # injects the Claudia Rules section into CLAUDE.md
```

`understand` only runs once (re-runnable as a refresh when the codebase
drifts). `rules` is idempotent — re-running it on the same repo
produces no diff.

## How invocation works

`/claudia` is the **only** command exposed by the plugin. It implements
two routing modes side-by-side:

1. **Explicit-verb route** — `/claudia <verb> [args]` invokes the
   matching skill directly. No NLP, no `AskUserQuestion` for
   disambiguation.
2. **Natural-language route** — `/claudia <free-form>` matches the
   intent against a keyword table. One match → invoke; many matches →
   ask the user; zero matches → fallback message + verb list.

The authoritative routing table lives in
[`skills/claudia/SKILL.md`](skills/claudia/SKILL.md). Some examples:

| Input | Routes to |
|---|---|
| `/claudia understand` | `claudia:understand` (explicit verb) |
| `/claudia plan 42` | `claudia:plan`, passing `42` as the issue ref |
| `/claudia close base:main` | `claudia:close`, passing `base:main` |
| `/claudia prepare-docstrings src/foo.py` | `claudia:prepare-docstrings` (dual-mode verb) |
| `/claudia let's start a new feature` | `claudia:plan` (NLP keyword match) |
| `/claudia test this` | ambiguous → `AskUserQuestion` between `python-testing` and `nextflow-testing` |

## Workflow verbs

| Verb | Skill | Purpose | Gate |
|---|---|---|---|
| `understand` | `claudia:understand` | One-time bootstrap → `.planning/CONTEXT.md` + `.planning/config.json`. Re-runnable as `refresh`. | summary (no formal gate) |
| `plan [issue-ref]` | `claudia:plan` | Intent + design + tasks in **one** plan file at `.planning/plans/YYYY-MM-DD-<slug>.md`. Optionally seeds intent from `gh issue view`. | **plan-accept** |
| `execute [T1 T2 …]` | `claudia:execute` | Implement plan tasks one at a time, ticking checkboxes in the plan file. Branches on `mode`. | per-commit (in `pair`) |
| `close [base:<branch>]` | `claudia:close` | Verify (parallel reviewer dispatch) + draft + open/hand off the PR. | **PR-accept** |

## Utility verbs

| Verb | Skill | Purpose |
|---|---|---|
| `rules` | `claudia:rules` | Inject the Claudia Rules section into the project's `CLAUDE.md` (idempotent, detect-aware). |
| `pr-review <ref>` | `claudia:pr-review` | Local-only structured PR review classified `URGENT`/`HIGH`/`MEDIUM`/`LOW`. **Never posts to GitHub.** |
| `write-issue <description>` | `claudia:write-issue` | Draft + create a GitHub issue, gated on user confirmation. |

## Content skills (auto-triggered)

These fire automatically when the model sees relevant context. The first
two are **dual-mode** — also callable as explicit verbs:

| Skill | Auto-triggered? | Callable verb? |
|---|---|---|
| `claudia:add-type-hints` | yes | `/claudia add-type-hints <path>` |
| `claudia:prepare-docstrings` | yes | `/claudia prepare-docstrings <path>` |
| `claudia:python-testing` | yes | — |
| `claudia:python-patterns` | yes | — |
| `claudia:nextflow-testing` | yes | — |
| `claudia:nextflow-patterns` | yes | — |

## Agents (`agents/`)

| Agent | Called by | Role |
|---|---|---|
| `planner` | `plan` skill | Task breakdown from intent + design. |
| `executor` | `execute` skill | Implement one task in a fresh context. |
| `verifier` | `close` skill | Orchestrates two-stage review; **dispatches reviewers in parallel**. |
| `researcher` | `plan`, `understand` skills | Read-only investigation. |
| `code-reviewer` | `verifier` (always) | General quality, security, maintainability. |
| `nextflow-reviewer` | `verifier` (conditional on `.nf` / `nextflow.config`) | Nextflow DSL2 production-readiness. |
| `domain-reviewer` | `verifier` (conditional on config + pipeline diff) | Bioinformatics output plausibility. |
| `pr-reviewer` | `pr-review` skill | Confidence-gated PR review (never posts). |
| `code-explorer` | `understand` skill (only when concrete dispatch triggers fire — see [skills/understand/SKILL.md](skills/understand/SKILL.md) step 3) | Deep architecture/call-chain trace. Complementary to `researcher`, not a substitute. |

## Rules (`rules/`)

`common/` and `python/` rule files. **Not auto-loaded by the plugin** —
consuming projects should run `/claudia rules` to inject the appropriate
subset into their `CLAUDE.md` as `@`-imports. The injector picks subsets
based on `claudia detect`:

| Project type | Subsets included |
|---|---|
| `python` | `common`, `python` |
| `nextflow` | `common`, `nextflow` (when the plugin ships one) |
| `mixed` | `common`, `python`, `nextflow` (when the plugin ships one) |
| `unknown` | `common` only |

To add a new rule, drop a `.md` file in the right subdirectory and add
its `@`-import to the [project's root CLAUDE.md](../../CLAUDE.md). The
`/claudia rules` injector will pick it up automatically.

## State — `.planning/`

Persists across sessions; agents reload it cold. Kept out of git by
default.

**Project-level** (written by `/claudia understand`):

- `CONTEXT.md` — codebase baseline plus a sentinel-bounded `## Environment` section managed by `claudia env capture --section`
- `config.json` — `{ mode, agents }`

**Per-task** (one file per task; previous tasks stay in place):

- `plans/YYYY-MM-DD-<slug>.md` — intent + decisions + checkbox task list + notes

That's it. There is no `STATE.md`, `VERIFICATION.md`, `ISSUE_BRIEF.md`,
`ROADMAP.md`, `DECISIONS.md`, or `ENVIRONMENT.md` in v2.

## Configuration — `config.json`

Created by `/claudia understand`. Schema:

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
| `mode` | `pair`, `yolo` | `pair` (default): executor stops after each task so you review and commit; close hands you the PR draft. `yolo`: executor commits autonomously following `commit-style`; close pushes and creates the PR via `gh`. |
| `agents.domain_reviewer` | `true`, `false` | Toggle the bioinformatics output reviewer for `/claudia close`. |
| `agents.nextflow_reviewer` | `true`, `false` | Toggle the Nextflow DSL2 reviewer for `/claudia close`. (Automatic on `.nf` diff regardless when `true`.) |

The **review gate** and the **secret scan** are not configurable —
they always run.

## Shared script — `scripts/claudia`

A single-file Python script (~250 LOC, stdlib-only). Invoked from skills
as `python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia <cmd>`. JSON-envelope
output by default (`{ok, data}` / `{ok, error}`); some commands accept
`--text` for human output.

| Subcommand | Purpose |
|---|---|
| `claudia detect [--root PATH] [--text]` | Report project type. |
| `claudia config init [--force]` / `get <key>` / `set <key> <value>` | Manage `.planning/config.json`. |
| `claudia env capture [--root PATH] [--section] [--text]` | Probe tool versions; with `--section`, rewrite the `## Environment` section of `.planning/CONTEXT.md`. |
| `claudia rules inject [--root PATH] [--path FILE] [--dry-run]` | Inject the `## Claudia Rules` section into `CLAUDE.md`. Idempotent, sentinel-bounded, detect-aware. |

## Safety model (GitHub)

- Read commands never mutate.
- Write commands always show a full draft and require explicit
  confirmation via `AskUserQuestion`. Editing the draft re-triggers the
  gate.
- `/claudia pr-review` and the `pr-reviewer` agent **never post to
  GitHub** — no comment, review, approval, merge, or label change.
  Output stays in chat.

## Install

Reference this repo as a marketplace and enable the `claudia` plugin in
Claude Code. The single `/claudia` command, every skill, and every agent
register automatically. Then in your project:

```text
/claudia understand
/claudia rules
```

That's the entire onboarding.
