# Workflow — `/claudia-brief`

Start work on a new issue. Produces `.planning/ISSUE_BRIEF.md`, proposes
and (after confirmation) creates a `{keyword}/{branch-description}`
branch, then chains into the **intent-mode** discuss step so the user and
the model align on what we're tackling and why before any planning
begins.

Argument: `$ARGUMENTS` — optional one-line description of the issue (used
to seed the brief title and the suggested branch slug).

## Preconditions

1. **Read project context.** `.planning/CONTEXT.md` must exist — if not,
   refuse and tell the user to run `/claudia-understand` first.
2. **Check for in-flight issue artifacts.** If any of `ISSUE_BRIEF.md`,
   `ROADMAP.md`, `STATE.md`, `DECISIONS.md` already exist in `.planning/`,
   ask the user with `AskUserQuestion`:
   - *Archive existing* — move them under `.planning/archive/<YYYY-MM-DD-HHMM>/`.
   - *Overwrite* — delete the current per-issue files.
   - *Cancel* — stop, leave everything as-is.
3. **Check git state.** Refuse to proceed if the working tree is dirty;
   tell the user to stash or commit first.

## Draft the brief

1. **Gather inputs** with `AskUserQuestion`, one cluster at a time:
   - Issue type (`feature` / `bugfix` / `refactor` / `docs` / `chore`)
   - Goal (1–2 sentences)
   - Constraints
   - Out of scope
   - Acceptance criteria (concrete, testable bullets)
   Do not pad thin answers with guesses.
2. **Render `ISSUE_BRIEF.md`** by rendering the template:
   ```
   claudia template render ISSUE_BRIEF \
       --var title=<title> --output .planning/ISSUE_BRIEF.md
   ```
   Fill in the prose placeholders with the gathered answers.

## Propose and create the branch

Branch name follows `{keyword}/{branch-description}`:

| Issue type | Inferred keyword |
|---|---|
| `feature`  | `feat`  |
| `bugfix`   | `fix`   |
| `refactor` | `dev`   |
| `docs`     | `chore` |
| `chore`    | `chore` |

`hotfix` is opt-in only — the user must override to use it.
`{branch-description}` is a kebab-case slug derived from the brief title
(or from `$ARGUMENTS` if it was passed). The branch name is the only
place the issue type is encoded, so it must always match this
convention with a valid keyword (`feat | fix | dev | chore | test |
hotfix`).

1. Detect the current branch with `git rev-parse --abbrev-ref HEAD`. If
   it already matches `{keyword}/{description}` with a valid keyword,
   it is reusable.
2. Propose the branch via `AskUserQuestion`, allowing the user to edit
   both the keyword and the description. When step 1 detected a
   reusable branch, also offer *Use current branch (`<name>`)* as an
   option. If its parsed keyword conflicts with the issue type gathered
   in *Draft the brief*, flag the mismatch and ask the user to resolve
   it (rename the branch, or revisit the issue type) before continuing.
3. On confirmation:
   - *Use current branch* — do not run `git checkout`; we are already
     on it.
   - Otherwise, create and switch from the current base:
     ```
     git checkout -b <keyword>/<description>
     ```
4. If the working tree is dirty at this point, stop and tell the user.

## Review gate

`ISSUE_BRIEF.md` is **direction-locking**. Present the drafted file and
ask accept / edit / cancel via `AskUserQuestion`. Follow the file-based
edit loop in `${CLAUDE_PLUGIN_ROOT}/rules/common/review-gate.md`. On accept,
record clearance:
```
claudia gate accept ISSUE_BRIEF.md
```

## Chain into discuss (intent mode)

Once the brief is accepted, **run the discuss workflow inline in `intent`
mode** — do not require the user to invoke a separate command. Follow
`${CLAUDE_PLUGIN_ROOT}/workflows/discuss.md` with:

- Inputs: `ISSUE_BRIEF.md` + `CONTEXT.md`
- Focus: what the issue is, why now, scope boundaries
- Output: a new `## <date> — intent — <topic>` section appended to
  `.planning/DECISIONS.md`

When the intent-mode discuss completes, **check whether the user
cancelled the gate** before advancing state. The discuss workflow records
its outcome against the mode-scoped gate `DECISIONS:intent`:

```
claudia gate check DECISIONS:intent
```

- If the check **passes** (intent decisions were accepted), advance
  state:
  ```
  claudia state set last_command /claudia-brief
  claudia state set next_step /claudia-plan
  ```
- If the check **fails** (the user cancelled inside discuss, or the
  draft was never accepted), **do not** advance `next_step`. Tell the
  user the intent-mode discuss was cancelled and that `/claudia-brief`
  needs to be re-run to settle the open intent decisions. Stop here.

## Rules

- Refuse without `CONTEXT.md`; do not silently bootstrap it.
- Never overwrite existing per-issue artifacts without an explicit user
  choice (archive / overwrite / cancel).
- The branch is created **only** after the user confirms the proposed
  name — or skipped entirely when the user picks *Use current branch*.
- The current branch is reusable only when its name already matches
  `{keyword}/{description}` with a valid keyword; otherwise the user
  must accept a freshly created branch.
- Do not skip the chained discuss step — the brief alone is not enough
  for `/claudia-plan` to plan well.
