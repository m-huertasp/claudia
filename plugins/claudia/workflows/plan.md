# Workflow — `/claudia-plan`

Draft a per-issue `ROADMAP.md` from the accepted `ISSUE_BRIEF.md`
(refined by intent-mode discuss into `DECISIONS.md`), then chain into the
**approach-mode** discuss step to align on how we'll tackle it, then
initialize `.planning/STATE.md` with the phase-1 task breakdown.

Argument: `$ARGUMENTS` — optional focus hint. Empty means: plan the
whole issue.

## Preconditions

1. `.planning/ISSUE_BRIEF.md` must exist — if not, refuse and tell the
   user to run `/claudia-brief` first.
2. `.planning/CONTEXT.md` must exist — if not, refuse and tell the user
   to run `/claudia-understand` first.

## Steps

1. **Read inputs.**
   ```
   claudia config get agents.researcher
   claudia config get agents.planner
   ```
   Then read `ISSUE_BRIEF.md`, `DECISIONS.md` (intent-mode entries),
   `CONTEXT.md`.
2. **Research** what the plan needs. If `agents.researcher` is enabled,
   dispatch `researcher` agents for open questions; otherwise investigate
   directly.
3. **Draft `ROADMAP.md`.** Render the template:
   ```
   claudia template render ROADMAP \
       --var name=<issue-title> --output .planning/ROADMAP.md
   ```
   Replace the example phases with the real ones for this issue. Every
   phase's `**Status:**` line must wrap its value in
   `<!-- claudia:status-N -->...<!-- /claudia:status-N -->` so
   `claudia phase set-status` can transition it. If `agents.planner` is
   enabled, dispatch the `planner` agent to produce the phase breakdown
   from the brief + decisions + context.
4. **Chain into discuss (approach mode).** Follow
   `plugins/claudia/workflows/discuss.md` with mode `approach`:
   - Inputs: drafted `ROADMAP.md` + `ISSUE_BRIEF.md` + `DECISIONS.md` +
     `CONTEXT.md`
   - Focus: sequencing, tradeoffs, risk areas, test strategy
   - Output: a new `## <date> — approach — <topic>` section appended to
     `.planning/DECISIONS.md`; ROADMAP.md draft revised in place if the
     discussion changes it.
5. **Plan phase-1 tasks.** With the ROADMAP.md now stable, break down
   phase 1 into small, verifiable tasks. Each task needs an ID, title,
   spec, depends-on, and "done when". Flag any task the planner could
   not specify and raise it with the user — do not let guesswork through.

## Review gate

The `ROADMAP.md` draft is presented and gated **before** initializing
`STATE.md`. Use `AskUserQuestion` for accept / edit / cancel and follow
the file-based edit loop in `plugins/claudia/rules/common/review-gate.md`.
The task breakdown (step 5) is also direction-locking and gated the same
way after ROADMAP.md is accepted.

On both gates passing:

1. Record gate clearances:
   ```
   claudia gate accept ROADMAP.md
   claudia gate accept STATE-tasks
   ```
2. Initialize `.planning/STATE.md` by rendering the template with
   starting values:
   ```
   claudia template render STATE \
       --var name=<issue-title> \
       --var current_phase="Phase 1 — <title>" \
       --var last_command=/claudia-plan \
       --var next_step=/claudia-execute \
       --var updated=<YYYY-MM-DD> \
       --output .planning/STATE.md --force
   ```
3. Write the task lines into the `<!-- claudia:tasks -->...
   <!-- /claudia:tasks -->` region of `.planning/STATE.md` (one line per
   task, `- [ ] T<N> — <title — full spec>`).
4. Advance state:
   ```
   claudia state set last_command /claudia-plan
   claudia state set next_step /claudia-execute
   ```

## Rules

- Tasks must be small and independently verifiable — sized for one
  executor and one verifier pass.
- Independent tasks are eligible for parallel execution only if
  `execution.parallel` is enabled.
- Do not skip the chained approach-mode discuss step. The brief tells us
  *what*; this discussion tells us *how*.
