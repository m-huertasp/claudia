# Review Gate

## Purpose

Every **direction-locking** artifact — one that, once accepted, constrains all
later work — passes through a review gate before it is treated as final. The
gate keeps the user in control: `claudia` may draft, but only the user locks
direction. Direction-locking artifacts include `ROADMAP.md`, `DECISIONS.md`,
the `STATE.md` task breakdown, and any drafted PR or issue body.

## The gate

When a direction-locking artifact is ready, present it and ask the user, with
`AskUserQuestion`, for one of three outcomes:

- **Accept** — the artifact is final. Keep it written; continue the workflow.
- **Edit** — the user wants changes first. Run the edit loop below.
- **Cancel** — discard the artifact. Delete any draft file created this session
  and stop.

## The edit loop (file-based)

`claudia` artifacts are files, so editing happens **in the file**, not as a
chat transcript — the user opens it in their editor and changes it directly.

1. **Write the current draft to its real path** (e.g. `.planning/ROADMAP.md`).
   The file is a *draft* — not final — until the user accepts it.
2. **Surface the file** to the user as a clickable path and tell them it is
   open for editing. They may edit and save it in their editor, or describe
   the change in chat for `claudia` to apply. Chat-supplied rewrites are used
   verbatim — do not paraphrase them.
3. **Wait** for the user to signal that editing is done.
4. **Re-read the file from disk** — the saved file is now the new draft.
5. **Re-present the gate** (accept / edit / cancel) on the updated draft.
6. Repeat until the user accepts or cancels.

A draft file existing on disk is never the same as acceptance. Do not advance
the workflow, commit, or push on the basis of an unaccepted draft.

## Example

```
/claudia-new drafts PROJECT.md + ROADMAP.md
   │
   ▼  AskUserQuestion: accept / edit / cancel
   ├─ accept  → files are final; next step → /claudia-discuss
   ├─ edit    → write drafts to .planning/*.md → user edits & saves
   │            → re-read → re-present gate  ⤴
   └─ cancel  → delete the draft files; stop
```

## Rules

- Never skip the gate for a direction-locking artifact. It is not configurable
  and cannot be disabled by any `config.json` setting.
- The draft file is the editing surface — do not re-paste long drafts into
  chat when the user can edit the file directly.
- On accept, the artifact stands as written on disk; on cancel, leave no
  draft behind.
