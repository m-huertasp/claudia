# Workflow — `/claudia-verify`

Two-stage review of the completed phase, plus a mandatory secret scan.
Output: a verification report shown in chat.

Argument: `$ARGUMENTS` — optional task IDs. Empty means: every task
completed since the last verification.

## Steps

1. **Read state.**
   ```
   claudia state tasks
   claudia state get
   claudia config get agents.verifier
   ```
2. **Verify.** If `agents.verifier` is enabled, dispatch the `verifier`
   agent (which runs both stages and delegates the quality pass to
   `code-reviewer`). Otherwise run the two stages directly:
   - **Stage 1 — spec compliance:** each completed task does what its spec
     said; "done when" actually holds; no out-of-scope changes.
   - **Stage 2 — code quality:** project rules; run the test suite; confirm
     coverage.
3. **Secret scan** the phase's diff per the secure-ai-use rule. Always
   runs; cannot be skipped.
4. **Report** per task: stage-1 pass/fail, stage-2 findings classified
   CRITICAL/HIGH/MEDIUM/LOW, overall verdict.

## Review gate

The verification report is presented to the user — verification never edits
or commits. If issues are found, ask: **fix now** (loop back to
`/claudia-execute` with fix tasks), **accept with warnings**, or **stop**.
Shipping is blocked on any CRITICAL finding.

On a passing verdict, advance state:
```
claudia state set last_command /claudia-verify
claudia state set next_step /claudia-ship
```

## Rules

- Verify behaviour — run the tests; do not trust commit messages.
- The secret scan is mandatory and is not configurable.
