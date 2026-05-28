---
name: close
description: Close out a claudia task by running verification (two-stage review with parallel reviewer dispatch + secret scan + CONTEXT drift check), then drafting and gating a pull request. In `yolo` mode the PR is created via `gh`; in `pair` mode the title + body are printed for the user to open. Invoked via `/claudia close [base:<branch>]`. Do NOT auto-trigger; callable-only workflow skill.
---

# Close

> Invoke as: `/claudia close [base:<branch>]`

**Input**: `$ARGUMENTS` — optional `base:<branch>` override for the PR target.
Empty → default base from the repo remote (usually `main` or `master`).

---

## Purpose

Finish the task: verify the work, then open (or hand off) a pull
request. This single command covers verification (spec compliance +
parallel reviewer dispatch + automated tests + secret scan + drift
check), the fix loop, and the PR draft + accept gate + push +
create-or-handoff. Verification output goes to chat — nothing is
written to disk for it.

## Preconditions

1. The active plan file at `.planning/plans/YYYY-MM-DD-<slug>.md` has
   **every task ticked** (`- [x]`). If any task is still open, refuse
   and tell the user to finish or skip it via `/claudia execute`.
2. The branch has at least one commit ahead of the base. If not, stop
   and say there is nothing to ship.
3. `.planning/CONTEXT.md` and `.planning/config.json` exist.

## Read state and mode

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia config get mode
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia detect
```

If `mode` is missing or unreadable, treat it as `pair`. Read the
project type from `claudia detect` — it picks the automated-test
runner and the conditional reviewers.

## Verification

Dispatch the `verifier` agent. The verifier orchestrates two stages
and **must dispatch its reviewers in parallel**, not sequentially or
absorbed into a single review:

### Stage 1 — spec compliance

For each task ticked in the plan file: does the diff actually
implement what the task spec said? Does the "done when" hold? Any
out-of-scope changes? The verifier reads the plan file and the diff
against the base; it does not run code in this stage.

### Stage 2 — code quality (parallel dispatch)

The verifier dispatches the following reviewer agents **in parallel —
in a single model turn, emitting every applicable Agent tool call in
the same `tool_use` block**. Sequential calls (one reviewer per turn,
or chained "wait, then next") violate this contract:

| Reviewer | When |
|---|---|
| `code-reviewer` | **Always.** General quality, security, maintainability. |
| `nextflow-reviewer` | When `git diff --name-only <base>...HEAD` includes `*.nf` or `nextflow.config`. |
| `domain-reviewer` | When `python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia config get agents.domain_reviewer` returns `true` AND the diff includes pipeline outputs (any `.nf`, `nextflow.config`, or data-producing scripts). |

Each reviewer returns findings classified `CRITICAL` / `HIGH` /
`MEDIUM` / `LOW`. Do not collapse their reports into one — surface
each reviewer's findings under its own heading.

### Automated tests

Branch the test runner on the `type` from `claudia detect`:

- `python` → `uv run pytest` (or `pytest` if `uv` is not on PATH).
  Also run `ruff check .` and `mypy` if configured.
- `nextflow` → `nf-test test` against any bundled test profile.
  Run `nextflow lint` if installed.
- `mixed` → run both runners.
- `unknown` → ask the user how to verify; do not invent a runner.

A red test suite blocks the close.

### Secret scan

Mandatory and not skippable. Scan the branch diff for hardcoded
secrets per [security.md](../../rules/common/security.md). Stop on any
finding.

### CONTEXT.md drift check

Compare changed paths against `.planning/CONTEXT.md`:

- New top-level directory not mentioned in CONTEXT.md
- New dependency in `pyproject.toml` / `nextflow.config` not listed
- A key file mentioned in CONTEXT.md was renamed or deleted

If drift is detected, ask via `AskUserQuestion`:

- *Refresh CONTEXT.md now* — run `/claudia understand refresh`, then
  resume.
- *Continue, note in PR* — proceed but mention the drift in the PR
  body's "What to review" section.
- *Stop.*

### Fix loop

If any reviewer surfaced `CRITICAL` or `HIGH` findings, or tests
failed, branch on mode:

- **`yolo`** — `AskUserQuestion`: *fix now (executor)* /
  *accept with warnings* / *stop*.
- **`pair`** — `AskUserQuestion`: *fix now (executor)* /
  *fix now (I'll fix it myself)* / *accept with warnings* / *stop*.

On *fix now (executor)*, dispatch the `executor` agent with the
findings as fix tasks; loop back to verification. Cap the loop at
**3 attempts**. After the 3rd failed verification, surface an
escalation prompt:

- *Accept with warnings* (still blocked on `CRITICAL`)
- *Stop*
- *Override and try once more*

`CRITICAL` findings always block, regardless of mode.

## Draft PR

On a passing verification:

### Gather the change

```bash
git branch --show-current
git remote -v
git log <base>..HEAD --oneline
git diff <base>...HEAD --stat
git diff <base>...HEAD
```

Group the change into themes (feature, fix, refactor).

### Compose the draft — FIXED structure

**Title:** one line, imperative, under 70 chars, with a
[`commit-style`](../../rules/common/commit-style.md) `{type}:` prefix.

**Body:**

```markdown
## What this does
<2–4 sentences, plain language. Lead with the main feature/fix. Say why, not just what.>

## Changes
- <one bullet per meaningful change; collapse formatting/rename noise into one bullet>

## What to review
<1–3 bullets pointing reviewers at parts that need real attention. If trivial,
say "Straightforward — no specific concerns.">

## Testing
<How it was verified. If untested, say so plainly.>
```

Rules:

- Human voice in "What this does" — not a changelog paraphrase.
- "What to review" must be honest — surface shaky or undertested areas.
- Never invent a test plan.

### Present + accept gate

Show in chat: target repo, base ← head, title, full body, whether the
branch still needs pushing.

`AskUserQuestion`:

- **`yolo`** — *Accept and create the PR* / *Edit first* / *Cancel*.
- **`pair`** — *Accept — I'll open it myself* / *Edit first* / *Cancel*.

Never push or call `gh pr create` before explicit accept.

### Create or hand off

On accept, push the branch in both modes (the user needs a remote ref
even when opening via the web UI):

```bash
git push -u origin <branch>
```

Call out the push explicitly.

- **`yolo`** — open the PR:
  ```bash
  gh pr create --base <base> --head <head> --title "<title>" \
      --body-file - <<'EOF'
  <body markdown>
  EOF
  ```
  Report the new PR URL.

- **`pair`** — print the final title verbatim, the body inside a
  fenced code block, a ready-to-run `gh pr create` line, and the
  compare-view URL
  (`https://github.com/<owner>/<repo>/compare/<base>...<head>?expand=1`).
  Do not call `gh pr create`.

## Rules

- The verifier must dispatch reviewers **in parallel** — every
  applicable reviewer issued as Agent tool calls in the same
  `tool_use` block of one model turn. Never one-per-turn, never
  chained.
- `CRITICAL` findings always block — no override.
- The secret scan is mandatory and is not configurable.
- `yolo` requires `gh` authenticated via `gh auth login`. If `gh`
  exits with an auth error, tell the user to run `gh auth login`
  rather than retrying.
- Acceptance is mandatory in both modes — never push or create
  before an explicit accept.
- This skill never merges, comments, or reviews other PRs — use
  `/claudia pr-review` for review.
