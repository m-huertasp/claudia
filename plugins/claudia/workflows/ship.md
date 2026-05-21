# Workflow — `/claudia-ship`

Open a pull request for the completed, verified phase.

Argument: `$ARGUMENTS` — passed through to `/claudia-draft-pr` (e.g. `base:dev`).

## Steps

1. **Check readiness.**
   ```
   claudia state get
   claudia gate check ROADMAP.md DECISIONS.md
   claudia verify ready
   ```
   If `claudia gate check` or `claudia verify ready` exits non-zero, stop
   and tell the user which gates or checklist items are still open. The
   `verify ready` check is skipped only when no `.planning/VERIFICATION.md`
   exists (pure-Python phases that didn't add a human checklist) — in that
   case run `ls .planning/VERIFICATION.md` first to decide.
2. **Final secret scan** of the branch diff against the base per the
   secure-ai-use rule. If anything is found, stop.
3. **CONTEXT.md drift check.** Re-run the drift heuristics from
   `/claudia-verify` (new top-level dir, new dependency, renamed key
   file). If drift is detected and was not already resolved during
   verify, ask via `AskUserQuestion`:
   - *Refresh CONTEXT.md now* — run `/claudia-understand refresh`, then
     resume the ship flow.
   - *Ship anyway* — proceed but include a note in the PR description.
   - *Stop.*
4. **Hand off to `/claudia-draft-pr`.** It drafts the PR in the fixed
   structure and runs its own accept / edit / cancel gate. The PR is
   created only on accept.
5. **On success**, advance the state machine:
   ```
   claudia phase set-status <N> complete
   claudia state set last_command /claudia-ship
   claudia state set next_step /claudia-brief
   ```
   If `claudia phase current` then raises "all phases are complete", mark
   the roadmap done in `STATE.md`'s notes section. The next issue starts
   with a fresh `/claudia-brief`.

## Review gate

Opening a PR is outward-facing — fully gated by `/claudia-draft-pr`'s
accept/edit/cancel flow. Never push or create anything before the user
accepts the draft.

## Rules

- Requires the `gh` CLI authenticated via `gh auth login`. If `gh` is not
  installed or not authenticated, tell the user and stop.
- Do not ship a phase that failed verification.
- The final secret scan is mandatory.
