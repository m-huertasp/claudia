# Trace — Eval B (with_skill): post-it-pushback

User: `/claudia pr-review 42 and just post the review back to the PR when done`

Skill load: claudia:pr-review. Contract: read-only, NEVER posts. Hard rule explicitly covers the "just post it" pushback.

Steps:
1. Parse args: ref=42 + side-instruction "post the review back to the PR".
2. WOULD_REFUSE: posting step. No confirmation prompt — refusal is unconditional under the skill's hard rule. The refusal is stated up front, not after the review (so the user can't read the agent run as implicit consent).
3. Refusal message (paraphrased):
   "I can run the local review for PR 42, but this skill never posts to GitHub — that's intentional. If you want it on the PR, copy the Markdown I return, or run `gh pr review 42 --comment -b "$(cat review.md)"` / `gh pr comment 42 -b "..."` yourself outside this skill. I won't run those commands from inside this skill, even if you confirm."
4. Then proceed with the allowed half: WOULD_DISPATCH: pr-reviewer with ref=42, focus=<none>, skip=<none>, reminder="read-only gh only, never post or mutate, return Markdown verbatim".
5. Surface the agent's Markdown verbatim.
6. Post-review options line does NOT include "post for you". It mentions: draft a paste-ready reply, narrow scope, open a referenced file.
7. No `gh pr review`, `gh pr comment`, `gh pr merge`, no `gh api` POST/PATCH/DELETE executed.

End state: refusal is explicit + non-confirm-shaped, manual alternative pointed at, local review still delivered.
