---
description: List GitHub issues assigned to the current user, grouped by repo and sorted by recency. Read-only.
---

# My Assigned Issues

Argument: `$ARGUMENTS` — optional filters, free-text. Recognized hints:

- `repo:owner/name` → restrict to one repo
- `label:foo` → filter by label
- `open` (default) / `closed` / `all`
- A bare word → fuzzy-match in titles

## Steps

1. **Identify the user.** Use the `github` MCP plugin's authenticated-user lookup to get the login. Do not rely on git config — the GitHub login may differ.

2. **Query issues.** Use the MCP `search_issues` (or equivalent read-only) tool with `assignee:<login>` plus the filters from `$ARGUMENTS`. Default to open issues across all repos the user has access to.

3. **Group and sort.** Group by repository; within each group, sort by `updated_at` descending.

4. **Render** as:

```markdown
## Issues assigned to @<login>  (<N> total)

### owner/repo  (<n>)
- **#123** — <title>  · <labels>  · updated <relative-time>
- **#118** — <title>  · <labels>  · updated <relative-time>

### owner/other-repo  (<n>)
- ...
```

5. **Tail line.** After the list, add one line: `Open any item in the browser, or run /gh-pr-draft once you have a branch.`

## Rules

- Read-only. Do not assign, label, comment, or close.
- If the user has 0 issues, say so plainly — don't pad the output.
- If the search returns >50 issues, show the first 30 grouped by repo and add a `… and <n> more, narrow with repo:/label:/keyword` line.
- If an MCP call fails with an auth error, `GITHUB_PERSONAL_ACCESS_TOKEN` is likely unset or under-scoped — tell the user rather than retrying blindly.
