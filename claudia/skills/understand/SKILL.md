---
name: understand
description: One-time codebase bootstrap for the claudia framework — analyses stack, architecture, conventions, and sensitive areas, captures local tool versions, and writes `.planning/CONTEXT.md` and `.planning/config.json`. Use when the user says things like "understand this codebase", "map the repo", "explore this project", "analyze the codebase", "bootstrap claudia", or asks claudia to onboard onto an unfamiliar repository. Invoked via `/claudia understand [focus|refresh]`. Re-runnable as a refresh when later phases detect drift. Do NOT auto-trigger from incidental mentions of "understanding" code — this is a callable-only workflow skill; fire only when explicitly invoked through `/claudia` or when the user clearly asks claudia to perform the bootstrap.
---

# Understand

> Invoke as: `/claudia understand [focus|refresh]`

**Input**: $ARGUMENTS — optional. A subdirectory or subsystem to focus the
exploration on, or the literal token `refresh` to force a CONTEXT.md drift pass
on an already-initialized repo.

---

## Purpose

Bootstrap the per-project artefacts the rest of the claudia workflow depends on:

- `.planning/CONTEXT.md` — narrative project context with four sections (Stack & architecture, Conventions, Sensitive areas, Environment). The `## Environment` section is mechanically refreshed by `claudia env capture --section` and is bounded by `<!-- claudia:env:start -->` / `<!-- claudia:env:end -->` sentinels — **never hand-edit between those sentinels**; the helper rewrites the block in place. The other three sections are narrative and edited freely.
- `.planning/config.json` — slim claudia config: `mode` (`pair`|`yolo`) and `agents.*` toggles.

Together these are *project-level* — they live for the lifetime of the project and are re-used by every issue. Do not write per-task artefacts here. There is no separate `ENVIRONMENT.md`; environment data is a section inside `CONTEXT.md`.

## Detect state

Decide which path to take based on what already exists in `.planning/`:

| State on disk | Action |
|---|---|
| `.planning/` missing or empty | **First run** |
| `CONTEXT.md` + `config.json` exist, no `refresh` arg, no drift hint | **No-op** — print status, suggest `/claudia plan` |
| `refresh` arg given, or drift flagged by a downstream skill | **Refresh** |

## First run

1. **Ensure `.planning/` exists.** Create the directory if needed. Add `.planning/` to `.gitignore` unless the user has opted in to tracking it (ask only if the file does not already mention `.planning`).

2. **Initialise config.** Run the deterministic helper:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia config init
   ```
   Then ask the user which mode they want via `AskUserQuestion`:
   - `pair` — claudia asks before every commit and PR (default, safer)
   - `yolo` — claudia commits and pushes autonomously after each gate

   Apply the choice:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia config set mode <choice>
   ```

3. **Explore the codebase.** Always dispatch the `researcher` agent for a read-only survey: entry points, module layout, data flow, dependencies, test conventions. Honour the `$ARGUMENTS` focus hint if given.

   Additionally dispatch the `code-explorer` agent for a deep architecture trace **only** when any of these concrete triggers fire — otherwise `researcher`'s high-level survey is enough:

   - `$ARGUMENTS` names a specific subsystem (e.g. `/claudia understand auth` or `/claudia understand src/services`) → the user is asking for depth on that area; dispatch `code-explorer` scoped to it.
   - `claudia detect` reports `mixed` or `nextflow` AND the repo has a `subworkflows/` directory or more than 10 `.nf` files under `modules/` + `workflows/` combined.
   - The repo has more than 8 top-level subdirectories under `src/` (Python) — a signal that the codebase is layered into services / domains / applications and `researcher`'s flat survey will miss the call chain.
   - The user explicitly passed `trace` as an argument (e.g. `/claudia understand trace`).

   When none of these fire, skip `code-explorer` — it duplicates `researcher`'s work on small, flat repos and just burns tokens. The distinction is: `researcher` answers *what's here?*; `code-explorer` answers *how does the call chain flow?*.

4. **Detect the stack.** Read manifests directly — `pyproject.toml`, `setup.py`, `nextflow.config`, `main.nf` — and identify language, version, package manager, test runner, lint/type tooling. Cross-check with the deterministic helper:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia detect
   ```

5. **Identify sensitive areas.** Data directories, credential files, embargoed or patient data, internal-only modules. Never read or quote the contents of those areas.

6. **Draft `CONTEXT.md`.** Create `.planning/CONTEXT.md` with these sections in order:

   ```markdown
   # Project context

   ## Stack & architecture
   <narrative — language(s), package manager, test runner, key modules, entry points, data flow>

   ## Conventions
   <narrative — naming, formatting, commit style, branch naming, test layout>

   ## Sensitive areas
   <narrative — directories/files to avoid reading; credentials; embargoed data>

   ## Environment
   <managed by `claudia env capture --section` — do not hand-edit>
   ```

   Write only what you verified. Mark anything uncertain as `<unknown — needs human review>` rather than guessing.

7. **Capture the environment section.** Refresh the `## Environment` section with the deterministic helper:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia env capture --section
   ```
   The section is bounded by `<!-- claudia:env:start -->` / `<!-- claudia:env:end -->` sentinels, so re-runs replace cleanly without duplication.

8. **Summarise.** Print a one-paragraph summary of what was written: project type, mode, sensitive areas, tooling. Suggest `/claudia rules` as the natural next step, followed by `/claudia plan` to start work.

## Refresh

1. **Re-explore** the same areas, honouring the `$ARGUMENTS` focus hint if given. Dispatch `researcher` for read-only survey.
2. **Re-render** the narrative sections (`Stack & architecture`, `Conventions`, `Sensitive areas`) against current repo state into a scratch file, then `diff` against the existing `CONTEXT.md`.
3. **Show the diff** to the user via `AskUserQuestion`:
   - *Apply diff* — write the refreshed narrative.
   - *Edit before applying* — write the scratch file to `.planning/CONTEXT.md.draft` so the user can edit it; on save, replace.
   - *Cancel* — leave `CONTEXT.md` untouched.
4. **Refresh the env section** regardless of the narrative outcome:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia env capture --section
   ```
5. **`config.json` is left alone** unless the user explicitly opts in — changes to mode/agents go through a manual `claudia config set`.

## Review gate

`CONTEXT.md` is reference material, not direction-locking. On first run, present the summary so the user can correct it before later phases rely on it. On a refresh, the file-based diff is the gate.

## Rules

- Report only what you verified. Uncertain claims become `<unknown>` placeholders, not guesses.
- Never read or quote contents of files in sensitive areas.
- Never hand-edit the `## Environment` section — always go through `claudia env capture --section`.
- `/claudia plan` and downstream skills refuse to run without `CONTEXT.md`. This skill is the only way to create it.
