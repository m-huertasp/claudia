# Scenario B — idempotent-refresh (with_skill)

User: `/claudia rules`
Repo: `/tmp/rules-test-idempotent-refresh` (Python repo, CLAUDE.md already has the sentinel-bounded block).

## Step 1 — Preview (dry-run)

Ran:
```
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia rules inject --dry-run --root /tmp/rules-test-idempotent-refresh
```

JSON envelope:
- `action`: `replace`
- `project_type`: `python`
- `rule_count`: `12`

This is a routine refresh — the existing sentinel block is replaced in place.
**No backup prompt** is shown because the previous content was claudia-injected
(sentinels present); per SKILL.md, the backup hint is only for replace actions
where hand-written content lives outside the sentinels.

## Step 2 — Confirm with user

Detected **python**, action=**replace** (refresh). Preview shows the same 12
`@`-imports already present.

`AskUserQuestion` → **Apply** / Cancel. Gate is still shown even on no-op.
(Simulated: Apply.)

## Step 3 — Apply

Ran:
```
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia rules inject --root /tmp/rules-test-idempotent-refresh
```

Snapshot before vs. after re-run:
```
diff CLAUDE.md.before CLAUDE.md
(no output — identical)
```

Ran a second time. Still identical. **Idempotency confirmed.**

## Grading

| Assertion | Pass |
|---|---|
| dry-run reports action=replace | yes |
| no backup prompt for previously-injected file | yes |
| running twice yields zero functional diff (diff exit 0) | yes |
| gate is still shown even on no-op refresh | yes |

**Score: 4/4**
