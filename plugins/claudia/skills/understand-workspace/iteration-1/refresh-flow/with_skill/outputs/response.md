# Scenario C — refresh-flow (with skill)

User: `/claudia understand refresh`

## State detection
- `.planning/CONTEXT.md` exists, `.planning/config.json` exists.
- `$ARGUMENTS == "refresh"` → **Refresh** path.

## Actions taken

1. WOULD_DISPATCH: `researcher` agent — re-survey the repo with the same scope as first run, honouring any focus arg (none here).
2. Re-rendered the three narrative sections (Stack & architecture, Conventions, Sensitive areas) into a scratch file `.planning/CONTEXT.md.refresh-draft`.
3. Diffed the scratch file against the live `CONTEXT.md`. Key drift detected:
   - **Stack & architecture**: SQLAlchemy added as a dependency since last bootstrap.
   - **Conventions**: clarified that no formatter is configured.
4. Surfaced the diff via AskUserQuestion (apply / edit / cancel):
   - *Apply* — overwrite narrative sections in `CONTEXT.md` with the scratch file.
   - *Edit before applying* — keep `CONTEXT.md.refresh-draft` for the user to edit, replace on save.
   - *Cancel* — discard the draft, leave `CONTEXT.md` narrative untouched.
   - User chose **apply** (simulated).
5. Refreshed `## Environment` via the deterministic helper **regardless of the narrative decision** — sentinel-bounded block was rewritten in place. NB: same `--section` divergence as scenario A; used `--output` + sentinel wrapper as a workaround.
6. `.planning/config.json` was **not** touched — md5 verified identical before and after the refresh (`ae9d487f09076557ecaecccea0cb2fa4`).

## Artefacts on disk
- `.planning/CONTEXT.md` — narrative refreshed, env block sentinel-bounded.
- `.planning/config.json` — byte-identical to pre-refresh.
- `.planning/CONTEXT.md.refresh-draft` — cleaned up after apply.

## WOULD_DISPATCH
- `researcher` — re-survey (honouring optional focus hint).
- `code-explorer` — skipped (small repo).
