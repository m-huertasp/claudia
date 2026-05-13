# Setting Up nf-test for the First Time

## 1. Initializing nf-test

Install and initialize from the project root:

```bash
curl -fsSL https://get.nf-test.com | bash
cd /path/to/your-pipeline
nf-test init
```

`nf-test init` produces `nf-test.config` at the root and a `tests/` directory. To scaffold a test file from an existing process:

```bash
nf-test generate process modules/fastqc/main.nf
```

---

## 2. What Goes in nf-test.config

```groovy
config {
    testsDir   "tests"
    workDir    ".nf-test"
    configFile "tests/nextflow.config"
    libDir     "tests/lib"
    profile    "docker"      // match your backend: docker / singularity / conda
    withTrace  true          // required for workflow.trace.tasks() assertions
    autoSort   true          // stable, order-independent snapshots
}
```

The most common first-run mistake: `profile` does not match your container backend.

Add `.nf-test/` to `.gitignore`. Snapshot files (`*.nf.test.snap`) are test oracles — commit them.

---

## 3. How to Structure the tests/ Directory

Mirror your pipeline layout:

```
tests/
├── nextflow.config
├── data/
│   ├── test.R1.fastq.gz
│   └── test.sorted.bam
├── modules/
│   ├── fastqc/main.nf.test
│   └── samtools/index/main.nf.test
└── workflows/
    └── rnaseq/main.nf.test
```

Always use `${projectDir}` for paths — never hardcode absolute paths. Keep fixtures tiny.

---

## 4. Configuring tests/nextflow.config to Limit CPU/Memory

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

process.errorStrategy = "terminate"

params {
    max_cpus   = 2
    max_memory = "8.GB"
    max_time   = "2.h"
}
```