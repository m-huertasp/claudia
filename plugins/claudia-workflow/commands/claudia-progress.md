---
description: Report where the claudia workflow currently stands — current phase, last command, open tasks, and the suggested next step — by reading .planning/STATE.md.
---

# Workflow progress

The user wants to know where the project stands. This command is read-only.

Argument: `$ARGUMENTS` — optional. `--next` means: after reporting, offer to
run the suggested next command.

## Steps

1. **Read `.planning/STATE.md`.** If it does not exist, tell the user no
   `claudia` project is initialized here and suggest `/claudia-new`.
2. **Report**, concisely:
   - Current phase and its roadmap goal
   - Last command run
   - Open tasks — done vs. remaining
   - Any "notes for the next session"
   - The suggested next step
3. **If `--next`** was passed, ask the user — with `AskUserQuestion` — whether
   to run the suggested next command now.

## Rules

- Read-only. This command never edits state or runs another phase on its own.
- With `--next`, still confirm before invoking the next command — never
  auto-run a phase.
