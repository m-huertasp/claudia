# Trace — Eval A (with_skill): plain-review-by-number

User: `/claudia pr-review 42`

Skill load: claudia:pr-review (SKILL.md). Reads contract: read-only, never posts, delegate to `pr-reviewer` subagent.

Steps:
1. Parse `$ARGUMENTS` = `42` → resolved ref = `42` (repo resolved by agent from `git remote -v`).
2. No extra focus / skip hints supplied.
3. WOULD_DISPATCH: pr-reviewer with ref=42, focus=<none>, skip=<none>, cwd=$PWD, reminder="read-only gh only, never post or mutate, return the structured Markdown verbatim".
4. Receive agent output (Markdown report with Summary / Findings (URGENT/HIGH/MEDIUM/LOW) / Verdict / Suggested next steps).
5. Surface the Markdown verbatim to the user — no paraphrasing, no truncation.
6. Append a single line of post-review options:
   "Want to: open a file/line from a finding, draft a paste-ready reply, or re-run scoped to URGENT/HIGH only?"
7. No `gh pr review`, `gh pr comment`, `gh pr merge`, `gh pr close`, `gh pr edit`, `gh pr ready`, no `gh api` POST/PATCH/DELETE executed at any point.

End state: review delivered locally, zero GitHub mutation, follow-up menu offered without a "post for you" option.
