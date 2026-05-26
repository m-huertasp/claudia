# Scenario B — idempotent-refresh (baseline, no skill)

User: `/claudia rules`
Repo: `/tmp/rules-test-idempotent-refresh` (Python, CLAUDE.md already has sentinel block).

Vanilla model has no concept of the sentinel contract. Likely behavior:

> CLAUDE.md already exists. Want me to overwrite it? (Or appends generic
> Python guidance below the existing content, duplicating context.)

Either path breaks idempotency. The model neither runs `claudia rules inject
--dry-run`, nor parses the JSON envelope, nor recognises that an existing
sentinel block means "safe to replace in place without a backup prompt".

## Grading

| Assertion | Pass |
|---|---|
| dry-run reports action=replace | no |
| no backup prompt for previously-injected file | no (likely prompts, or worse, appends) |
| running twice yields zero functional diff | no (would append, growing the file) |
| gate is still shown even on no-op refresh | no |

**Score: 0/4**
