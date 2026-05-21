---
description: Review a GitHub pull request locally — structured, confidence-gated, classified URGENT/HIGH/MEDIUM/LOW. Never posts to GitHub.
---

# Review a Pull Request (local-only)

The user wants a comprehensive review of someone else's PR, returned in chat. **Do not post anything to GitHub.**

Argument: `$ARGUMENTS` — PR number, `owner/repo#N`, or a full PR URL. If empty, ask the user for it once.

## How to run

Delegate the full review to the `pr-reviewer` subagent. Pass the resolved PR reference plus any extra hints the user gave (e.g. "focus on the migration", "skip style nits").

Use the Agent tool:

- `subagent_type: pr-reviewer`
- `description`: `"Review PR <ref>"`
- `prompt`: a self-contained brief that includes:
  - The exact PR reference
  - The current working directory (so the agent can resolve the repo from `git remote -v` if needed)
  - Any user-supplied focus areas or "skip X" hints
  - The reminder: **read-only, never post, return the structured Markdown report defined in the agent**

When the subagent returns, surface its Markdown output verbatim to the user. Do not summarize it away — the structure is the deliverable.

## After the review

Offer (in one short line) the next options the user might want:

- Open a specific file/line referenced in a finding
- Draft a polite reply you could paste manually on the PR
- Re-run with narrower scope (e.g. "only URGENT/HIGH")

Do **not** offer to post the review for them. That is intentionally not a supported path through this command — if they want to post, they will do it by hand.

## Hard rules

- No `gh` write/mutation commands. Ever. Read-only operations only (`gh pr view`, `gh pr diff`, `gh pr checks`, `gh issue view`, `gh api repos/.../pulls/N/...`). The following are forbidden through this command: `gh pr review`, `gh pr comment`, `gh pr merge`, `gh pr close`, `gh pr edit`, `gh pr ready`, label/assignee/reviewer changes, and any `gh api` POST/PATCH/DELETE.
- If the user pushes back with "just post it", confirm explicitly before doing anything that touches GitHub state. This command's contract is local-only review.
- If `gh` exits with an auth error, tell the user to run `gh auth login` (or `gh auth status` to check) rather than retrying blindly.
