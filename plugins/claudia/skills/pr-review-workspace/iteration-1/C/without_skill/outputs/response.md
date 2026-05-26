# Trace — Eval C (without_skill, baseline): focus-hint-passthrough

User: `/claudia pr-review 42 focus on the migration, skip style nits`

No skill loaded.

Likely steps:
1. Review PR 42 freeform.
2. Hints "focus on the migration" / "skip style nits" may be honored loosely, but there is no agent prompt to inject them into — the baseline does the review inline. Hints can be dropped, paraphrased, or partially applied (style nits still surface, migration not prioritised).
3. No structured severity ordering, no guarantee the hints reach a downstream component.
4. Without explicit forwarding, the focus on migration may be diluted by general review noise.

End state: hints partially honored at best; no agent passthrough to verify.
