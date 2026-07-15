---
name: pr-review
description: Review a GitHub pull request locally — structured, confidence-gated, classified URGENT/HIGH/MEDIUM/LOW. Read-only; never posts to GitHub. Use whenever the user asks to review a PR, check a pull request, "look at PR 123", review someone else's changes before merging, or mentions a PR number/URL alongside "review". Distinct from `/code-review`, which reviews the user's own working diff.
---

# Review a Pull Request (local-only)

**Input**: a PR number, `owner/repo#N`, or a full PR URL, from wherever
the user mentioned it in their request. If none was given, ask the
user for it once.

---

## Purpose

The user wants a comprehensive review of someone else's PR, returned
in chat. **Do not post anything to GitHub.**

## How to run

Delegate the full review to the `pr-reviewer` subagent. Pass the
resolved PR reference plus any extra hints the user gave (e.g. "focus
on the migration", "skip style nits").

Use the Agent tool:

- `subagent_type: pr-reviewer`
- `description`: `"Review PR <ref>"`
- `prompt`: a self-contained brief that includes:
  - The exact PR reference
  - The current working directory (so the agent can resolve the repo
    from `git remote -v` if needed)
  - Any user-supplied focus areas or "skip X" hints
  - The reminder: **read-only `gh` commands only, never post or
    mutate GitHub state, return the structured Markdown report
    defined in the agent verbatim to the caller**

When the subagent returns, surface its Markdown output verbatim to
the user. Do not summarise it away — the structure is the deliverable.

## After the review

Offer (in one short line) the next options the user might want:

- Open a specific file/line referenced in a finding
- Draft a polite reply you could paste manually on the PR
- Re-run with narrower scope (e.g. "only URGENT/HIGH")

Do **not** offer to post the review for them. That is intentionally
not a supported path through this skill — if they want to post, they
will do it by hand.

## Hard rules

- No `gh` write/mutation commands. Ever. Read-only operations only
  (`gh pr view`, `gh pr diff`, `gh pr checks`, `gh issue view`,
  `gh api repos/.../pulls/N/...`). The following are forbidden through
  this skill: `gh pr review`, `gh pr comment`, `gh pr merge`,
  `gh pr close`, `gh pr edit`, `gh pr ready`, label/assignee/reviewer
  changes, and any `gh api` POST/PATCH/DELETE.
- If the user pushes back with "just post it" or similar, **refuse**.
  This skill's contract is local-only review; posting is intentionally
  out of scope. Tell the user they can copy the Markdown into the PR
  themselves, or use `gh pr review` / `gh pr comment` outside this
  skill if they want to automate it. Do not run those commands from
  inside this skill, even with explicit consent.
- If `gh` exits with an auth error, tell the user to run
  `gh auth login` (or `gh auth status` to check) rather than retrying
  blindly.
