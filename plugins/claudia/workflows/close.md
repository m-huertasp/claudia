# Workflow — `/claudia-close`

Close out a verified issue by opening (or drafting) a pull request. The
actual PR drafting lives in the internal
[`workflows/draft-pr.md`](draft-pr.md) workflow, which this command
invokes after running readiness gates. The behavior at the end of the
flow branches on `mode`:

- **`yolo`** — draft-pr pushes the branch and creates the PR via `gh`.
- **`pair`** — draft-pr pushes the branch and prints the title + body
  for the user to open the PR themselves.

Argument: `$ARGUMENTS` — optional base branch override (e.g. `base:dev`),
passed through to the draft-pr workflow.

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
   exists (pure-Python phases that didn't add a human checklist) — in
   that case run `ls .planning/VERIFICATION.md` first to decide.
2. **Final secret scan** of the branch diff against the base per the
   secure-ai-use rule. If anything is found, stop.
3. **CONTEXT.md drift check.** Re-run the drift heuristics from
   `/claudia-verify` (new top-level dir, new dependency, renamed key
   file). If drift is detected and was not already resolved during
   verify, ask via `AskUserQuestion`:
   - *Refresh CONTEXT.md now* — run `/claudia-understand refresh`, then
     resume the close flow.
   - *Close anyway* — proceed but include a note in the PR description.
   - *Stop.*
4. **Read mode.**
   ```
   claudia config get mode
   ```
   If missing/unreadable, treat as `pair`.
5. **Invoke `workflows/draft-pr.md`** with the resolved `mode` and any
   `base:` argument passed through. That workflow drafts the PR, runs
   its own accept gate, and either creates the PR (yolo) or prints the
   draft for manual open (pair).
6. **On success**, advance the state machine:
   ```
   claudia phase set-status <N> complete
   claudia state set last_command /claudia-close
   claudia state set next_step /claudia-brief
   ```
   If `claudia phase current` then raises "all phases are complete", mark
   the roadmap done in `STATE.md`'s notes section. The next issue starts
   with a fresh `/claudia-brief`.

## Review gate

Opening or printing a PR is outward-facing — fully gated by
`draft-pr.md`'s accept/edit/cancel flow. Never push, create, or print
anything before the user accepts the draft.

## Rules

- In `yolo`, requires the `gh` CLI authenticated via `gh auth login`.
  If `gh` is not installed or not authenticated, tell the user and stop
  — even in pair we still push the branch with `git`, but `gh pr create`
  is yolo-only.
- Do not close a phase that failed verification.
- The final secret scan is mandatory.
