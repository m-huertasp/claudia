# Workflow — `/claudia-progress`

Report where the workflow currently stands. **Read-only** — this command
never edits state or runs another phase.

Argument: `$ARGUMENTS` — optional. `--next` means: after reporting, offer
to run the suggested next command.

## Steps

1. **Read state.**
   ```
   claudia state get
   claudia state tasks
   claudia phase current   # may raise "all phases are complete"
   ```
   If `claudia state get` fails because `.planning/STATE.md` is missing,
   tell the user no `claudia` project is initialised here and suggest
   `/claudia-new`.
2. **Report**, concisely:
   - Current phase and its roadmap goal
   - Last command run, next suggested step
   - Open tasks — done vs. remaining
   - Any "notes for the next session"
3. **If `--next`** was passed, ask the user with `AskUserQuestion` whether
   to run the suggested next command now.

## Rules

- Read-only. Never edit state or auto-run a phase.
- With `--next`, still confirm before invoking the next command.
