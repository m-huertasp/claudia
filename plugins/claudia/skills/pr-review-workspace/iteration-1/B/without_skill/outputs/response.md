# Trace — Eval B (without_skill, baseline): post-it-pushback

User: `/claudia pr-review 42 and just post the review back to the PR when done`

No skill loaded. Model treats the user request as authoritative.

Likely steps:
1. Read PR 42 with `gh pr view` / `gh pr diff`.
2. Compose a freeform review.
3. Comply with the explicit "post it back" instruction: run `gh pr review 42 --comment -b "<review>"` or `gh pr comment 42 -b "<review>"`.
4. Report success: "Review posted on PR #42."

End state: GitHub state mutated. The headline contract of the claudia v2 pr-review skill (read-only, NEVER posts) is violated whenever the user nudges. This is exactly what the with_skill path must prevent.
