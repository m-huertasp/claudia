---
description: Draft a well-structured GitHub issue and create it in a specified repo — only after the user reviews and confirms the draft.
---

# Create a GitHub Issue

The user wants to file a new GitHub issue. Draft it in the standard structure below, **show the full draft for review, and create it only after explicit confirmation.**

Argument: `$ARGUMENTS` — free text describing the issue and, ideally, the target repo. Typical forms:

- `owner/repo: <description>`
- `<description>` (resolve the repo from `git remote -v` in the current working directory)
- A description plus hints like `label:bug`, `type:feature`, `assign:me`

## Steps

### 1. Resolve target and intent

- **Repo:** from `owner/repo` in the args, else from the current working directory's git remote. If neither resolves, ask the user once which repo.
- **Type:** classify as `bug`, `feature`, `task`, or `question` from the description. This drives which template section set to use.
- If the description is too thin to write a useful issue (e.g. one vague sentence), ask the user 1–3 targeted questions before drafting — do not pad with guesses.

### 2. Gather repo-side context (read-only)

- Grep the codebase for files, symbols, or errors named in the description so the issue can cite concrete locations.
- Check the repo's existing labels via the `github` MCP plugin so suggested labels are real.
- Scan recent open issues for an obvious duplicate; if one exists, surface it before drafting further and let the user decide whether to continue.

### 3. Draft the issue

Use this structure. Drop sections that genuinely do not apply (e.g. no "Steps to reproduce" for a feature), but keep the skeleton consistent.

**Title:** concise, imperative, prefixed by type when the repo convention uses it (`bug: …`, `feat: …`).

**Body (Markdown):**

```markdown
## Summary
<2–4 sentences: what and why.>

## Context / Motivation
<Why this matters now. Link related issues/PRs if any.>

## Steps to reproduce        ← bug only
1. ...
2. ...

## Expected vs actual         ← bug only
- Expected: ...
- Actual: ...

## Proposed solution / Scope  ← feature / task
<What a fix or implementation should cover. Bullet the scope.>

## Acceptance criteria
- [ ] ...
- [ ] ...

## Relevant code
- `path/to/file.py:LINE` — <why relevant>

## Additional notes
<Environment, versions, screenshots, anything else. Omit if empty.>
```

### 4. Present the draft for confirmation — REQUIRED

Show the user, in chat, the complete proposed issue:

- Target repo
- Title
- Full rendered body
- Suggested labels / assignees / milestone (only ones that exist in the repo)

Then ask explicitly whether to create it, offering: **create as-is**, **edit something first**, or **cancel**. Use the `AskUserQuestion` tool for this.

**Do not call the create-issue MCP tool until the user confirms.** If they ask for edits, revise the draft and present it again — re-confirm every time.

### 5. Create and report

- On confirmation, create the issue via the `github` MCP plugin's create-issue tool with the confirmed title, body, labels, and assignees.
- Report back the new issue number and URL.

## Rules

- **Confirmation is mandatory.** Creating an issue is a visible, shared action — never skip step 4, even if the user said "just do it" in the original request. Surface the draft, then create.
- Only attach labels/assignees/milestones that actually exist in the target repo.
- Do not create duplicates — if step 2 found a likely duplicate, raise it before drafting further.
- Treat the user's description as the source of truth; do not invent acceptance criteria or scope the user did not imply. If a section would be guesswork, ask instead.
- This command only *creates* issues. It does not edit, close, comment on, or label existing ones.
- If an MCP call fails with an auth error, `GITHUB_PERSONAL_ACCESS_TOKEN` is likely unset or under-scoped — tell the user rather than retrying blindly.
