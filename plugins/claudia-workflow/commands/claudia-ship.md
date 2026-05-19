---
description: Ship the verified phase — run a final secret scan, then hand off to the gh-workflow PR draft so the user reviews and accepts the pull request before it is created.
---

# Ship the phase

The user wants to open a pull request for the completed, verified phase.

Argument: `$ARGUMENTS` — passed through to `/gh-pr-draft` (e.g. `base:dev`).

## Steps

1. **Check readiness.** Read `STATE.md` — the phase must have passed
   `/claudia-verify` with no unresolved CRITICAL findings. If it has not, stop
   and tell the user to run `/claudia-verify` first.
2. **Final secret scan.** Scan the branch's diff against the base for secrets,
   credentials, and unpublished data per the secure-ai-use rule. If anything
   is found, stop and surface it — do not proceed.
3. **Hand off to `/gh-pr-draft`.** It drafts the PR in the fixed structure and
   runs its own review gate: present the draft, then **accept / edit /
   cancel**. The PR is created only on accept.
4. **On success**, update `STATE.md`: record the PR, advance the current
   phase, set next step = `/claudia-discuss` for the following phase (or mark
   the roadmap complete).

## Review gate

Opening a PR is outward-facing — it is fully gated by `/gh-pr-draft`'s
accept/edit/cancel flow. Never create or push anything before the user
accepts the draft.

## Rules

- Requires the `gh-workflow` plugin. If it is not available, tell the user.
- Do not ship a phase that failed verification.
- The final secret scan is mandatory.
