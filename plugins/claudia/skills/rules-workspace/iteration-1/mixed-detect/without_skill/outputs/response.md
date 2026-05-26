# Scenario C — mixed-repo-detect (baseline, no skill)

User: `/claudia rules`
Repo: `/tmp/rules-test-mixed-detect` (Python + Nextflow, no CLAUDE.md).

Vanilla model does not know `claudia detect` exists. Most likely behavior:

> I see both pyproject.toml and main.nf. Let me write a CLAUDE.md with
> general Python and Nextflow guidance. [Writes ad-hoc content covering
> both stacks, possibly inventing a nextflow style guide.]

No `claudia rules inject`. No JSON envelope. No `@`-imports. No
sentinel block. The baseline cannot know that the plugin does not yet
ship `rules/nextflow/`, so it will likely fabricate nextflow rules or
miss them entirely.

## Grading

| Assertion | Pass |
|---|---|
| project_type=mixed reported | no |
| preview contains python rules, zero nextflow rules | no (either fabricates nextflow or invents content) |
| user message mentions nextflow was skipped | no |
| CLAUDE.md created successfully with action=create | yes (but wrong content) |

**Score: 1/4**
