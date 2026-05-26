---
name: plan
description: Start work on a new issue or task in the claudia framework — produce a task breakdown / roadmap by gathering intent (optionally seeded from a GitHub issue via `gh issue view`), capturing design decisions, proposing a `{keyword}/{description}` branch, and writing a single per-task plan file with an ordered checkbox task list. Invoked via `/claudia plan [issue-ref]`. Use whenever the user says they want to plan, tackle, scope, or start an issue or new feature, or asks for a roadmap or task breakdown. Do NOT auto-trigger; callable-only workflow skill.
---

# Plan

> Invoke as: `/claudia plan [issue-ref]`

**Input**: `$ARGUMENTS` — optional GitHub issue reference. One of:
- `123` — issue number in the current repo
- `owner/repo#123` — cross-repo
- A full URL (e.g. `https://github.com/owner/repo/issues/123`)

No argument → gather intent interactively via `AskUserQuestion`.

---

## Purpose

Replace the old `brief → discuss(intent) → plan → discuss(approach)` chain
with a single command that produces **one plan file** per task:

```
.planning/plans/YYYY-MM-DD-<slug>.md
```

The file has four sections — Intent, Design decisions, Tasks, Notes —
and is the only direction-locking artefact for the task. Execution
state lives in TodoWrite + the checkboxes inside `## Tasks`. There is
no separate ISSUE_BRIEF / ROADMAP / DECISIONS / STATE file.

## Preconditions

Check both before doing anything else. Run the checks explicitly and
short-circuit on failure — do not gather intent until both pass.

1. `.planning/CONTEXT.md` must exist (`test -f .planning/CONTEXT.md`).
   If not, refuse and tell the user to run `/claudia understand` first.
   Do NOT create the file, do NOT propose a branch, do NOT draft a plan.
2. The working tree must be clean (`git status --porcelain` empty). If
   not, tell the user to commit or stash before continuing.

## Steps

### 1. Gather intent

**If an `issue-ref` was given:**

Fetch the issue via the GitHub CLI:

```bash
gh issue view <issue-ref> --json title,body,labels,comments
```

Parse the returned JSON. Use the issue title + body to seed:
- **Goal** — derived from the title and the opening paragraph
- **Constraints** — anything explicit in the body or labels
- **Acceptance criteria** — bullets the issue lists, or inferred from
  the description
- **Source** — the canonical issue ref (`owner/repo#123`)

Present the extracted intent to the user via `AskUserQuestion` and let
them confirm or amend each field before continuing. Do not silently
guess where the issue is thin — surface `<unknown — needs human input>`
placeholders for the user to fill.

**If no `issue-ref` was given:**

Drive intent capture with exactly **five** `AskUserQuestion` clusters,
one per field, in this order:

1. Issue type — `feature` / `bugfix` / `refactor` / `docs` / `chore`
2. Goal — one or two sentences
3. Constraints — anything that must be honoured (free-text; `none` is allowed)
4. Out of scope — anything explicitly excluded (free-text; `none` is allowed)
5. Acceptance criteria — concrete, testable bullets

Do not pad thin answers with guesses. Do not collapse the five clusters
into a single mega-prompt — each field gets its own question so the user
can answer them one at a time.

### 2. Propose the branch

Branch name follows `{keyword}/{branch-description}`:

| Issue type | Inferred keyword |
|---|---|
| `feature`  | `feat`  |
| `bugfix`   | `fix`   |
| `refactor` | `dev`   |
| `docs`     | `chore` |
| `chore`    | `chore` |

`hotfix` is opt-in only — the user must override to use it. The
`{branch-description}` is a kebab-case slug derived from the goal
or the issue title.

1. Detect the current branch with `git rev-parse --abbrev-ref HEAD`.
   If it already matches `{keyword}/{description}` with a valid
   keyword, it is reusable.
2. Propose the branch via `AskUserQuestion`. If the current branch is
   reusable, also offer *Use current branch (`<name>`)*. If the
   parsed keyword conflicts with the gathered issue type, flag the
   mismatch and ask the user to resolve it.
3. On confirmation:
   - *Use current branch* — do not run `git checkout`.
   - Otherwise — `git checkout -b <keyword>/<description>` from the
     current base.

### 3. Investigate (if needed)

Identify open questions about *approach*: module layout, API shapes,
data flow, error handling, test strategy, dependency choices.

For each open question, decide whether to:
- **Investigate via `researcher` agent** — read-only survey of relevant
  code, returns a brief.
- **Ask the user via `AskUserQuestion`** — present realistic options
  with trade-offs. Do not pick for the user.

Repeat until the design decisions are concrete enough to break into
tasks.

### 4. Draft the task list

Dispatch the `planner` agent. Inputs to the agent:
- The gathered intent
- The design decisions from step 3
- `.planning/CONTEXT.md`

The planner returns an ordered list of tasks. Each task must be:
- Small enough for one executor pass
- Independently verifiable (clear "done when")
- Specified with title + one-line spec

Flag any task the planner could not specify cleanly — raise it with
the user rather than letting guesswork through.

### 5. Write the plan file

Compose the plan file at `.planning/plans/YYYY-MM-DD-<slug>.md`,
where `<slug>` is the kebab-case form of the goal (≤ 50 chars).

Format:

```markdown
# <slug>

## Intent
- **Goal:** <one or two sentences>
- **Constraints:**
  - <constraint>
- **Out of scope:**
  - <item>
- **Acceptance criteria:**
  - <criterion>
- **Source:** <github-issue-ref | "manual">

## Design decisions
- <decision> — <one-line rationale>

## Tasks
- [ ] T1 — <title>: <spec>
- [ ] T2 — <title>: <spec>

## Notes
<free-form, optional>
```

Tasks use checkboxes; `/claudia execute` ticks them on disk as each
task is completed. Use stable IDs (`T1`, `T2`, …) so later notes can
reference them.

### 6. Review gate

The plan file is **direction-locking**. Present it and ask
accept / edit / cancel via `AskUserQuestion`, following the
file-based edit loop in
[review-gate.md](../../rules/common/review-gate.md):

- **Accept** — keep the file as written; the task is ready for
  `/claudia execute`.
- **Edit** — the file is already on disk; tell the user it is open
  for editing. Wait for their signal that editing is done, re-read
  the file, re-present the gate.
- **Cancel** — delete the draft file and stop. Do not advance any
  state.

On accept, print a one-line summary and suggest `/claudia execute` as
the next step.

## Rules

- Tasks must be small and independently verifiable — sized for one
  executor and one verifier pass.
- Do not silently fall back on guesses when an issue body is thin —
  surface `<unknown>` placeholders for the user to fill.
- The plan file is the only direction-locking artefact. No
  `STATE.md`, no `DECISIONS.md`, no `ROADMAP.md`.
- Never overwrite an accepted plan. If the scope shifts mid-task,
  archive the existing plan to `.planning/plans/archive/` and
  re-run `/claudia plan`.
