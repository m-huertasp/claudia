# Scenario A — python-create-claude-md (baseline, no skill)

User: `/claudia rules`
Repo: `/tmp/rules-test-python-create` (pyproject.toml, src/, no CLAUDE.md)

Vanilla model with no skill loaded. The model does not know about the
`claudia rules inject` helper or the sentinel contract. Most likely behavior:

> I'll create a `CLAUDE.md` for you with some Python project guidance.
> [Writes ad-hoc content: "Use type hints, follow PEP 8, prefer pytest..."]

No dry-run preview. No `AskUserQuestion` gate. No `@`-imports to plugin rules.
No sentinel block, so the next `/claudia rules` run would not be idempotent —
it would `append` and duplicate content.

## Grading

| Assertion | Pass |
|---|---|
| preview rendered with action=create, project_type=python | no |
| gate prompt shown before any disk write | no |
| CLAUDE.md created at repo root | yes (but with wrong content) |
| section contains `@${CLAUDE_PLUGIN_ROOT}/rules/python/coding-style.md` | no |

**Score: 1/4**
