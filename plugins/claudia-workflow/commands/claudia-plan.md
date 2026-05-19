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

The task breakdown is **direction-locking**. Present the full ordered list
with specs and dependencies, then ask **accept / edit / cancel**. Apply edits
per the review-gate rule — verbatim rewrites used as given — and re-present.
Write the tasks into `STATE.md` only on accept.

## Rules

- Tasks must be small and independently verifiable — sized for one executor
  and one verifier pass.
- Mark independent tasks; they are eligible for parallel execution only if
  `execution.parallel` is enabled.
- Update `STATE.md`: next step = `/clavia-execute`.
