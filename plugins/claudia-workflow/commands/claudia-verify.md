---
description: Verify completed tasks with a two-stage review — stage 1 spec compliance, stage 2 code quality — run tests and a secret scan, and report a verdict before anything ships.
---

# Verify the work

The user wants the completed phase checked before shipping. Output: a
verification report shown in chat.

Argument: `$ARGUMENTS` — optional task IDs to verify. If empty, verify every
task completed since the last verification.

## Steps

1. **Read** `STATE.md` for completed tasks and their specs, `CONTEXT.md` for
   conventions, `config.json` for `agents.verifier`.
2. **Verify.** If `agents.verifier` is enabled, dispatch the `verifier` agent
   (it runs both stages and delegates the quality pass to `code-reviewer`).
   Otherwise run the two stages directly:
   - **Stage 1 — spec compliance:** each task does what its spec said; "done
     when" actually holds; no out-of-scope changes.
   - **Stage 2 — code quality:** project rules (coding-style, security,
     testing); run the test suite; confirm coverage.
3. **Secret scan.** Scan the phase's changes for secrets, credentials, and
   unpublished data per the secure-ai-use rule. This always runs.
4. **Report** — per task: stage 1 pass/fail, stage 2 findings classified
   CRITICAL/HIGH/MEDIUM/LOW, overall verdict.

## Review gate

The verification report is presented for the user to read — verification
never edits or commits. If issues are found, ask the user how to proceed:
**fix now** (loop back to `/clavia-execute` with fix tasks), **accept with
warnings**, or **stop**. Shipping is blocked on a CRITICAL finding.

## Rules

- Verify behavior — run the tests, do not trust commit messages.
- The secret scan is mandatory and cannot be skipped.
- Update `STATE.md`: next step = `/clavia-ship` if the verdict allows.
