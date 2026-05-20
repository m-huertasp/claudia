# Workflow — `/claudia-new`

Produce `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`,
and `.planning/config.json`.

Argument: `$ARGUMENTS` — optional one-line description of the project.

## Steps

1. **Ensure `.planning/` exists** and is gitignored. If `CONTEXT.md` already
   exists from `/claudia-map`, read it and ask stack-aware questions.
2. **Gather vision and scope.** Use `AskUserQuestion` for discrete choices.
   Do not pad thin answers with guesses.
3. **Initialise the config:**
   ```
   claudia config init
   claudia config set mode <chosen>
   claudia config set model_profile <chosen>
   ```
4. **Draft `PROJECT.md`** by rendering the template:
   ```
   claudia template render plugins/claudia-workflow/templates/PROJECT.md \
       --var name=<project> --output .planning/PROJECT.md
   ```
   Then fill in the prose placeholders (`<...>`).
5. **Draft `ROADMAP.md`** by rendering the template:
   ```
   claudia template render plugins/claudia-workflow/templates/ROADMAP.md \
       --var name=<project> --output .planning/ROADMAP.md
   ```
   Replace the example phases with the real ones. Every phase's
   `**Status:**` line must wrap its value in `<!-- claudia:status-N -->...
   <!-- /claudia:status-N -->` so `claudia phase set-status` can transition it.
6. **Initialise `STATE.md`** by rendering the template with starting values:
   ```
   claudia template render plugins/claudia-workflow/templates/STATE.md \
       --var name=<project> \
       --var current_phase="Phase 1 — <title>" \
       --var last_command=/claudia-new \
       --var next_step=/claudia-discuss \
       --var updated=<YYYY-MM-DD> \
       --output .planning/STATE.md
   ```

## Review gate

`ROADMAP.md` is **direction-locking**. Present the drafted `PROJECT.md` and
`ROADMAP.md` and use `AskUserQuestion` for accept / edit / cancel. Follow
the file-based edit loop in `.claude/rules/common/review-gate.md`. On
accept, record it:
```
claudia gate accept ROADMAP.md
```

## Rules

- Do not treat `ROADMAP.md` as final before the explicit accept.
- One project per `.planning/`. If state files already exist, ask before
  overwriting (`--force` flags exist on `config init` and `template render`).
