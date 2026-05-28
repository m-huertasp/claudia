---
name: nextflow-patterns
description: Production-ready Nextflow DSL2 habits that Claude tends to skip — named functions, input validation, null-safe operators, shell variable escaping, dynamic resource directives, and workflow event handlers. Use this skill whenever writing, reviewing, or refactoring Nextflow workflows, even for seemingly simple tasks, to ensure the output is opinionated and production-ready rather than just technically correct.
---

# Nextflow Production Habits

Claude already knows the common Nextflow patterns (splitCsv, map, branch, filter, collect/join, instanceof List). This skill exists to make sure those patterns are always wrapped in the production scaffolding that is easy to omit but critical in real pipelines.

Apply all four of these habits whenever writing or reviewing Nextflow code.

---

## 1. Extract to Named Functions — Always

Complex `.map{}` closures belong in a `def` function at script level, not inline. This keeps the workflow block readable as a pipeline diagram and makes the logic reusable.

```groovy
// Always do this — the workflow block should read like a flowchart
def parseSampleRow(row) {
    def meta = [
        id:      row.sample_id.toLowerCase(),
        depth:   row.sequencing_depth.toInteger(),   // CSV values are always strings
        quality: row.quality_score.toDouble()
    ]
    def priority = meta.quality > 40 ? 'high' : 'normal'
    return tuple(meta + [priority: priority], file(row.file_path))
}

workflow {
    ch_samples = channel.fromPath(params.input)
        .splitCsv(header: true)
        .map { row -> parseSampleRow(row) }   // one line, not twenty
    PROCESS(ch_samples)
}
```

Never mutate maps in-place — use `meta + [key: value]` to create a new map, since the same object can flow through multiple concurrent operators.

---

## 2. Validate Inputs at the Top — Always

Call a validation function before any channels are created. This produces a clear error message instead of a cryptic mid-run process failure.

```groovy
def validateInputs() {
    if (!params.input)                  error("Specify --input <file.csv>")
    if (!file(params.input).exists())   error("File not found: ${params.input}")
}

workflow {
    validateInputs()
    ch_samples = channel.fromPath(params.input).splitCsv(header: true) ...
}
```

Use `log.warn` (non-fatal) inside parsing functions for data-quality issues on individual samples:

```groovy
if (meta.depth < 20_000_000) log.warn "Low depth for ${meta.id}: ${meta.depth}"
```

---

## 3. Use Safe Navigation for Optional Fields — Always

CSV columns and metadata fields are often absent. Guard every optional field access with `?.` and provide a default with `?:`.

```groovy
// Without this, a missing column causes an immediate NullPointerException
def run_id  = row.run_id?.toUpperCase() ?: 'UNSPECIFIED'
def tissue  = row.tissue_type?.replaceAll('_', ' ')?.toLowerCase() ?: 'unknown'
def deep_id = sample?.run?.id ?: 'UNKNOWN'
```

---

## 4. Escape Shell Variables in Process Scripts — Always

Inside a Nextflow `script:` block, `${var}` is resolved by Groovy. Shell environment variables and command substitutions must be escaped or Nextflow will crash trying to resolve them.

```groovy
script:
"""
echo "Sample: ${meta.id}" > ${meta.id}_report.txt   // Groovy — no escape
echo "User: \${USER}" >> ${meta.id}_report.txt       // shell env var — escape
echo "Host: \$(hostname)" >> ${meta.id}_report.txt   // shell command — escape
"""
```

---

## Bonus: Include These When the Context Calls for Them

**Dynamic resource directives** — use closures that read `meta` or `task.attempt`:

```groovy
cpus   { meta.depth > 40_000_000 ? 4 : 2 }
memory { 4.GB * task.attempt }
errorStrategy 'retry'
maxRetries 3
```

**Workflow event handlers** — add a completion summary for any non-trivial pipeline:

```groovy
workflow.onComplete = {
    def status = workflow.success ? "SUCCESS" : "FAILED"
    println "Pipeline ${status} | duration: ${workflow.duration} | exit: ${workflow.exitStatus}"
    if (!workflow.success) println "Error: ${workflow.errorMessage}"
}
```