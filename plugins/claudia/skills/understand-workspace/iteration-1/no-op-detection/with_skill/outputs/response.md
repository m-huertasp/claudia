# Scenario B — no-op-detection (with skill)

User: `/claudia understand` (no `refresh` arg, no drift hint)

## State detection
- `.planning/CONTEXT.md` exists.
- `.planning/config.json` exists (mode=pair).
- No `refresh` argument was passed.
- No drift hint from a downstream skill.

→ **No-op** path selected.

## Actions taken

1. Stat-checked `.planning/CONTEXT.md` and `.planning/config.json` — both present.
2. Printed status to user:

> claudia is already bootstrapped for this repo: `.planning/CONTEXT.md` and `.planning/config.json` exist (mode=`pair`). No exploration triggered. Re-run with `/claudia understand refresh` to force a drift pass. Next: `/claudia plan`.

3. **Did not** dispatch researcher or code-explorer.
4. **Did not** rewrite `CONTEXT.md`.
5. **Did not** call `claudia env capture` — env section is left untouched on a no-op.

## Artefacts on disk
- `.planning/CONTEXT.md` — byte-identical to before invocation.
- `.planning/config.json` — byte-identical to before invocation.

## WOULD_DISPATCH
- (none — no-op path)
