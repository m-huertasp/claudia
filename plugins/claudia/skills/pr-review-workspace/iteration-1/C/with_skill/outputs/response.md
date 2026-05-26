# Trace — Eval C (with_skill): focus-hint-passthrough

User: `/claudia pr-review 42 focus on the migration, skip style nits`

Skill load: claudia:pr-review. Contract says pass user-supplied focus / "skip X" hints through to the subagent.

Steps:
1. Parse args: ref=42, focus="the migration", skip="style nits".
2. WOULD_DISPATCH: pr-reviewer with
     ref=42,
     cwd=$PWD,
     focus="the migration" (forwarded verbatim),
     skip="style nits" (forwarded verbatim, mapped to: drop LOW style findings),
     reminder="read-only gh only, never post or mutate, return Markdown verbatim".
3. Receive agent output. Expectation: the agent's Findings sections weight URGENT/HIGH around the migration, and the LOW section is `_None_` or trimmed.
4. Surface Markdown verbatim.
5. Post-review options line offered, no posting option.
6. No GitHub mutation.

End state: focus + skip hints reached the agent prompt unmodified; review narrowed accordingly.
