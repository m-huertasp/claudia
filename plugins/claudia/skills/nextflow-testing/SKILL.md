---
name: nextflow-testing
description: Nextflow pipeline testing strategies using nf-test: TDD methodology, process/workflow/function/channel tests, snapshot testing, assertions, parametrization, configuration, and coverage requirements. Use this skill whenever writing, reviewing, or setting up tests for Nextflow pipelines or modules, generating nf-test files, adding assertions to existing tests, configuring nf-test.config, or working with snapshots — even if the user doesn't explicitly say "nf-test".
---
**IMPORTANT** Check whether the project uses `docker`, `singularity`, or `conda` profiles and match `profile` in `nf-test.config` accordingly.

# Nextflow Testing Patterns

## When to Activate

- Writing or reviewing nf-test files for any process, workflow, or function
- Setting up nf-test for the first time in a project
- Updating snapshots or debugging snapshot drift
- Configuring `nf-test.config` or `tests/nextflow.config`

## Snapshot-First Rule

**Always default to snapshotting all outputs.** Then add targeted assertions only for things you care about explicitly.

```groovy
then {
    assert process.success
    assert snapshot(process.out).match()   // captures all channels; catches unintended changes
}
```

Use **named snapshots** when a single test needs multiple independent captures:

```groovy
then {
    assert workflow.success
    assert snapshot(workflow.out.bam).match("bam_files")
    assert snapshot(workflow.out.multiqc).match("multiqc_report")
}
```

Snapshot files (`.nf.test.snap`) are test oracles — **commit them**. A snap diff in a PR is a signal to investigate, not a file to blindly regenerate.

```bash
nf-test test tests/modules/fastqc/main.nf.test --update-snapshot   # intentional changes only
nf-test test tests/modules/fastqc/main.nf.test --clean-snapshot     # remove stale entries (v0.8+)
```

## Test Structure

Four block types map to what you're testing:

| Block | Use for |
|-------|---------|
| `nextflow_process` | A single process |
| `nextflow_workflow` | A named sub-workflow |
| `nextflow_pipeline` | The full `main.nf` entry point |
| `nextflow_function` | A Groovy helper function |

**Process test:**
```groovy
nextflow_process {
    name "Test Process SAMTOOLS_INDEX"
    script "modules/samtools/index/main.nf"
    process "SAMTOOLS_INDEX"
    tag "samtools"

    test("Should produce a .bai index file") {
        when {
            process {
                """
                input[0] = [ [id: 'test', single_end: false],
                             file("${projectDir}/tests/data/test.sorted.bam") ]
                """
            }
        }
        then {
            assert process.success
            assert process.out.bai.size() == 1
            assert snapshot(process.out).match()
        }
    }
}
```

**Workflow test:**
```groovy
nextflow_workflow {
    name "Test Workflow RNASEQ_ALIGN"
    script "workflows/rnaseq.nf"
    workflow "RNASEQ_ALIGN"

    test("Should emit sorted BAM for each sample") {
        when {
            workflow {
                """
                input[0] = Channel.of(
                    [ [id: 'sample1', single_end: false],
                      [ file("${projectDir}/tests/data/R1.fastq.gz"),
                        file("${projectDir}/tests/data/R2.fastq.gz") ] ]
                )
                input[1] = file("${projectDir}/tests/data/star_index")
                """
            }
        }
        then {
            assert workflow.success
            assert workflow.out.bam.size() == 1
            assert workflow.trace.tasks().size() == 2   // requires withTrace true in nf-test.config
            assert snapshot(workflow.out.bam).match()
        }
    }
}
```

## Configuration

### nf-test.config (project root)

```groovy
config {
    testsDir   "tests"
    workDir    ".nf-test"
    configFile "tests/nextflow.config"
    libDir     "tests/lib"
    profile    "docker"       // must be active (not commented out) — match your container backend
    withTrace  true           // required for workflow.trace.tasks() assertions
    autoSort   true           // sort channels for stable snapshots
}
```

### tests/nextflow.config (resource limits for CI)

```groovy
process {
    cpus   = 1
    memory = "2.GB"
    time   = "30.min"

    withName: "STAR_ALIGN" {
        cpus   = 2
        memory = "4.GB"
    }
}

process.errorStrategy = "terminate"   // fail fast — no retries during tests

params {
    max_cpus   = 2
    max_memory = "8.GB"
    max_time   = "2.h"
}
```

## Tags and Selection

```groovy
nextflow_process {
    tag "fastqc"
    tag "slow"
    // ...
    test("...") { tag "integration" }
}
```

```bash
nf-test test . --tag fastqc
nf-test test . --tag "not slow"
nf-test test . --profile +singularity   # add profile on top of default
```

## Key Best Practices

- Use `${projectDir}` for all test data paths — never hardcode absolute paths
- Keep test fixtures tiny (small FASTQ/BAM); large files slow CI and obscure failures
- Add `process.errorStrategy = "terminate"` to `tests/nextflow.config` so failures are immediately visible
- Set `withTrace true` in `nf-test.config` before using `workflow.trace.tasks()`
- Name tests starting with "Should" — e.g. `"Should produce sorted BAM when given unsorted input"`

## Quick Reference

| Pattern | Usage |
|---------|-------|
| `assert snapshot(process.out).match()` | Snapshot all channels (default) |
| `assert snapshot(x).match("name")` | Named snapshot |
| `--update-snapshot` | Regenerate after intentional change |
| `--clean-snapshot` | Remove stale entries |
| `process.out.channel_name` | Named output channel |
| `workflow.trace.tasks().size()` | Count executed tasks |
| `nf-test generate process main.nf` | Scaffold a test file |
| `nf-test test --tag label` | Run tagged subset |