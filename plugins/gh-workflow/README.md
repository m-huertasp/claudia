# gh-workflow

GitHub workflow commands for Claude Code — triage issues and pull requests without leaving the chat.

## What's inside

| Command | Action | Writes to GitHub? |
|---|---|---|
| `/gh-issue [owner/repo:] <description>` | Draft a structured issue and create it | Yes — after a confirmation gate |
| `/gh-my-issues [filters]` | List issues assigned to me, grouped by repo | No |
| `/gh-my-prs [filters]` | List PRs I authored / am review-requested on / am assigned | No |
| `/gh-pr-draft [base:branch]` | Draft a PR for the current branch and create it | Yes — after an accept/refuse gate |
| `/gh-pr-review <num\|owner/repo#num\|url>` | Structured review classified URGENT/HIGH/MEDIUM/LOW | **Never** — output stays in chat |

Plus one subagent, `pr-reviewer`, which `/gh-pr-review` delegates to.

## Safety model

- **Read commands** (`/gh-my-issues`, `/gh-my-prs`) never mutate anything.
- **Write commands** (`/gh-issue`, `/gh-pr-draft`) always show a full draft and require explicit confirmation via an `AskUserQuestion` prompt before anything is created. Editing the draft re-triggers the gate.
- **`/gh-pr-review` and the `pr-reviewer` agent never post to GitHub.** No comment, review, approval, merge, or label change — the review is returned to you and you decide what to do with it. This is the deliberate inverse of the official `code-review` plugin.

## Prerequisite — the GitHub MCP server

These commands call GitHub through an MCP server that exposes `mcp__github__*` tools. This plugin does **not** bundle its own MCP server, to avoid a server-name collision when the official one is also installed.

Install the official `github` plugin from the `claude-plugins-official` marketplace, then set a token:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx   # repo + read:org scopes
```

The token must be set in the environment Claude Code runs in. If it is missing, every command here fails at the first MCP call — that is the first thing to check when a command errors out.

## Install

Copy `plugins/gh-workflow/` into a marketplace directory, or reference this repo as a marketplace and enable the `gh-workflow` plugin. The commands and the `pr-reviewer` agent register automatically.

## Notes

- `/gh-pr-draft` defaults the base branch to `dev`; override with `base:main` (or any branch) in the argument.
- `gh` CLI is not required — all GitHub access goes through the MCP server.
