---
name: rules
description: Show the Claudia rule set (common + Python conventions) as a ready-to-paste `@`-imports block for a project's CLAUDE.md. Read-only — never edits any file. Use whenever the user asks to "set up rules", "show me the claudia rules", "what rules does claudia ship", "add the claudia rules to this project", or otherwise wants to see or wire the plugin's rule files into their own CLAUDE.md.
---

# Rules

**Input**: none required.

---

## Purpose

Surface the rule files bundled with this plugin
(`${CLAUDE_PLUGIN_ROOT}/rules/`) as a copy-pasteable `@`-imports block,
so the user can wire them into their own project's `CLAUDE.md` by hand.

This skill is **read-only**. It never writes, edits, or otherwise
touches any file outside the plugin's own `rules/` directory — not the
current project's `CLAUDE.md`, not any other file. It only prints
content to chat. If the user wants the block applied, they paste it
themselves, or ask the model directly to edit their `CLAUDE.md` as a
separate, explicit action outside this skill.

## Steps

### 1. List the available rule files

List the `.md` files under each subset directory that actually exists
in `${CLAUDE_PLUGIN_ROOT}/rules/` (currently `common/` and `python/` —
a `nextflow/` subset may or may not exist depending on the plugin
version; include it only if the directory is present).

### 2. Detect the project type (best-effort, informational only)

Look at the current project root for:

- **Python markers**: `pyproject.toml`, `setup.py`, `requirements.txt`
- **Nextflow markers**: `main.nf`, `nextflow.config`, or `.nf` files
  under `modules/`, `workflows/`, `subworkflows/`

This only decides which subsets to *recommend* in the printed block —
it does not gate anything. If both or neither match, say so and offer
`common` as the safe default plus whichever subsets exist.

### 3. Print the block

Print a fenced Markdown code block the user can paste as-is into their
project's `CLAUDE.md`, e.g.:

```markdown
## Claudia Rules

@${CLAUDE_PLUGIN_ROOT}/rules/common/code-review.md
@${CLAUDE_PLUGIN_ROOT}/rules/common/coding-style.md
@${CLAUDE_PLUGIN_ROOT}/rules/common/commit-style.md
@${CLAUDE_PLUGIN_ROOT}/rules/common/patterns.md
@${CLAUDE_PLUGIN_ROOT}/rules/common/security.md
@${CLAUDE_PLUGIN_ROOT}/rules/common/testing.md
@${CLAUDE_PLUGIN_ROOT}/rules/python/coding-style.md
@${CLAUDE_PLUGIN_ROOT}/rules/python/fastapi.md
@${CLAUDE_PLUGIN_ROOT}/rules/python/patterns.md
@${CLAUDE_PLUGIN_ROOT}/rules/python/security.md
@${CLAUDE_PLUGIN_ROOT}/rules/python/tests.md
```

List only the subsets relevant per step 2 (drop the `python/` lines
for a non-Python project, etc.). Note that `${CLAUDE_PLUGIN_ROOT}`
resolves automatically at Claude Code's import time — the user does
not need to substitute anything.

### 4. Tell the user what to do with it

One short line: "Paste this into your project's `CLAUDE.md` (create
the file if it doesn't exist). Re-run this skill any time the plugin's
rule set changes to get an updated block."

## Rules

- **Never write to any file.** Not `CLAUDE.md`, not anything else.
  This skill's entire output is chat text.
- Do not fabricate rule files — only list `.md` files that actually
  exist on disk under `${CLAUDE_PLUGIN_ROOT}/rules/`.
- If the user pushes back and asks you to just apply it directly to
  their `CLAUDE.md`, that is a legitimate separate request you can
  fulfill with the `Edit`/`Write` tool as a normal file edit — just not
  as part of *this* skill's contract. Make that distinction clear if
  it comes up.
