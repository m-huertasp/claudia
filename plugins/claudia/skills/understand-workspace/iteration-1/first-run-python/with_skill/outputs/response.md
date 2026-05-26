# Scenario A — first-run-python (with skill)

User: `/claudia understand`

## State detection
`.planning/` is missing on disk → **First run** path.

## Actions taken

1. Created `.planning/` and appended `.planning/` to `.gitignore` (file did not previously mention it).
2. Ran `claudia config init` → wrote default `.planning/config.json`.
3. AskUserQuestion: pair vs yolo?
   - Options surfaced: `pair` (default — claudia asks before commits/PRs) and `yolo` (autonomous).
   - User answered `pair` → applied via `claudia config set mode pair`.
4. WOULD_DISPATCH: `researcher` agent — read-only survey (entry points, modules, deps, tests). Larger codebases would also dispatch `code-explorer`; this repo is small, single-package, so researcher alone is enough.
5. Detected stack with `claudia detect`: primary = `python`, evidence = `pyproject.toml`. Cross-checked manifests directly — FastAPI + pydantic, ruff (line-length 100), pytest.
6. Drafted `.planning/CONTEXT.md` with four sections (Stack & architecture, Conventions, Sensitive areas, Environment). Commit-style/formatting marked `<unknown — needs human review>` rather than guessed.
7. Refreshed `## Environment` via the deterministic helper. NB: SKILL.md says `claudia env capture --section` but the installed CLI exposes only `--output PATH`. Used `claudia env capture --output .planning/_env.tmp.md --force` and wrapped the contents in `<!-- claudia:env:start --> ... <!-- claudia:env:end -->` sentinels. **Drift between SKILL.md and the `claudia-tools` CLI flagged for the maintainer.**

## Summary printed to user

> Bootstrap complete. `myapp` is a Python 3.11+ FastAPI project (src layout, ruff, pytest). Mode set to `pair`. No sensitive areas detected. Environment captured via `claudia env capture` and pinned between sentinels. Next: run `/claudia rules` to load the rule pack, then `/claudia plan` to start work.

## Artefacts on disk
- `.planning/config.json` (mode=pair)
- `.planning/CONTEXT.md` (4 sections, env section bounded by sentinels)
- `.gitignore` updated with `.planning/`

## WOULD_DISPATCH
- `researcher` — read-only survey of /tmp/understand-test-first-run-python
- `code-explorer` — **skipped** (small single-package repo, not layered)
