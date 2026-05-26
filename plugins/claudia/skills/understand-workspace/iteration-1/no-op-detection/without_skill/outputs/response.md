# Scenario B — no-op-detection (baseline, no skill)

Without the skill, the model has no rule for "already bootstrapped = no-op". Likely behaviour:

- Re-explores the repo, re-summarises in chat.
- May overwrite `.planning/CONTEXT.md` with a fresh draft, **destroying any human edits**.
- Does not check whether `config.json` already exists before running `claudia config init` (which would also stomp the existing config).
- Wastes a researcher dispatch.

End state: idempotence violated; user's curated CONTEXT.md may be lost.
