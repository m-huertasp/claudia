# Workflow — discuss step

Surface design gray areas and record decisions in `.planning/DECISIONS.md`.

**This workflow is no longer user-invoked.** It runs as an internal step
of two parent workflows:

- **`intent` mode** — invoked from `/claudia-brief` after the brief is
  accepted. Focus: what we're tackling and why. Inputs: `ISSUE_BRIEF.md`
  + `CONTEXT.md`.
- **`approach` mode** — invoked from `/claudia-plan` after the ROADMAP.md
  draft is rendered. Focus: how we'll tackle it (sequencing, tradeoffs,
  risk, test strategy). Inputs: drafted `ROADMAP.md` + `ISSUE_BRIEF.md` +
  existing `DECISIONS.md` + `CONTEXT.md`. May trigger revisions to the
  `ROADMAP.md` draft.

Both modes append entries to the **same** `.planning/DECISIONS.md`. The
section header records the mode so later readers can tell intent
decisions from approach decisions.

## Steps

1. **Read inputs** appropriate for the mode (listed above).
2. **Find the gray areas:**
   - **intent** — scope edges, success criteria, "what does done mean",
     hidden constraints from `CONTEXT.md`.
   - **approach** — module layout, API shapes, data structures, error
     handling, edge cases, dependency choices, test strategy, phase
     sequencing.
3. **Ask, one cluster at a time** with `AskUserQuestion`. Present
   realistic options with trade-offs. Use a `researcher` agent for items
   that need investigation. Do not pick for the user.
4. **In `approach` mode**, if the discussion surfaces changes to the
   ROADMAP.md draft, apply them to the draft file before the gate.
5. **Draft decision entries** in the append-only template format
   (`question / decision / rationale / alternatives rejected`). The
   section header must be:
   ```
   ## <YYYY-MM-DD> — <intent | approach> — <phase / topic>
   ```

## Review gate

`DECISIONS.md` is **direction-locking**. Present the drafted entries
(and, in `approach` mode, any ROADMAP.md revisions) and ask
accept / edit / cancel via `AskUserQuestion`. Follow the file-based edit
loop in `plugins/claudia/rules/common/review-gate.md`. On accept:

1. Append the entries to `.planning/DECISIONS.md` (never rewrite existing
   accepted entries — supersede them with a new entry instead).
2. Record the gate clearance:
   ```
   claudia gate accept DECISIONS.md
   ```
3. Return control to the calling workflow (`/claudia-brief` or
   `/claudia-plan`), which is responsible for advancing the state
   machine. Do not set `last_command` / `next_step` here.

## Rules

- These are the user's decisions. Surface options; never decide for them.
- Stop when the question is specified well enough for the next step — do
  not over-discuss.
- Do not advance the state machine; the caller does.
