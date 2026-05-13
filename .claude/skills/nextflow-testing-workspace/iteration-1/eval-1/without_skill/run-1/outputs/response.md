# nf-test Workflow Test for RNASEQ_ALIGN (baseline, no skill)

Complete nf-test file for the `RNASEQ_ALIGN` sub-workflow.

## Test 1: Paired-end, two samples

Covers: `workflow.success`, `workflow.out.bam.size() == 2`, `workflow.out.versions != null`, `workflow.trace.tasks().size() == 4` (STAR_ALIGN × 2 + SAMTOOLS_SORT × 2).

## Test 2: Single-end, one sample

Validates single-end mode: `workflow.out.bam.size() == 1`, `workflow.trace.tasks().size() == 2`.

## Notes

- Uses `${projectDir}/tests/data/` for all file references.
- `workflow.trace.tasks().size()` requires `withTrace true` in `nf-test.config`.
- Snapshot assertion omitted here but should be added for output stability.