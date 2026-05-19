---
description: Start a clavia project — gather vision and scope, build a phased roadmap, and initialize the .planning/ state files and config. Roadmap is created only after the user accepts it.
---

# Start a project

The user wants to begin a project under the `clavia` workflow. Produce
`PROJECT.md`, `ROADMAP.md`, and `config.json` in `.planning/`.

Argument: `$ARGUMENTS` — optional one-line description of the project.

## Steps

1. **Ensure `.planning/` exists** and is gitignored (unless opted in). If
   `CONTEXT.md` already exists from `/clavia-map`, read it — use it to ask
   stack-aware questions instead of generic ones.
2. **Gather vision and scope.** Ask the user, with `AskUserQuestion` where
   choices are discrete: what the project is, why it exists, what is in and
   out of scope, success criteria. Do not pad thin answers with guesses — ask
   again.
3. **Choose configuration.** Confirm `mode`, `model_profile`, and agent
   toggles. Copy `config.template.json` to `.planning/config.json` with the
   chosen values.
4. **Draft `PROJECT.md`** from the template.
5. **Draft `ROADMAP.md`** from the template — break the work into phases, each
   a shippable unit.
6. **Initialize `STATE.md`** — current phase = Phase 1, next step =
   `/clavia-discuss`.

## Review gate

`ROADMAP.md` is **direction-locking**. Present the full drafted `PROJECT.md`
and `ROADMAP.md`, then use `AskUserQuestion`: **accept**, **edit**, or
**cancel**. Apply edits per the review-gate rule — verbatim rewrites used as
given — and re-present. Write the files only on accept.

## Rules

- Follow the review-gate rule for the roadmap. Do not write `ROADMAP.md`
  before an explicit accept.
- One project per `.planning/` directory. If state files already exist, ask
  before overwriting.
