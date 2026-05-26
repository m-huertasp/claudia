# Scenario C — refresh-flow (baseline, no skill)

Without the skill, the model has no contract for "refresh = diff + gate + env-always". Likely behaviour:

- Treats `refresh` as a freeform instruction.
- May overwrite `CONTEXT.md` wholesale without showing a diff.
- May skip the env section entirely, or re-write it without sentinels (breaking later replacements).
- May "helpfully" also re-run `claudia config init`, stomping the user's mode choice.
- No AskUserQuestion gate before applying narrative changes.

End state: lossy refresh; env block likely loses sentinel boundaries; config may be reset.
