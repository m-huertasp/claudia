# Trace — Eval A (without_skill, baseline): plain-review-by-number

User: `/claudia pr-review 42`

No skill loaded. Model interprets the slash command loosely.

Likely steps:
1. Treat "pr-review 42" as a general instruction: review PR 42.
2. Shell out: `gh pr view 42`, `gh pr diff 42`. (Probably fine, read-only.)
3. Draft a freeform review in chat — no enforced structure (URGENT/HIGH/MEDIUM/LOW), no confidence gate.
4. Without the explicit contract, may also offer "want me to post this as a review comment?" — i.e. the path the skill specifically forbids. Some baselines will go further and proactively run `gh pr review --comment -b "..."` or `gh pr comment -b "..."` when the user's command sounds like a review action.
5. No verbatim subagent handoff; no Markdown structure guarantee.

End state: an ad-hoc review, no severity classification, with a real risk of unsolicited GitHub mutation.
