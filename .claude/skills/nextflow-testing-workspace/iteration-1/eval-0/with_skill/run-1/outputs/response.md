# nf-test for SAMTOOLS_INDEX (with skill)

Here's a complete nf-test file for the `SAMTOOLS_INDEX` process, following the nextflow-testing skill patterns.

## Test file: `tests/modules/samtools/index/main.nf.test`

See `main.nf.test` for the full file.

## Design decisions

1. **Test 1 — Explicit assertions**: Checks `process.success`, `bai` channel size == 1, `.bai` extension, file existence on disk, and `versions` not null.

2. **Test 2 — Snapshot testing**: Uses `assert snapshot(process.out).match()` to snapshot all output channels. Per the skill: "Default to `assert snapshot(process.out).match()` for file outputs".

3. **Test 3 — Meta map preservation**: Verifies that meta map fields (`id`, `single_end`, `strandedness`) pass through unchanged in the output tuple.

4. **Structural patterns applied**:
   - `nextflow_process {}` block with `tag` declarations
   - Descriptive test names starting with "Should"
   - `when { process { ... } }` / `then { }` structure
   - `${projectDir}` references for test data (no hardcoded paths)
   - Three focused tests, each verifying a distinct behavior