# Setting Up nf-test for the First Time

## 1. Initializing nf-test

**Install the binary:**

```bash
curl -fsSL https://get.nf-test.com | bash
# or via conda
mamba install -c bioconda nf-test
nf-test --version
```

**Initialize in your project root:**

```bash
cd /path/to/your/nextflow-project
nf-test init
```

This creates `nf-test.config` and the `tests/` directory. You can also scaffold test stubs:

```bash
nf-test generate process modules/local/fastqc/main.nf
nf-test generate workflow main.nf
```

---

## 2. What Goes in nf-test.config

```groovy
config {
    testsDir   "tests"
    workDir    ".nf-test"
    configFile "tests/nextflow.config"
    // profile "test"          // optional: activate a Nextflow profile
    // timeout 600             // seconds per test (default 3600)
    // snapshotMode "never"    // "never" | "always" | "ask"
}
```

| Field | Purpose |
|---|---|
| `testsDir` | Where nf-test looks for `.nf.test` files |
| `workDir` | Scratch space for test execution |
| `configFile` | Nextflow config applied to every test run |
| `timeout` | Max seconds per test before it is killed |

---

## 3. How to Structure the tests/ Directory

**Centralized layout** (mirror the source tree):

```
tests/
├── nextflow.config
├── data/
│   └── reads/
│       ├── sample1_R1.fastq.gz
│       └── sample1_R2.fastq.gz
├── modules/
│   └── local/
│       └── fastqc/
│           └── main.nf.test
├── subworkflows/
│   └── local/
│       └── align_and_sort/
│           └── main.nf.test
└── workflows/
    └── main.nf.test
```

**Example process test** (`tests/modules/local/fastqc/main.nf.test`):

```groovy
nextflow_process {

    name "Test FASTQC process"
    script "modules/local/fastqc/main.nf"
    process "FASTQC"

    test("Should run FastQC on paired-end reads") {

        when {
            process {
                """
                input[0] = [
                    [ id: 'sample1', single_end: false ],
                    [
                        file("${projectDir}/tests/data/reads/sample1_R1.fastq.gz"),
                        file("${projectDir}/tests/data/reads/sample1_R2.fastq.gz")
                    ]
                ]
                """
            }
        }

        then {
            assert process.success
            assert process.out.html.size() == 1
            assert process.out.zip.size() == 1
            assert snapshot(process.out).match()
        }
    }
}
```

---

## 4. tests/nextflow.config to Limit CPU/Memory

```groovy
// tests/nextflow.config — resource limits for nf-test runs

process {
    resourceLimits = [
        cpus:   4,
        memory: '8.GB',
        time:   '1.h'
    ]

    cpus   = 1
    memory = '2.GB'
    time   = '30.m'

    withLabel: 'process_single' {
        cpus   = 1
        memory = '1.GB'
        time   = '10.m'
    }

    withLabel: 'process_low' {
        cpus   = 2
        memory = '2.GB'
        time   = '20.m'
    }

    withLabel: 'process_medium' {
        cpus   = 2
        memory = '4.GB'
        time   = '30.m'
    }

    withLabel: 'process_high' {
        cpus   = 4
        memory = '8.GB'
        time   = '1.h'
    }
}

executor {
    name   = 'local'
    cpus   = 4
    memory = '8.GB'
}

docker.enabled      = false
singularity.enabled = false
conda.enabled       = false

params {
    max_cpus   = 4
    max_memory = '8.GB'
    max_time   = '1.h'
}
```

## Running Tests

```bash
nf-test test                                              # run all tests
nf-test test tests/modules/local/fastqc/main.nf.test     # single file
nf-test test --update-snapshot                           # accept new snapshots
nf-test test --verbose                                   # show Nextflow output
```

Add `.nf-test/` to `.gitignore` but **commit snapshot files** (`.snap`) so regressions are caught in CI.