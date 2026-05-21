# Commit message style

## Format

```
{type}: {description}
```

- **`{type}`** is one of the keywords below — lowercase, no scope.
- **`{description}`** is a single imperative-mood sentence, no period,
  no more than 72 characters. Capitalise only the first word.
- Exactly one blank line, then an optional body explaining *why* (not
  *what* — the diff already shows what).
- Trailers (e.g. `Co-Authored-By:`) are allowed after the body.

Scopes (`feat(api): ...`) are **not** allowed. Pick the right type
instead.

## Types

| type | when to use |
|---|---|
| `add`      | New function, class, or file added |
| `feat`     | New feature visible to the user |
| `remove`   | Removed function, file, or feature |
| `fix`      | Bug fix |
| `update`   | Dependency bump or file refresh that isn't a bug fix |
| `docs`     | Documentation-only change |
| `refactor` | Code restructure with no behavior change |
| `test`     | Added or changed tests only |
| `style`    | Formatting, whitespace, lint fixes — no behavior change |
| `chore`    | Grunt task with no production-code impact |

If a change spans two categories, prefer the more behavior-y one
(`feat` over `add`, `fix` over `refactor`).

## Examples

```
feat: add pair-programming mode to /claudia-execute
fix: stop ship workflow from skipping verify ready check
refactor: lift draft-pr into an internal workflow
docs: clarify CONTEXT.md drift heuristics in verify
test: cover mode=interactive rejection in config tests
```

## Who follows this

- **Executor agent in `yolo` mode** — every commit it creates must
  match this format. The agent dispatcher passes the rule by reference,
  not by paste.
- **You, in `pair` mode** — recommended. The executor will suggest a
  `{type}: {description}` line you can use as-is when you commit.

## Enforcement

There is no pre-commit hook for this rule yet. The executor agent is
expected to self-check before running `git commit`. A bad commit
message is a workflow bug — flag it and use `git commit --amend` (only
for the most recent commit, never published) to fix it.
