---
description: Draft a pull request from the current branch in a fixed, human-readable structure — then create it on GitHub only after the user accepts the draft.
---

# Draft a Pull Request

The user wants to open a PR for their current branch. Write the draft in the fixed structure below, **show it, and create the PR only if the user accepts.**

Argument: `$ARGUMENTS` — optional. May contain a base branch (`base:dev`), a target repo, or focus hints. If empty, infer the base branch (usually `dev`) and the repo from the git remote.

## Steps

### 1. Gather the change

Run, in the working directory:

- `git branch --show-current` — the head branch
- `git remote -v` — the repo
- `git log <base>..HEAD --oneline` — every commit on the branch, not just the latest
- `git diff <base>...HEAD --stat` and the full `git diff <base>...HEAD` — the actual change
- Check whether the branch is pushed and up to date with its remote

If the branch has no commits ahead of base, stop and tell the user there is nothing to draft.

Read enough of the diff to understand it. Group the changes into themes (a feature, a bug fix, a refactor) — do not just paraphrase commit messages.

### 2. Write the draft — FIXED structure, shallow

Always produce exactly these sections. Keep it concise: this is a PR description, not a design doc. No deep dives, no per-file walkthroughs.

**Title:** one line, imperative, under 70 characters. Prefix with type if the repo uses it (`feat:`, `fix:`, `refactor:`).

**Body (Markdown):**

```markdown
## What this does
<2–4 sentences, plain language, like explaining it to a teammate. Lead with
the main feature(s) added or bug(s) fixed. Say why, not just what.>

## Changes
- <one bullet per meaningful change — group small/related edits into one line>
- ...

## What to review
<1–3 bullets pointing reviewers at the parts that need real attention:
tricky logic, a decision that could go another way, a risky area. If the PR
is trivial, say "Straightforward — no specific concerns.">

## Testing
<How it was verified: tests added/run, manual checks. If untested, say so
plainly.>
```

Rules for the body:

- Write the "What this does" section in a human voice — a person explaining their work, not a changelog.
- Keep "Changes" to the meaningful edits; collapse noise (formatting, renames) into a single bullet.
- "What to review" must be honest — if something is shaky or undertested, point reviewers at it. Do not hide it.
- Never invent a test plan. If the branch has no tests and you can't verify it, the Testing section says exactly that.

### 3. Present the draft for accept / refuse — REQUIRED

Show the user, in chat:

- Target repo and `base ← head` branches
- Title
- Full rendered body
- Whether the branch still needs to be pushed

Use the `AskUserQuestion` tool to ask: **accept and create the PR**, **edit something first**, or **refuse / cancel**. Do not call any PR-creating tool before an explicit accept. On "edit", revise and re-present — re-ask every time.

### 4. Create and report

Only after the user accepts:

- If the branch is not pushed, push it (`git push -u origin <branch>`) — this is a shared action, so mention it explicitly as you do it.
- Create the PR via the `github` MCP plugin's create-pull-request tool, using the accepted title and body and the resolved base branch. Open it as a draft PR if the user asked for that.
- Report the new PR number and URL.

## Rules

- **Acceptance is mandatory.** Opening a PR is visible to others — never skip step 3, even if the original request said "just open it". Show the draft, then create.
- The structure in step 2 is fixed. Do not add, drop, or reorder sections per PR.
- Keep it shallow and readable. A reviewer should grasp the PR in under a minute.
- This command only *creates* PRs. It does not review, merge, or comment — use `/gh-pr-review` for review.
- If an MCP call fails with an auth error, `GITHUB_PERSONAL_ACCESS_TOKEN` is likely unset or under-scoped — tell the user rather than retrying blindly.
