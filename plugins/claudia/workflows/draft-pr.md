# Workflow — draft-pr (internal)

Draft a pull request from the current branch in a fixed, human-readable
structure, then either create it on GitHub or hand the draft to the user
to open themselves — depending on the `mode` parameter passed by the
caller.

**This workflow is not user-callable.** It is invoked from
[`workflows/close.md`](close.md) at the end of `/claudia-close`. The
caller resolves `mode` from `claudia config get mode` and passes it in.

Inputs from the caller:

- `mode` — `pair` or `yolo`.
- Optional `base:<branch>` argument forwarded from `$ARGUMENTS`.

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

**Title:** one line, imperative, under 70 characters. Use a `{type}:` prefix matching the [`commit-style`](../rules/common/commit-style.md) keywords (`feat:`, `fix:`, `refactor:`, etc.) — no scope.

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

### 3. Present the draft — REQUIRED

Show the user, in chat:

- Target repo and `base ← head` branches
- Title
- Full rendered body
- Whether the branch still needs to be pushed

Then run the accept gate, **branched on mode**:

#### `yolo` accept gate

Use `AskUserQuestion`:

- **Accept and create the PR** — proceed to step 4 (yolo).
- **Edit something first** — revise the draft and re-present (re-ask every time).
- **Refuse / cancel** — stop, nothing is pushed or created.

#### `pair` accept gate

Use `AskUserQuestion`:

- **Accept — I'll open it myself** — proceed to step 4 (pair).
- **Edit something first** — revise the draft and re-present.
- **Refuse / cancel** — stop, nothing is pushed.

Never push or run `gh pr create` before an explicit accept.

### 4. Create or hand off

Only after the user accepts:

- **Push the branch in both modes** (the user needs a remote ref to open the PR even via the GitHub UI). If already pushed, skip:
  ```bash
  git push -u origin <branch>
  ```
  This is a shared action — call it out explicitly as you do it.

Then branch on mode:

#### `yolo` — create the PR

```bash
gh pr create \
  --base <base> \
  --head <head> \
  --title "<title>" \
  --body-file - <<'EOF'
<full body markdown>
EOF
```

Add `--draft` if the user asked for a draft PR. `gh` infers the repo from the current working directory's git remote — pass `--repo <owner/repo>` explicitly only if the user named a different target.

Report the new PR number and URL from `gh`'s output.

#### `pair` — print the draft and hand off

Do **not** call `gh pr create`. Instead, print to chat:

- The final **title** verbatim.
- The final **body** (full rendered Markdown), inside a fenced code block so it's copy-paste-ready.
- A ready-to-run `gh pr create` command line the user can paste into a terminal if they prefer the CLI over the web UI.

Report the GitHub URL to open the compare view, derived from the
remote and the head branch, so the user can click straight through:
`https://github.com/<owner>/<repo>/compare/<base>...<head>?expand=1`.

End the workflow. The user opens the PR themselves.

## Rules

- **Acceptance is mandatory in both modes.** Never push or print without an explicit accept on step 3.
- The PR (if created) will be opened under the GitHub account authenticated via `gh auth login` — attributed to the user, not to Claude.
- The structure in step 2 is fixed in both modes. Do not add, drop, or reorder sections per PR.
- Keep it shallow and readable. A reviewer should grasp the PR in under a minute.
- This workflow only *drafts* and (in yolo) creates PRs. It does not review, merge, or comment — use `/claudia-pr-review` for review.
- `yolo` requires the `gh` CLI authenticated. If `gh` exits with an auth error, tell the user to run `gh auth login` (or `gh auth status` to check) rather than retrying blindly. `pair` mode only needs `git push` access.
