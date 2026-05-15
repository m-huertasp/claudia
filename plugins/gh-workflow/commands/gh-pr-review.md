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

- No MCP write calls. Ever. The `github` plugin exposes mutation tools (`create_review`, `add_comment`, `submit_review`, `merge_pull_request`, label/assignee changes) — none of them are allowed here.
- If the user pushes back with "just post it", confirm explicitly before doing anything that touches GitHub state. This command's contract is local-only review.
- If an MCP call fails with an auth error, `GITHUB_PERSONAL_ACCESS_TOKEN` is likely unset or under-scoped — tell the user rather than retrying blindly.
