---
description: Turn the current roadmap phase into an ordered breakdown of small, verifiable tasks — using research and recorded decisions — then lock it into STATE.md only after the user accepts.
---

# Plan the phase

The user wants a concrete task breakdown for the current phase. Output: the
**Open tasks** list in `.planning/STATE.md`.

Argument: `$ARGUMENTS` — optional phase number. If empty, use the current
phase from `STATE.md`.

## Steps

1. **Read context** — `STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `CONTEXT.md`.
2. **Research** what the plan needs. If `agents.researcher` is enabled in
   `config.json`, dispatch `researcher` agents for open questions; otherwise
   investigate directly.
3. **Plan.** If `agents.planner` is enabled, dispatch the `planner` agent with
   the phase, decisions, and research briefs. Otherwise build the breakdown
   directly. Each task: ID, title, spec, depends-on, "done when".
4. **Flag guesswork.** If the planner flagged a task it could not specify,
   raise it with the user — do not let it through.

## Review gate

The task breakdown is **direction-locking**. Present the ordered list with
specs and dependencies, then ask **accept / edit / cancel**. On **edit**,
follow the review-gate rule's file-based edit loop — write the tasks into the
**Open tasks** section of `.planning/STATE.md`, surface the file so the user
edits them in place, then re-read and re-present. The breakdown is final only
on accept; on cancel, remove the draft tasks.

## Rules

- Tasks must be small and independently verifiable — sized for one executor
  and one verifier pass.
- Mark independent tasks; they are eligible for parallel execution only if
  `execution.parallel` is enabled.
- Update `STATE.md`: next step = `/claudia-execute`.
