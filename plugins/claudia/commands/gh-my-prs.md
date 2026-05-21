---
description: List GitHub pull requests that involve the current user — authored, review-requested, or assigned. Read-only.
---

# My Pull Requests

Argument: `$ARGUMENTS` — optional filters, free-text. Recognized hints:

- `authored` / `review-requested` / `assigned` / `all` (default `all`)
- `repo:owner/name`
- `open` (default) / `closed` / `merged` / `all`
- `draft` → include drafts (excluded by default)

## Steps

1. Resolve the authenticated GitHub login via the `github` MCP plugin.

2. Run up to three read-only searches and merge the results, deduping by PR URL:
   - `is:pr author:<login>`
   - `is:pr review-requested:<login>`
   - `is:pr assignee:<login>`

   Apply state/repo filters from `$ARGUMENTS`. Drafts excluded unless `draft` is in the args.

3. Annotate each PR with a relationship tag — `authored`, `review-requested`, `assigned` (a PR can carry several tags).

4. **Render** in three sections, in this order:

```markdown
## Review-requested  (<n>)
- **owner/repo#456** — <title> · @<author> · updated <rel> · checks: <pass/fail/pending>

## Authored by me  (<n>)
- **owner/repo#321** — <title> · <state> · updated <rel> · checks: <pass/fail/pending>

## Assigned (other)  (<n>)
- ...
```

If a section is empty, write `_None_` rather than omitting it.

5. **Tail line.** `Run /gh-pr-review <number> for a structured review (does not post).`

## Rules

- Read-only.
- Surface failing CI checks if the MCP plugin exposes them — do not re-run CI.
- If totals are large, cap each section at 20 and add a `… and <n> more` line.
- If an MCP call fails with an auth error, `GITHUB_PERSONAL_ACCESS_TOKEN` is likely unset or under-scoped — tell the user rather than retrying blindly.
