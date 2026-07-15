# Review Gate

## Purpose

Every edit this plugin's skills make to your files should be
trustworthy without a line-by-line audit — because the skill resolves
uncertainty **before** writing, not after. `claudia` drafts nothing
speculative and posts nothing without being asked.

## The gate, as it applies here

The skills in this plugin follow one of two patterns:

- **Ask before writing** (`add-type-hints`, `prepare-docstrings`) —
  when a skill can't determine something with high confidence (a
  type, an inferred intent), it stops and asks via `AskUserQuestion`
  *before* touching the file. It never guesses and never writes
  speculative content to fill a gap.
- **Read-only, no writes** (`pr-review`, `rules`) — these skills only
  report or print information to chat. They never edit, create, or
  delete a file. If the user wants a suggestion applied, that is a
  separate, explicit request outside the skill's contract.

## Rules

- Never write an uncertain type hint, docstring claim, or rule change
  to disk on a guess — ask first.
- `pr-review` never posts to GitHub, under any framing, even if the
  user insists otherwise.
- `rules` never edits `CLAUDE.md` or any other file; it only prints.
- Standard git hygiene still applies: the user reviews the diff
  (`git diff`) before committing, same as with any other edit.
