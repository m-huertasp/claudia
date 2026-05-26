# Scenario C — mixed-repo-detect (with_skill)

User: `/claudia rules`
Repo: `/tmp/rules-test-mixed-detect` (pyproject.toml + main.nf, no CLAUDE.md).

## Step 1 — Preview (dry-run)

Ran:
```
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia rules inject --dry-run --root /tmp/rules-test-mixed-detect
```

JSON envelope:
- `action`: `create`
- `project_type`: `mixed`
- `rule_count`: `12` (7 common + 5 python; **zero nextflow**)

The plugin does not currently ship a `rules/nextflow/` directory, so the
nextflow subset is silently skipped by the helper (per
`_collect_rule_files`). Per SKILL.md, the skill should communicate this
clearly.

## Step 2 — Confirm with user

> Detected **mixed** project (Python + Nextflow). I'm going to inject
> **common + python** rules only — the plugin does not yet ship a
> `rules/nextflow/` directory, so those rules are skipped. 12 `@`-imports
> total. Action: `create`.

`AskUserQuestion` → **Apply** / Cancel. (Simulated: Apply.)

## Step 3 — Apply

Result: `action=create rule_count=12 project_type=mixed`.

Verified: `grep -c nextflow CLAUDE.md` → 0.

## Grading

| Assertion | Pass |
|---|---|
| project_type=mixed reported | yes |
| preview contains python rules, zero nextflow rules | yes |
| user message mentions nextflow was skipped (only common+python included) | yes |
| CLAUDE.md created successfully with action=create | yes |

**Score: 4/4**

## Observation (improvement candidate)

The JSON envelope from `claudia rules inject` does **not** include an
explicit `skipped_subsets` field — the model has to infer "nextflow was
skipped" from `project_type=mixed` + the plugin layout. Mentioned in
final report as a candidate enhancement for the script (out of scope for
this iteration).
