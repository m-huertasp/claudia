---
description: Comprehensive Nextflow pipeline review for a single file, module, or full pipeline. Generates a local review artifact.
agent: code-reviewer
---

# Nextflow Pipeline Review

> Designed to run with the `@code-reviewer` agent. Invoke as: `@code-reviewer /nextflow-review <path>`

**Input**: $ARGUMENTS

---

## Nextflow Review Mode

Comprehensive Nextflow-specific code review — reads full pipeline files, resolves includes, runs available linting, generates a local review artifact.

### Phase 1 — PARSE

Parse the input to determine the review target:

| Input | Action |
|---|---|
| `.nf` file path (e.g. `workflows/align.nf`) | Review that single file |
| Folder / repo path (e.g. `modules/` or `.`) | Recursively find all `.nf` and `nextflow.config` files |
| No input | Default to current working directory |

Resolve the path to absolute. If the target does not exist, stop with an error.

Derive the **artifact name** from the target:
- Single file → basename without extension (e.g. `align.nf` → `align`)
- Folder → folder name (e.g. `modules/` → `modules`, `.` → repo root name)

Artifact will be written to `.github/nf-<NAME>-review.md`.

### Phase 2 — CONTEXT

Build review context:

1. **Project rules** — Read `copilot-instructions.md` and any contributing guidelines found in the repo
2. **Nextflow version** — Check `nextflow.config` for `nextflowVersion` and DSL version (`nextflow.enable.dsl = 2`)
3. **nf-core** — Detect if the pipeline follows nf-core conventions (presence of `nf-core-*` files, `lib/`, `conf/` layout); apply nf-core-specific checks if so
4. **Container strategy** — Detect whether the pipeline uses Docker, Singularity, Conda, or a mix (from `profiles` in `nextflow.config`)
5. **File list** — Enumerate all `.nf` and `nextflow.config` files in scope

### Phase 3 — REVIEW

Read each file **in full**. Resolve `include { ... } from '...'` statements and read included modules when their interface is relevant to a finding.

Apply the review checklist across 7 categories:

| Category | What to Check |
|---|---|
| **Correctness** | Channel logic errors, wrong cardinality, missing `first()`/`collect()`, incorrect `join`/`combine` keys |
| **Security** | Secrets in `params`, `shell=true`-equivalent, user input unsanitised in `script:` blocks |
| **Reproducibility** | Pinned container tags, `cache` directives, deterministic output file names |
| **Resource Management** | Hardcoded CPUs/memory, missing `label`, missing or misconfigured `errorStrategy` |
| **Code Quality** | Groovy logic in `script:` blocks, unquoted variables, unused channels, dead processes |
| **Completeness** | Missing `stub:` blocks, missing input/output validation, no `workflow.onError` handler |
| **Maintainability** | Naming conventions, magic numbers in resource values, overly long processes, undocumented params |

Assign a severity to each finding:

| Severity | Meaning |
|---|---|
| **CRITICAL** | Security vulnerability or pipeline correctness failure — must fix |
| **HIGH** | Bug or logic error that will cause wrong results or crashes — should fix |
| **MEDIUM** | Code quality issue or missing best practice — fix recommended |
| **LOW** | Style nit or minor suggestion — optional |

#### Confidence-Based Filtering

Only report issues you are **>80% confident** are real problems. Consolidate similar issues (e.g., "4 processes missing `label`" not 4 separate findings).

#### CRITICAL — Must Fix

- Secrets or credentials interpolated directly into `script:` blocks via `params`
- Unvalidated user-controlled values used in shell commands (`shell=true`-style interpolation)
- Pipeline silently producing incorrect results due to channel cardinality bugs (e.g., `join` on mismatched keys)
- Pinned container tags replaced with `latest` — breaks reproducibility

#### HIGH — Should Fix

- Missing `errorStrategy` on processes that can fail transiently (I/O, network, HPC preemption)
- Hardcoded CPU/memory values — use params or resource profiles
- Unquoted Nextflow variables in `script:` blocks causing word-splitting (e.g., `$sample` vs `"${sample}"`)
- Output channels not consumed or a single channel consumed multiple times without `.multiMap`/`.branch`
- Groovy business logic embedded in `script:` blocks — extract to a helper script
- Missing `label` on processes — cannot target resource profiles

```nextflow
// BAD: hardcoded resources, unquoted variable, no errorStrategy
process ALIGN {
    cpus 8
    memory '32 GB'
    script:
    """
    bwa mem -t 8 $ref $reads > out.sam
    """
}

// GOOD:
process ALIGN {
    label 'high_cpu'
    errorStrategy 'retry'
    maxRetries 2
    script:
    """
    bwa mem -t ${task.cpus} "${ref}" "${reads}" > out.sam
    """
}
```

#### MEDIUM — Fix Recommended

- Processes emitting to `publishDir` that are not final outputs — publish only terminal results
- Missing `stub:` block on long-running processes — prevents `-stub` dry-run testing
- Non-deterministic output file names (globbing with `*` when exact names are predictable)
- Container image not pinned to a digest or versioned tag
- Params not declared in `nextflow.config` `params` block with defaults and validation
- Missing `workflow.onError` or `workflow.onComplete` handlers for pipeline-level logging
- `cache` not set to `true` on expensive processes — forces full re-run on resume

