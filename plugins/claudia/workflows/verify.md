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
or commits. If issues are found, branch the fix prompt on
`claudia config get mode`:

- **`yolo`** — `AskUserQuestion`: *fix now (executor)* / *accept with
  warnings* / *stop*.
- **`pair`** — `AskUserQuestion`: *fix now (executor)* / *fix now
  (I'll fix it myself)* / *accept with warnings* / *stop*.

On **fix now (executor)** in either mode, create fix tasks and loop back
to `/claudia-execute`. On **fix now (I'll fix it myself)** in `pair`,
list every issue with `file:line` and severity, then wait for the user
to signal *fixed* / *cancel* before re-running verify. Do **not**
re-dispatch the executor in this branch.

### Fix-loop cap

Before either *fix now* branch starts — `fix now (executor)` **and**
`fix now (I'll fix it myself)` — bump the fix-attempts counter:

```
claudia verify fix-attempts --increment
```

The cap and escalation prompt apply equally to both branches. A
user-driven fix loop that keeps surfacing new issues hits the cap
exactly like an executor-driven one — the workflow stalls otherwise.

The CLI returns `{attempts, cap, cap_reached}`. The cap is **3**. If
`cap_reached` is true (this would be the 3rd consecutive failed verify
without a passing pass in between), do **not** silently loop again.
Surface an escalation prompt via `AskUserQuestion`:

- *Accept with warnings* — close the loop, ship despite the remaining
  issues (still blocked on CRITICAL).
- *Stop* — abort the workflow; the user takes over manually.
- *Override and try once more* — explicit one-pass override; only use
  when the user has a concrete reason to believe the next fix will
  succeed.

The counter is **reset on a passing verify verdict**:

```
claudia verify fix-attempts --reset
```

This must happen *before* the state-advance below, so a future verify
loop starts fresh. The CLI also resets the counter automatically
whenever `claudia state set current_phase ...` changes the phase value,
so phase N+1 always starts from zero attempts — no leftover state from
phase N.

Shipping is blocked on any CRITICAL finding regardless of mode.

On a passing verdict, advance state:
```
claudia verify fix-attempts --reset
claudia state set last_command /claudia-verify
claudia state set next_step /claudia-close
```

## Rules

- Verify behaviour — run the tests; do not trust commit messages.
- The secret scan is mandatory and is not configurable.
