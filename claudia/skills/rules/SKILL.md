---
name: rules
description: Inject or refresh the Claudia Rules section in the project's CLAUDE.md so the plugin's always-on rule files are wired in via `@`-imports. Use whenever the user asks to "set up rules", "inject rules", "add the claudia rules", "wire rules into CLAUDE.md", "install rules", "refresh rules", or otherwise mentions configuring CLAUDE.md with the claudia rule set. Idempotent (sentinel-bounded section), detect-aware (picks `common` + `python` / `nextflow` subsets based on `claudia detect`), and creates CLAUDE.md if it does not exist. Invoked via `/claudia rules`. Do NOT auto-trigger on unrelated tasks — callable-only utility skill.
---

# Rules

> Invoke as: `/claudia rules`

**Input**: `$ARGUMENTS` — optional. Currently ignored by the skill. To
target a non-default `CLAUDE.md`, invoke the underlying script with
`--path <CLAUDE.md>` directly.

---

## Purpose

Wire the claudia rule files into the project's `CLAUDE.md` so they
become always-on instructions for any Claude Code session run in this
project. Uses `@`-imports pointing at `${CLAUDE_PLUGIN_ROOT}/rules/...`
— rule content stays single-sourced and refreshes automatically when
the plugin updates.

The skill is **idempotent**: running it twice on the same repo
produces no diff. The section lives under a `## Claudia Rules`
heading and is bounded by `<!-- claudia:rules:start -->` /
`<!-- claudia:rules:end -->` sentinels, so a re-run replaces the
block in place without duplicating. Any `action == "replace"` —
even a no-op refresh — is normal and expected on a second run.

The skill is **detect-aware**: the included rule subsets depend on the
project type detected by `claudia detect`:

| Project type | Subsets included |
|---|---|
| `python` | `common`, `python` |
| `nextflow` | `common`, `nextflow` (when the plugin ships one) |
| `mixed` | `common`, `python`, `nextflow` (when the plugin ships one) |
| `unknown` | `common` only |

Subsets without a corresponding `rules/<subset>/` directory in the
plugin are silently skipped by the helper. The skill, however, must
**not** be silent: when the detected project type implies a subset
that the plugin does not ship (e.g. `mixed` today, where `rules/nextflow/`
does not exist), the skill must explicitly tell the user which subsets
were included and which were skipped, so the missing coverage is visible.

To detect this, compare the detected `project_type` against the
`@`-imports in `data.preview`: if `project_type` is `nextflow` or
`mixed` and no `rules/nextflow/...` lines appear, surface a one-line
note like *"nextflow rules skipped — plugin does not ship `rules/nextflow/` yet."*

## Steps

### 1. Preview the change

Run the deterministic helper in dry-run mode:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia rules inject --dry-run
```

Parse the JSON envelope. The script prints
`{"ok": true, "data": {...}}` on success; extract from `data`:

- `path` — target `CLAUDE.md` location
- `action` — one of `create` / `append` / `replace`
- `project_type` — what `claudia detect` reported
- `rule_count` — how many `@`-imports the section will contain
- `preview` — the would-be section content (only present with `--dry-run`)

On `{"ok": false, "error": ...}` (printed to stderr), surface the
error to the user and stop.

If `path` is not the expected `CLAUDE.md` at the repo root, surface
that to the user so they can intervene before any write.

### 2. Confirm with the user

Show in chat:

- The detected project type
- The action (`create` new file / `append` to existing / `replace`
  stale section)
- The full preview content (markdown), inside a fenced code block

`AskUserQuestion`:

- **Apply** — write the change.
- **Cancel** — do nothing.

In the special case of `action == "replace"` against a `CLAUDE.md`
that already has hand-written content outside the sentinels, suggest
the user back the file up first if they want a safety net —
`cp CLAUDE.md CLAUDE.md.bak` before re-running. Do not perform the
backup automatically. (A replace against a previously-injected file
is a routine refresh and does not need a backup prompt.)

### 3. Apply the change

On *Apply*:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/claudia rules inject
```

Print a one-line summary of the result (action + rule count + path)
so the user can confirm at a glance.

On *Cancel*: stop. Do nothing on disk.

## Rules

- Never hand-edit the sentinel-bounded section; always go through
  `claudia rules inject`.
- The skill is the **only** sanctioned way to wire claudia rules into
  a project. Do not paste rule content into `CLAUDE.md` directly —
  that loses the auto-refresh behaviour and diverges from the
  plugin's source of truth.
- Idempotency is a contract: if running this skill twice in a row
  ever produces a diff (beyond whitespace), it is a bug. The cheap
  field check is `diff CLAUDE.md CLAUDE.md.before` after a back-to-back
  re-run — it must exit `0`.
- The skill never stages or commits changes to `CLAUDE.md`. The user
  reviews the diff and commits when they are ready.