```nextflow
// BAD: unpinned image, no stub
process CALL_VARIANTS {
    container 'gatk:latest'
    script: ...
}

// GOOD:
process CALL_VARIANTS {
    container 'broadinstitute/gatk:4.5.0.0'
    stub:
    """
    touch variants.vcf
    """
    script: ...
}
```

#### LOW — Optional

- Process names not in `UPPER_SNAKE_CASE`
- Workflow names not in `camelCase`
- TODO/FIXME comments without issue references
- Magic numbers in resource values (e.g., `cpus 4` — extract to a named param)
- Undocumented `params` entries (no comment explaining purpose and valid values)

#### nf-core-Specific Checks (when nf-core conventions detected)

- Modules not following the nf-core module template (`main.nf`, `meta.yml`, `tests/`)
- `meta` map not threaded through all processes that handle sample-level data
- Missing `versions.yml` emission from processes
- `samplesheet_check` not validated at pipeline entry
- `lib/WorkflowMain.groovy` not used for parameter validation

### Phase 4 — VALIDATE

Run available tools against the target path. Detect which tools are installed before running:

```bash
# Nextflow syntax check
nextflow -quiet run <TARGET> -stub-run --dry-run 2>&1 || nextflow lint <TARGET>

# nf-core lint (if nf-core pipeline detected)
nf-core lint

# nf-test (if test suite exists)
nf-test run

# YAML/JSON config validation
python -c "import yaml, sys; yaml.safe_load(open('nextflow.config'))" 2>/dev/null || true
```

Skip tools that are not installed. Record **Pass / Fail / Skipped** for each.

### Phase 5 — DECIDE

Form a recommendation:

| Condition | Decision |
|---|---|
| Zero CRITICAL/HIGH issues, validation passes | **PASS** — approve |
| Only MEDIUM/LOW issues, validation passes | **WARNING** — merge with caution |
| Any HIGH issues or validation failures | **FAIL** — fix before merge |
| Any CRITICAL issues | **BLOCK** — must fix before merge |

### Phase 6 — REPORT

Create a **local** review artifact at `.github/nf-<NAME>-review.md`. Do not post or publish anything.

```markdown
# Nextflow Review: <TARGET>

**Reviewed**: <date>
**Decision**: PASS | WARNING | FAIL | BLOCK
**DSL Version**: DSL2 / DSL1 / unknown
**nf-core**: Yes / No

## Summary
<1–2 sentence overall assessment>

## Findings

### CRITICAL
<findings or "None">

### HIGH
<findings or "None">

### MEDIUM
<findings or "None">

### LOW
<findings or "None">

## Validation Results

| Check | Result |
|---|---|
| nextflow lint / stub-run | Pass / Fail / Skipped |
| nf-core lint | Pass / Fail / Skipped |
| nf-test | Pass / Fail / Skipped |

## Files Reviewed
<list of .nf and config files reviewed>
```

### Phase 7 — OUTPUT

Report to the user:

```
Nextflow Review: <TARGET>
Decision: <PASS|WARNING|FAIL|BLOCK>

Issues: <critical_count> critical, <high_count> high, <medium_count> medium, <low_count> low
Validation: <pass_count>/<total_count> checks passed

Artifact: .github/nf-<NAME>-review.md

Next steps:
  - <contextual suggestions based on decision>
```

---

## Common Fixes

### Quote All Variables in Script Blocks

```nextflow
// Before
script:
"""
tool -i $input -o $output
"""

// After
script:
"""
tool -i "${input}" -o "${output}"
"""
```

### Use Labels for Resource Profiles

```nextflow
// Before
process HEAVY_TASK {
    cpus 16
    memory '64 GB'
    ...
}

// After — in nextflow.config
process {
    withLabel: 'high_mem' {
        cpus = 16
        memory = '64 GB'
    }
}

// In process
process HEAVY_TASK {
    label 'high_mem'
    ...
}
```

### Add errorStrategy

```nextflow
// Before
process DOWNLOAD {
    script: ...
}

// After
process DOWNLOAD {
    errorStrategy { task.attempt <= 3 ? 'retry' : 'finish' }
    maxRetries 3
    script: ...
}
```

### Move Secrets Out of Params

```nextflow
// Before — params.token interpolated in script
script:
"""
api_call --token ${params.token}
"""

// After — use Nextflow secrets or environment variables
secret 'API_TOKEN'
script:
"""
api_call --token "$API_TOKEN"
"""
```

### Add Stub Block

```nextflow
// Before
process RUN_ANALYSIS {
    input: path data
    output: path "results.tsv"
    script:
    """
    run_analysis.py ${data} > results.tsv
    """
}

// After
process RUN_ANALYSIS {
    input: path data
    output: path "results.tsv"
    stub:
    """
    touch results.tsv
    """
    script:
    """
    run_analysis.py "${data}" > results.tsv
    """
}
```

---

## Edge Cases

- **No `.nf` files found** in the target folder → stop with a clear error.
- **DSL1 pipeline** → note it, apply DSL1-compatible checks; do not flag DSL2 patterns as missing.
- **Large pipelines (>30 processes)** → warn about scope; review main workflow first, then subworkflows, then individual modules.
- **Missing tools** → skip gracefully; note which tools were not available in the report.
- **ASK IF DOUBTS, do not suppose.**
