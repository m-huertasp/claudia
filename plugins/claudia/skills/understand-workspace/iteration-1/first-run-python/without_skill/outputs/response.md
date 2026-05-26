# Scenario A — first-run-python (baseline, no skill)

User: `/claudia understand` (no skill loaded)

Without the skill, the model has no contract for what `/claudia understand` should do. Likely behaviour:

- Skims the repo with ad-hoc Read/Glob calls.
- Produces a freeform summary in chat.
- Does NOT create `.planning/`, does NOT init `config.json`, does NOT ask about mode.
- Does NOT capture env via the deterministic helper; lists tool versions inline if at all.
- No sentinel-bounded env block; nothing reusable for later phases.
- Does not suggest `/claudia rules` or `/claudia plan` as next steps in a structured way.

End state: chat-only summary, no `.planning/` artefacts, downstream `/claudia plan` would refuse to run.
