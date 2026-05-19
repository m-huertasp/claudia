# claudia

> A personal, Claude Code framework for Python and Nextflow development.

---

## What this is

**claudia** is a Claude Code framework. It gives a phased development
**workflow** — map, discuss, plan, execute, verify, ship — backed by reusable
agents, rules, and skills. It works with Claude Code in VS Code, and the rules
are written to hold for any AI model.

Two principles run through everything:

- **Control-first.** Every direction-locking artifact (roadmap, plan, design
  decisions) and every outward action (issues, PRs, pushes) passes through a
  **review gate**: drafted, shown in full, and acted on only after you accept.
  "Edit" means you can rewrite anything — your text is used verbatim.
- **Safe to share.** The rules are model-agnostic and include guardrails for
  using AI on lab repositories — no secrets, no unpublished research data, a
  secret scan before anything is published.

---

## The workflow — `claudia-workflow` plugin

Explicit-command workflow. State persists in `.planning/` so
work resumes cold across sessions.

| Command | Phase |
|---|---|
| `/claudia-map` | Analyze an existing codebase → `CONTEXT.md` |
| `/claudia-new` | Start a project, build the roadmap |
| `/claudia-discuss` | Pin down design decisions before planning |
| `/claudia-plan` | Research + ordered task breakdown |
| `/claudia-execute` | Implement tasks via executor subagents (sequential by default) |
| `/claudia-verify` | Two-stage review + secret scan |
| `/claudia-ship` | Open a PR (via `gh-workflow`) |
| `/claudia-progress` | Where things stand / next step |
| `/claudia-settings` | View or edit `.planning/config.json` |

Four agent roles — `researcher`, `planner`, `executor`, `verifier` — each run
in a fresh context. See [plugins/claudia-workflow/README.md](plugins/claudia-workflow/README.md).

---

## Folder structure

```
claudia/
├── CLAUDE.md                        # Global Claude Code instructions (auto-loaded per project)
├── .claude/
│   ├── agents/                      # Subagent definitions (code-explorer, code-reviewer)
│   ├── rules/                       # Conventions — common/ (incl. review-gate, secure-ai-use) 
│   └── skills/                      # Skills, invokable as /<skill-name>
├── plugins/
│   ├── claudia-workflow/             # The phased development workflow
│   └── gh-workflow/                 # GitHub issue / PR commands
├── docs/                            # docs/INDEX.md — architecture overview
└── README.md                        # This file
```

---

## Skills

Invokable as `/<skill-name>`, or triggered automatically when relevant.

| Skill | Purpose |
|---|---|
| `/prepare-docstrings <file>` | Add or rewrite docstrings in NumPy/SciPy format |
| `/add-type-hints <file>` | Infer and add type annotations; asks when uncertain |
| `/python-testing <path>` | Write pytest tests using TDD |
| `/python-patterns` | Non-obvious Python patterns |
| `/nextflow-patterns` | Production-ready Nextflow DSL2 habits |
| `/nextflow-testing` | Nextflow pipeline testing with nf-test |
| `/claudia-new-skill` | Author a new skill following repo conventions |

---

## Agents

| Agent | Purpose |
|---|---|
| `code-explorer` | Deep codebase exploration — traces execution paths, maps architecture |
| `code-reviewer` | Security, correctness, and quality review |
| `researcher` / `planner` / `executor` / `verifier` | The four `claudia-workflow` roles |

---

## Plugins

### `claudia-workflow` — `plugins/claudia-workflow/`

The phased development workflow. See above and the plugin README.

### `gh-workflow` — `plugins/gh-workflow/`

GitHub automation. Requires the official `github` MCP plugin and
`GITHUB_PERSONAL_ACCESS_TOKEN`. Every write action is gated behind explicit
confirmation. See [plugins/gh-workflow/README.md](plugins/gh-workflow/README.md).

| Command | Purpose |
|---|---|
| `/gh-issue [owner/repo:] <description>` | Draft and create a structured issue (gated) |
| `/gh-my-issues [filters]` | List issues assigned to me |
| `/gh-my-prs [filters]` | List my PRs |
| `/gh-pr-draft [base:branch]` | Draft and create a PR (gated) |
| `/gh-pr-review <num\|url>` | Structured PR review — never posts to GitHub |

---

## Documentation

Architecture overview: **[docs/INDEX.md](docs/INDEX.md)**.
