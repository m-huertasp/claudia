# claudia-tools

The deterministic engine behind the [claudia](../README.md) development
workflow. The `claudia` CLI owns every mechanical operation the workflow
needs, so the orchestrating model only ever *reads* state and *judges* — it
never hand-edits planning files.

## What it does

| Module | Responsibility |
|---|---|
| `output` | The `{ok, data, error}` result envelope and error model |
| `markers` | Read/replace HTML-comment-delimited regions in Markdown |
| `state` | Get/update `STATE.md` fields and task checkboxes |
| `config` | Read/validate/update `.planning/config.json` |
| `phase` | List roadmap phases and transition phase status |
| `templates` | Render workflow templates with variable substitution |
| `gates` | Track review-gate acceptance and block advancement |
| `cli` | The `claudia` Click command-line interface |

## Install

```bash
uv tool install ./claudia_tools      # or, for development:
uv sync && uv run claudia --help
```

## Output contract

Every command emits a consistent envelope as JSON on stdout:

```json
{ "ok": true, "data": { ... }, "error": null }
```

Pass `--text` for human-readable output. A failed command writes the envelope
to stderr and exits non-zero.
