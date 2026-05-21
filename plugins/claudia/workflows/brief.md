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
   claudia template render plugins/claudia/templates/ISSUE_BRIEF.md \
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
(or from `$ARGUMENTS` if it was passed).

1. Propose the full branch name to the user via `AskUserQuestion` (allow
   them to edit both the keyword and the description).
2. On confirmation, create and switch to the branch from the current base:
   ```
   git checkout -b <keyword>/<description>
   ```
3. If the working tree is dirty at this point, stop and tell the user.

## Review gate

`ISSUE_BRIEF.md` is **direction-locking**. Present the drafted file and
ask accept / edit / cancel via `AskUserQuestion`. Follow the file-based
edit loop in `plugins/claudia/rules/common/review-gate.md`. On accept,
record clearance:
```
claudia gate accept ISSUE_BRIEF.md
```

## Chain into discuss (intent mode)

Once the brief is accepted, **run the discuss workflow inline in `intent`
mode** — do not require the user to invoke a separate command. Follow
`plugins/claudia/workflows/discuss.md` with:

- Inputs: `ISSUE_BRIEF.md` + `CONTEXT.md`
- Focus: what the issue is, why now, scope boundaries
- Output: a new `## <date> — intent — <topic>` section appended to
  `.planning/DECISIONS.md`

When the intent-mode discuss completes, advance state:
```
claudia state set last_command /claudia-brief
claudia state set next_step /claudia-plan
```

## Rules

- Refuse without `CONTEXT.md`; do not silently bootstrap it.
- Never overwrite existing per-issue artifacts without an explicit user
  choice (archive / overwrite / cancel).
- The branch is created **only** after the user confirms the proposed
  name.
- Do not skip the chained discuss step — the brief alone is not enough
  for `/claudia-plan` to plan well.
