---
description: Start a claudia project — gather vision and scope, build a phased roadmap, and initialize the .planning/ state files and config. Roadmap is created only after the user accepts it.
---

# Start a project

The user wants to begin a project under the `claudia` workflow. Produce
`PROJECT.md`, `ROADMAP.md`, and `config.json` in `.planning/`.

Argument: `$ARGUMENTS` — optional one-line description of the project.

## Steps

1. **Ensure `.planning/` exists** and is gitignored (unless opted in). If
   `CONTEXT.md` already exists from `/claudia-map`, read it — use it to ask
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
   `/claudia-discuss`.

## Review gate

`ROADMAP.md` is **direction-locking**. Present the drafted `PROJECT.md` and
`ROADMAP.md`, then use `AskUserQuestion`: **accept**, **edit**, or **cancel**.
On **edit**, follow the review-gate rule's file-based edit loop — write the
drafts to `.planning/PROJECT.md` and `.planning/ROADMAP.md`, surface them so
the user edits them in place, then re-read and re-present. The files are final
only on accept; on cancel, delete the drafts.

## Rules

- Follow the review-gate rule for the roadmap. A draft file written during an
  edit loop is not acceptance — do not treat `ROADMAP.md` as final before an
  explicit accept.
- One project per `.planning/` directory. If state files already exist, ask
  before overwriting.
