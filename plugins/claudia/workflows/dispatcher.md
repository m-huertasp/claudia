# /claudia — dispatcher workflow

Parse `$ARGUMENTS` as a free-form intent and route to the right skill or
workflow command. The dispatcher is the primary entry point into the
framework; direct slash commands still work for users who already know them.

## How to route

1. **Read `$ARGUMENTS`** — strip leading filler words (e.g. "please",
   "Claudia,") and treat the rest as the intent string. If `$ARGUMENTS` is
   empty, fall back to `/claudia-progress`.
2. **Match against the routing table below.** A match is keyword-based and
   case-insensitive. Count matches:
   - **Exactly one** → invoke the target immediately (see "Invocation rules").
   - **Two or more** → use `AskUserQuestion` to surface the candidates and
     let the user pick. Never silently choose. This honours the control-first
     review-gate philosophy.
   - **Zero** → tell the user no intent matched, then fall back to
     `/claudia-progress` so they see where they are in the workflow.
3. **Pass remaining arguments through.** Anything in `$ARGUMENTS` that isn't
   an intent keyword is forwarded to the target (e.g. file path, phase
   number, PR reference).

## Routing table

| Intent keywords (any match) | Target | Notes |
|---|---|---|
| `docstrings`, `document`, `numpy format`, `scipy format` | Skill `claudia:prepare-docstrings` | Pass file path |
| `type hint`, `type hints`, `annotate`, `typing`, `mypy` | Skill `claudia:add-type-hints` | Pass file path |
| `write tests`, `add tests`, `pytest`, `tdd`, `coverage` | Skill `claudia:python-testing` | Pass file/dir |
| `python pattern`, `decorator`, `dataclass`, `paramspec` | Skill `claudia:python-patterns` | |
| `nextflow`, `dsl2`, `.nf`, `channel` | Skill `claudia:nextflow-patterns` | |
| `nf-test`, `nftest`, `pipeline test` | Skill `claudia:nextflow-testing` | |
| `map`, `map codebase`, `explore repo`, `analyze codebase` | `/claudia-map` | |
| `start project`, `new project`, `roadmap`, `init project` | `/claudia-new` | |
| `discuss`, `design decision`, `decisions` | `/claudia-discuss` | |
| `plan`, `task breakdown`, `break down` | `/claudia-plan` | |
| `execute`, `implement task`, `run task` | `/claudia-execute` | |
| `verify`, `review gate`, `secret scan`, `check work` | `/claudia-verify` | |
| `ship`, `open pr`, `pull request`, `create pr` | `/claudia-ship` | |
| `progress`, `status`, `where am i`, `next step` | `/claudia-progress` | |
| `settings`, `config` | `/claudia-settings` | |
| `file issue`, `github issue`, `open issue`, `write issue` | `/claudia-write-issue` | |
| `draft pr`, `pr draft` | `/claudia-draft-pr` | |
| `review pr`, `pr review` | `/claudia-pr-review` | Pass `<num\|owner/repo#num\|url>` |

## Invocation rules

- **Skill target** — call the `Skill` tool with `skill: claudia:<name>` and
  pass through `$ARGUMENTS` (minus the intent keyword) as `args`.
- **Command target** — instruct the model to follow the workflow file the
  command points at, with the remaining `$ARGUMENTS` forwarded. Do not
  literally re-invoke a slash command from inside this workflow; read its
  pointer (`commands/<name>.md` → `workflows/<name>.md`) and execute that
  workflow directly.

## Ambiguity examples

- `"Claudia, test this"` matches both `claudia:python-testing` and
  `claudia:nextflow-testing`. Surface both via `AskUserQuestion`; let the
  user choose.
- `"Claudia, plan it"` after a clean checkout might mean `/claudia-plan` or
  `/claudia-new`. Ask which.
- A bare verb with no object (e.g. `"Claudia, run"`) is ambiguous between
  `/claudia-execute` and others. Ask.

## Fallback

- Zero matches → say so plainly, then route to `/claudia-progress` so the
  user sees the current workflow state.
- If `$ARGUMENTS` is empty → `/claudia-progress` (no message needed).

## Rules

- **Never bypass the review gate.** The dispatcher only routes; the target
  workflow's own gates still apply (e.g. `/claudia-ship` still calls
  `claudia gate check` and `claudia verify ready`).
- **Never invent a target.** If a request doesn't match any keyword, do not
  guess — surface the fallback message.
- **Respect skill autonomy.** Once a skill is invoked, follow that skill's
  instructions; do not graft dispatcher logic onto it.
