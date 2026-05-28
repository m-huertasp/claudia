---
name: claudia
description: Dispatcher for the claudia framework — routes `/claudia <verb> [args]` to the matching skill (explicit-verb mode) or, when the first token is not a known verb, falls through to natural-language routing against a keyword table. The only command the plugin exposes; all other claudia capabilities live behind this entry point. Fires **only** when the user invokes `/claudia` — do not auto-trigger this skill from context.
---

# claudia (dispatcher)

> Invoke as: `/claudia [<verb> [args]] | <free-form request>`

**Input**: `$ARGUMENTS` — empty, an explicit verb, or free-form natural
language.

---

## Purpose

`/claudia` is the **only** command exposed by the plugin. Every
capability — workflow skills like `understand`/`plan`/`execute`/`close`,
the utility `rules`, the actionable content skills `add-type-hints` and
`prepare-docstrings`, and the GitHub helpers `pr-review` and
`write-issue` — lives behind this single entry point.

## Routing

The dispatcher implements two routing modes side-by-side, in this
order:

### 1. Explicit-verb route

If the first whitespace-separated token of `$ARGUMENTS` matches a
known verb from the table below, invoke that skill directly with the
remaining arguments. No NLP, no `AskUserQuestion` for disambiguation.

| Verb | Skill | Notes |
|---|---|---|
| `understand` | `claudia:understand` | Forward the rest of `$ARGUMENTS` as a focus hint or `refresh`. |
| `plan` | `claudia:plan` | Forward optional `issue-ref` (`123`, `owner/repo#123`, URL). |
| `execute` | `claudia:execute` | Forward optional task IDs (`T1 T2 ...`). |
| `close` | `claudia:close` | Forward optional `base:<branch>`. |
| `rules` | `claudia:rules` | No args. |
| `pr-review` | `claudia:pr-review` | Forward `<num \| owner/repo#num \| url>`. |
| `write-issue` | `claudia:write-issue` | Forward the issue description. |
| `add-type-hints` | `claudia:add-type-hints` | Forward the file path. Dual-mode: also auto-triggers. |
| `prepare-docstrings` | `claudia:prepare-docstrings` | Forward the file path. Dual-mode: also auto-triggers. |

The list of known verbs lives in this file and is the single source
of truth. Adding a new callable skill means appending a row here.

### 2. Natural-language route (fallback)

If the first token is **not** in the verb table, treat `$ARGUMENTS`
as a free-form intent and match against the keyword table below.
Strip leading filler ("please", "Claudia,") first.

| Intent keywords (any match) | Target skill |
|---|---|
| `docstrings`, `document this`, `numpy format`, `scipy format`, `format docstring` | `claudia:prepare-docstrings` |
| `type hint`, `type hints`, `annotate`, `typing`, `mypy` | `claudia:add-type-hints` |
| `write tests`, `add tests`, `pytest`, `tdd`, `coverage` | `claudia:python-testing` |
| `python pattern`, `decorator`, `dataclass`, `paramspec`, `python idiom`, `best practices python` | `claudia:python-patterns` |
| `nextflow`, `dsl2`, `.nf`, `channel`, `nf-core` | `claudia:nextflow-patterns` |
| `nf-test`, `nftest`, `pipeline test` | `claudia:nextflow-testing` |
| `understand`, `map codebase`, `explore repo`, `analyze codebase`, `bootstrap`, `survey codebase`, `onboard` | `claudia:understand` |
| `plan`, `roadmap`, `task breakdown`, `break down`, `new issue`, `start issue`, `tackle` | `claudia:plan` |
| `execute`, `implement task`, `run task` | `claudia:execute` |
| `verify`, `review gate`, `secret scan`, `check work`, `close`, `wrap up`, `ship`, `open pr`, `pull request`, `create pr` | `claudia:close` |
| `rules`, `inject rules`, `add rules`, `claude md`, `setup rules` | `claudia:rules` |
| `file issue`, `github issue`, `open issue`, `write issue` | `claudia:write-issue` |
| `review pr`, `pr review` | `claudia:pr-review` |

Match counting:

- **Exactly one** target → invoke it. Pass through `$ARGUMENTS` as
  `args` (minus the matched keyword if it is the first token).
- **Two or more** targets → surface the candidates via
  `AskUserQuestion` and let the user pick. This is a **routing
  disambiguation**, not a clarifying question about the model's task,
  so it is **not** suppressed by auto-mode or by instructions to "make
  the reasonable call". The user is the principal here: which skill
  runs next is the user's decision because the choice changes which
  files get edited, which agents fire, and what the gate at the end
  asks. Picking silently can run the wrong skill and waste the user's
  time recovering. When in doubt between two skills, ask.
- **Zero matches** → tell the user no intent matched and print the
  available verbs.

## Empty input

If `$ARGUMENTS` is empty, print:

1. The list of available explicit verbs (from the table above).
2. The current branch (`git rev-parse --abbrev-ref HEAD`).
3. The current `mode` (`python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia config get mode`).
4. The most recent plan file in `.planning/plans/` if any.

This is the "where am I?" view — a read-only snapshot of the current
workflow state.

## Invocation mechanics

- **Skill target** — call the `Skill` tool with
  `skill: claudia:<name>` and pass the remaining `$ARGUMENTS` as
  `args`.
- **Never re-invoke `/claudia` recursively.** Routes resolve to
  skills, not back to this dispatcher.

## Ambiguity examples

- `"write tests for this"` on a mixed repo — matches
  `claudia:python-testing` (via `write tests`); if the file in
  context is `.nf` the user likely wants `claudia:nextflow-testing`
  instead. Ask which.
- `"plan it"` on a clean checkout — `claudia:plan` is the only
  match; route directly.
- `"implement the plan we agreed on"` — matches both `implement task`
  (`claudia:execute`) AND `plan` (`claudia:plan`). The phrasing
  *sounds* like it should be `execute`, but that's the model's
  reading, not the user's. Ask: do they want to plan (re-open
  design) or execute (run the existing plan)? Picking for them is
  exactly the silent-routing failure mode this section warns against.
- `"discuss this"` — not a target. Surface no match and offer
  `claudia:plan` (which covers intent + design discussion).
- `"run"` with no object — ambiguous. Ask.

## Rules

- **Explicit-verb wins.** If the first token is a known verb, never
  re-interpret it as NLP. This guarantees `/claudia plan 42` always
  invokes the planner with `42` as the issue ref, regardless of
  what other keywords appear later.
- **Never bypass the review gate.** The dispatcher only routes; the
  target skill's own gates still apply.
- **Never invent a target.** Zero matches → fallback message and the
  verb list. Do not guess.
- **Respect skill autonomy.** Once a skill is invoked, follow that
  skill's instructions; do not graft dispatcher logic onto it.
- The auto-triggered content skills (`python-testing`,
  `python-patterns`, `nextflow-testing`, `nextflow-patterns`) fire
  on their own when the model sees relevant context. The dispatcher
  is not required to invoke them — but the NLP table above lists
  them so the user can be explicit.
- The dual-mode skills (`add-type-hints`, `prepare-docstrings`) are
  both auto-triggered (via their descriptions) AND callable here.
  Either entry point produces the same result.
