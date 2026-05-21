# Workflow — `/claudia-discuss`

Surface design gray areas for the upcoming phase and record decisions in
`.planning/DECISIONS.md`.

Argument: `$ARGUMENTS` — optional phase number or topic. Empty means: the
current phase.

## Steps

1. **Read context.** Resolve the current phase:
   ```
   claudia phase current
   claudia state get
   ```
   Then read `ROADMAP.md`, `CONTEXT.md`, and existing `DECISIONS.md`.
2. **Find the gray areas** — module layout, API shapes, data structures,
   error handling, edge cases, dependency choices.
3. **Ask, one cluster at a time** with `AskUserQuestion`. Present realistic
   options with trade-offs. Use a `researcher` agent for items that need
   investigation. Do not pick for the user.
4. **Draft decision entries** in the append-only format from the template
   (`question / decision / rationale / alternatives rejected`).

## Review gate

`DECISIONS.md` is **direction-locking**. Present the drafted entries and ask
accept / edit / cancel via `AskUserQuestion`. Follow the file-based edit
loop in `plugins/claudia/rules/common/review-gate.md`. On accept:

1. Append the entries to `.planning/DECISIONS.md` (never rewrite existing
   accepted entries — supersede them with a new entry instead).
2. Record the gate clearance:
   ```
   claudia gate accept DECISIONS.md
   ```
3. Advance state:
   ```
   claudia state set last_command /claudia-discuss
   claudia state set next_step /claudia-plan
   ```

## Rules

- These are the user's decisions. Surface options; never decide for them.
- Stop when the phase is specified well enough to plan — do not
  over-discuss.
