# nf-test for RNASEQ_ALIGN workflow (with skill)

Complete nf-test workflow test for the `RNASEQ_ALIGN` sub-workflow, following the nextflow-testing skill patterns.

## Design decisions

1. **Test 1 — Success baseline**: Single sample, asserts `workflow.success` only. Lightweight smoke test.

2. **Test 2 — BAM channel size**: Two samples, asserts `workflow.out.bam.size() == 2`, `workflow.out.versions != null`, plus a named snapshot `("bam_outputs")` for output stability.

3. **Test 3 — Task count**: Single sample, uses `workflow.trace.tasks().size() == 2` and `workflow.trace.succeeded().size() == 2` to confirm exactly STAR_ALIGN + SAMTOOLS_SORT ran.

## Skill patterns applied

- `nextflow_workflow {}` block with `script`, `workflow`, and `tag` fields
- `input[0]` / `input[1]` notation inside `workflow {}` block
- `Channel.of(...)` with meta+fastq tuples for `input[0]`
- `${projectDir}/tests/data/` for all test data paths
- Named snapshot (`"bam_outputs"`) for selective output capture
- Descriptive test names starting with "Should"