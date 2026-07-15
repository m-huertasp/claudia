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
feat: add confidence tiers to add-type-hints inference
fix: stop prepare-docstrings from documenting private symbols
refactor: simplify rule file layout
docs: clarify rules skill output format
test: cover nf-test snapshot regeneration flow
```

## Who follows this

Any commit made on the user's behalf by a skill or agent in this
plugin must match this format. There is no pre-commit hook enforcing
it — self-check before running `git commit`. A bad commit message is
a mistake, not a policy violation — fix it with `git commit --amend`
only if the commit hasn't been pushed yet.
