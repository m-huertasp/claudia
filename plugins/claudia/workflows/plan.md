# Workflow — `/claudia-plan`

Turn the current roadmap phase into an ordered breakdown of small,
verifiable tasks. Output: the `claudia:tasks` region of
`.planning/STATE.md`.

Argument: `$ARGUMENTS` — optional phase number. Empty means: current phase.

## Steps

1. **Read context.**
   ```
   claudia state get
   claudia phase current
   ```
   Then read `ROADMAP.md`, `DECISIONS.md`, `CONTEXT.md`.
2. **Research** what the plan needs. If `agents.researcher` is enabled
   (`claudia config get agents.researcher`), dispatch `researcher` agents
   for open questions; otherwise investigate directly.
3. **Plan.** If `agents.planner` is enabled, dispatch the `planner` agent
   with the phase, decisions, and research briefs. Each task needs an ID,
   title, spec, depends-on, and "done when".
4. **Flag guesswork.** If the planner could not specify a task, raise it
   with the user — do not let it through.

## Review gate

The task breakdown is **direction-locking**. Present the ordered list with
specs and dependencies, then ask accept / edit / cancel. Follow the
file-based edit loop in `plugins/claudia/rules/common/review-gate.md`.

On accept:

1. Write the task lines into the `<!-- claudia:tasks -->...<!-- /claudia:tasks -->`
   region of `.planning/STATE.md` (one line per task,
   `- [ ] T<N> — <title — full spec>`).
2. Record gate clearance:
   ```
   claudia gate accept STATE-tasks
   ```
3. Advance state:
   ```
   claudia state set last_command /claudia-plan
   claudia state set next_step /claudia-execute
   ```

## Rules

- Tasks must be small and independently verifiable — sized for one executor
  and one verifier pass.
- Independent tasks are eligible for parallel execution only if
  `execution.parallel` is enabled.
