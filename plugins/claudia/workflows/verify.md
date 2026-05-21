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
2. **Resolve project type** to choose the automated-test runner:
   ```
   claudia detect
   ```
3. **Verify.** If `agents.verifier` is enabled, dispatch the `verifier`
   agent (which runs both stages and delegates the quality pass to
   `code-reviewer`). Otherwise run the two stages directly:
   - **Stage 1 — spec compliance:** each completed task does what its spec
     said; "done when" actually holds; no out-of-scope changes.
   - **Stage 2 — code quality:** project rules; run the test suite; confirm
     coverage. **Branch the test runner on `primary` from `claudia detect`:**
     - `python` → `uv run pytest` (or `pytest`); `ruff check .`; `mypy`.
     - `nextflow` → `nf-test test` against the bundled stub profile;
       `nextflow lint` if installed.
     - `unknown` → ask the user how to verify; do not invent a runner.
4. **Generate the human checklist.** For pipelines, automated stub runs
   alone do not prove the work; produce specific manual checks the user
   must run before shipping. Initialise the artifact if it does not exist:
   ```
   claudia verify init --name <project>
   ```
   then add one item per check, e.g.:
   ```
   claudia verify add "Run nextflow run . -profile test"
   claudia verify add "Confirm results/multiqc_report.html opens cleanly"
   claudia verify add "Confirm row count of results/summary.tsv ≈ <expected>"
   ```
   For a pure-Python phase where automated tests are sufficient, skip the
   checklist (no items added). The ship gate then permits the phase if the
   automated tests pass.
5. **Secret scan** the phase's diff per the secure-ai-use rule. Always
   runs; cannot be skipped.
6. **CONTEXT.md drift check.** Compare the branch's changed paths
   against `.planning/CONTEXT.md`. Drift signals:
   - A new top-level directory not mentioned in CONTEXT.md's "Key files"
     or "Architecture" section.
   - A new dependency added to `pyproject.toml` / `nextflow.config` /
     equivalent that CONTEXT.md does not list.
   - A file mentioned in CONTEXT.md as a "key file" was renamed or
     deleted.
   If any signal fires, ask the user via `AskUserQuestion`:
   - *Refresh CONTEXT.md now* — run `/claudia-understand refresh` before
     proceeding.
   - *Continue, refresh later* — note the drift in the verification
     report and proceed.
   - *Stop.*
7. **Report** per task: stage-1 pass/fail, stage-2 findings classified
   CRITICAL/HIGH/MEDIUM/LOW, overall verdict. If a human checklist was
   added, list its items and tell the user how to confirm them
   (`claudia verify confirm V<N>`). Surface any CONTEXT.md drift the
   user opted to defer.

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
