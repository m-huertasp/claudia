# claudia workflows

This directory holds the **orchestration text** for every `/claudia-*`
command. The command files in `../commands/` are deliberately thin — they
carry the slash-command frontmatter and a one-line pointer here. The full
procedure, decisions, review gates, and explicit `claudia` CLI invocations
live in the matching workflow file in this directory.

## Why the split

- **Commands** stay short so the `--help` surface is easy to scan.
- **Workflows** can grow as the orchestration evolves without bloating the
  command surface.
- The orchestrating model always reads the workflow file when it runs a
  command, so adding a step here is enough — no command file changes
  required.

## The CLI contract

Every workflow file invokes the `claudia` CLI (`claudia-tools` package) for
**every deterministic operation** — state mutations, config reads/writes,
phase transitions, template renders, and review-gate acceptance. The
orchestrating model never hand-edits the planning files. The CLI emits the
`{ok, data, error}` envelope on stdout; on failure it sets a non-zero exit
code with a human-readable error.

## Files

| Workflow | Command entry point |
|---|---|
| `dispatcher.md` | `/claudia` (natural-language router) |
| `understand.md` | `/claudia-understand` |
| `brief.md` | `/claudia-brief` |
| `discuss.md` | _internal_ — called from `brief.md` (intent) and `plan.md` (approach) |
| `plan.md` | `/claudia-plan` |
| `execute.md` | `/claudia-execute` |
| `verify.md` | `/claudia-verify` |
| `close.md` | `/claudia-close` |
| `draft-pr.md` | _internal_ — called from `close.md`; gates accept and either `gh pr create`s (yolo) or prints the draft for the user to open (pair) |
| `progress.md` | `/claudia-progress` |
| `settings.md` | `/claudia-settings` |
