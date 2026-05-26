---
name: write-issue
description: Draft a well-structured GitHub issue and create it in a target repo via `gh` — but ONLY after the user reviews and explicitly confirms the draft. Callable-only utility skill, invoked via `/claudia write-issue [owner/repo:] <description>`. Do NOT auto-trigger from natural-language hints like "file an issue", "open a github issue", "write an issue", "new issue", "report a bug to the repo", or "create a feature request" — this skill runs only when the dispatcher explicitly routes the `write-issue` verb. Confirmation is mandatory even if the user said "just do it" up front.
---

# Write a GitHub Issue

> Invoke as: `/claudia write-issue <description>` or `/claudia write-issue <owner/repo>: <description>`

**Input**: `$ARGUMENTS` — free text describing the issue and, ideally, the
target repo. Typical forms:

- `owner/repo: <description>`
- `<description>` (resolve the repo from `git remote -v` in the current
  working directory)
- A description plus hints like `label:bug`, `type:feature`, `assign:me`

---

## Purpose

The user wants to file a new GitHub issue. Draft it in the standard
structure below, **show the full draft for review, and create it only
after explicit confirmation.**

## Steps

### 1. Resolve target and intent

- **Repo:** from `owner/repo:` in the args (parse the prefix before the
  first `:`), else from the current working directory's git remote
  (`git remote get-url origin`, parsed to `owner/repo`). If neither
  resolves, ask the user once via `AskUserQuestion` which repo to target
  — do not guess.
- **Type:** classify as `bug`, `feature`, `task`, or `question` from
  the description. This drives which template section set to use.
- If the description is too thin to write a useful issue (e.g. one
  vague sentence), ask the user 1–3 targeted questions before drafting
  — do not pad with guesses.

### 2. Gather repo-side context (read-only)

- Grep the codebase for files, symbols, or errors named in the
  description so the issue can cite concrete locations.
- Check the repo's existing labels with `gh label list --repo <owner/repo> --limit 200`
  so suggested labels are real.
- Scan recent open issues with
  `gh issue list --repo <owner/repo> --state open --search "<keywords>" --limit 20`
  for an obvious duplicate; if one exists, surface it before drafting
  further and let the user decide whether to continue.

### 3. Draft the issue

Use this structure. Drop sections that genuinely do not apply
(e.g. no "Steps to reproduce" for a feature), but keep the skeleton
consistent.

**Title:** concise, imperative, prefixed by type when the repo
convention uses it (`bug: …`, `feat: …`).

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
- Suggested labels / assignees / milestone (only ones that exist in
  the repo)

Then ask explicitly whether to create it, offering: **create as-is**,
**edit something first**, or **cancel**. Use the `AskUserQuestion`
tool for this.

**Do not run `gh issue create` until the user confirms.** If they ask
for edits, revise the draft and present it again — re-confirm every
time.

### 5. Create and report

On confirmation, create the issue with `gh`. Pass the body via a
HEREDOC and stdin (`--body-file -`) so Markdown formatting survives
shell quoting:

```bash
gh issue create \
  --repo <owner/repo> \
  --title "<title>" \
  --body-file - \
  --label "<label1>,<label2>" \
  --assignee "<user>" <<'EOF'
<full body markdown>
EOF
```

Drop `--label`, `--assignee`, or `--milestone` flags entirely if there
are none — do not pass empty strings. Report back the new issue number
and URL from `gh`'s output.

## Rules

- **Confirmation is mandatory.** Creating an issue is a visible,
  shared action that other people will see and react to — never skip
  step 4, even if the user said "just do it", "skip the gate", or
  "post it" in the original request. Surface the draft, gate via
  `AskUserQuestion`, then create only on explicit accept.
- The issue will be created under the GitHub account authenticated
  via `gh auth login` — i.e. attributed to the user, not to Claude.
  Mention this if the user asks.
- Only attach labels/assignees/milestones that actually exist in the
  target repo.
- Do not create duplicates — if step 2 found a likely duplicate, raise
  it before drafting further.
- Treat the user's description as the source of truth; do not invent
  acceptance criteria or scope the user did not imply. If a section
  would be guesswork, ask instead.
- This skill only *creates* issues. It does not edit, close, comment
  on, or label existing ones.
- If `gh` exits with an auth error, tell the user to run
  `gh auth login` (or `gh auth status` to check) rather than retrying
  blindly.
