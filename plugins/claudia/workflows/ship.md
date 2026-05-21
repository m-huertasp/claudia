# Workflow — `/claudia-ship`

Open a pull request for the completed, verified phase.

Argument: `$ARGUMENTS` — passed through to `/gh-pr-draft` (e.g. `base:dev`).

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
3. **Hand off to `/gh-pr-draft`.** It drafts the PR in the fixed structure
   and runs its own accept / edit / cancel gate. The PR is created only on
   accept.
4. **On success**, advance the state machine:
   ```
   claudia phase set-status <N> complete
   claudia state set last_command /claudia-ship
   claudia state set next_step /claudia-discuss
   ```
   If `claudia phase current` then raises "all phases are complete", mark
   the roadmap done in `STATE.md`'s notes section.

## Review gate

Opening a PR is outward-facing — fully gated by `/gh-pr-draft`'s
accept/edit/cancel flow. Never push or create anything before the user
accepts the draft.

## Rules

- Requires the `gh-workflow` plugin. If it is not available, tell the user
  and stop.
- Do not ship a phase that failed verification.
- The final secret scan is mandatory.
