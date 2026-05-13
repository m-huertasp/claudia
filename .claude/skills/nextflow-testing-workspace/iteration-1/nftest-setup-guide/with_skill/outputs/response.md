# Setting Up nf-test for the First Time

## 1. Initializing nf-test

Run once from your project root:

```bash
nf-test init
```

This creates `nf-test.config` at the project root and sets up the `tests/` directory. After that, generate test scaffolds for existing code:

```bash
# For an individual process
nf-test generate process modules/fastqc/main.nf

# For a sub-workflow
nf-test generate workflow workflows/alignment.nf

# For the full pipeline
nf-test generate pipeline main.nf
```

These scaffolds give you the correct block structure — you still fill in inputs and assertions.

---

## 2. What Goes in nf-test.config

`nf-test.config` lives at the project root. Here is a fully annotated example:

```groovy
config {
    testsDir   "tests"                    // where .nf.test files live
    workDir    ".nf-test"                 // working directory for test artefacts
    configFile "tests/nextflow.config"    // test-specific Nextflow config (limits CPU/memory)
    libDir     "tests/lib"                // shared Groovy helpers for tests
    profile    "docker"                   // default container profile
    withTrace  true                       // enable tracing (required for trace assertions)
    autoSort   true                       // sort channels for stable snapshots
}
```

Key points:
- `configFile` wires in `tests/nextflow.config` automatically — no need to pass `-c` on the CLI.
- `profile` must match your container backend (`docker`, `singularity`, or `conda`). Check your main `nextflow.config` profiles first.
- `withTrace true` is required if you plan to use `workflow.trace.tasks()` assertions.
- Commit this file as part of your project's test infrastructure.

---

## 3. How to Structure the tests/ Directory

Mirror your pipeline's module layout inside `tests/`:

```
project/
├── main.nf
├── nf-test.config
├── modules/
│   ├── fastqc/
│   │   └── main.nf
│   └── trimmomatic/
│       └── main.nf
├── workflows/
│   └── alignment.nf
└── tests/
    ├── nextflow.config                  # resource limits for test runs
    ├── lib/                             # shared Groovy helpers (optional)
    ├── data/                            # small test fixtures
    │   ├── samplesheet.csv
    │   ├── sample_R1.fastq.gz
    │   └── sample_R2.fastq.gz
    ├── main.nf.test                     # pipeline-level test
    ├── main.nf.test.snap                # snapshot oracle — commit this
    ├── modules/
    │   ├── fastqc/
    │   │   ├── main.nf.test
    │   │   └── main.nf.test.snap
    │   └── trimmomatic/
    │       ├── main.nf.test
    │       └── main.nf.test.snap
    └── workflows/
        └── alignment/
            ├── main.nf.test
            └── main.nf.test.snap
```

Rules:
- Test files use the `.nf.test` extension.
- Snapshot files (`.nf.test.snap`) are created on the first test run — commit them. They are your test oracle.
- Keep test data small. Large fixtures slow CI and obscure failures.
- Always use `${projectDir}` to reference test data paths, never absolute paths.

Example process test file:

```groovy
// tests/modules/fastqc/main.nf.test
nextflow_process {
    name "Test Process FASTQC"
    script "modules/fastqc/main.nf"
    process "FASTQC"
    tag "fastqc"
    tag "modules"

    test("Should produce html and zip outputs for paired-end reads") {
        when {
            process {
                """
                input[0] = [
                    [ id: 'test_sample', single_end: false ],
                    [ file("${projectDir}/tests/data/sample_R1.fastq.gz"),
                      file("${projectDir}/tests/data/sample_R2.fastq.gz") ]
                ]
                """
            }
        }
        then {
            assert process.success
            assert snapshot(process.out).match()
        }
    }

    test("Should fail gracefully with missing input file") {
        when {
            process {
                """
                input[0] = [ [id: 'bad'], file("nonexistent.fastq.gz") ]
                """
            }
        }
        then {
            assert process.failed
        }
    }
}
```

---

## 4. Configuring tests/nextflow.config to Limit CPU/Memory

`tests/nextflow.config` overrides resource settings so tests don't request excessive CPU/memory on developer machines or in CI:

```groovy
// tests/nextflow.config

process {
    // Global defaults for all processes during tests
    cpus   = 1
    memory = "2.GB"
    time   = "30.min"

    // Per-process overrides where a tool needs slightly more
    withName: "FASTQC" {
        cpus   = 1
        memory = "1.GB"
        ext.args = "--quiet"
    }

    withName: "STAR_ALIGN" {
        cpus   = 2
        memory = "4.GB"
        time   = "1.h"
    }

    withName: "TRIMMOMATIC" {
        cpus   = 1
        memory = "2.GB"
    }
}

// Fail immediately on error — do not retry during tests
process.errorStrategy = "terminate"

// Hard ceiling so no process can accidentally exceed test limits
params {
    max_cpus   = 2
    max_memory = "8.GB"
    max_time   = "2.h"
}
```

This file is picked up automatically via `configFile` in `nf-test.config` — no manual `-c` flag needed.

---

## Putting It All Together

```bash
# 1. Initialize (one-time)
nf-test init

# 2. Generate a test scaffold
nf-test generate process modules/fastqc/main.nf

# 3. Fill in inputs and assertions in the generated .nf.test file

# 4. Run for the first time — creates the snapshot file
nf-test test tests/modules/fastqc/main.nf.test

# 5. Commit both test file and snapshot
git add tests/modules/fastqc/main.nf.test tests/modules/fastqc/main.nf.test.snap

# 6. Run all tests
nf-test test .

# 7. After intentional pipeline changes, regenerate snapshots
nf-test test tests/modules/fastqc/main.nf.test --update-snapshot
```

Key reminders: commit `.nf.test.snap` files, match `profile` to your container backend, keep test fixtures tiny, and set `errorStrategy = "terminate"` so failures are immediately visible.