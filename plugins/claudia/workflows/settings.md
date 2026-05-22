# Workflow — `/claudia-settings`

View or change `.planning/config.json` — mode, model profile, agent
toggles, parallelisation — without reinstalling.

Argument: `$ARGUMENTS` — optional `key=value` (e.g. `mode=yolo`,
`model_profile=quality`, `execution.parallel=true`). Empty means: show the
current config.

## Steps

1. **Show the config** when no argument is given:
   ```
   claudia config get
   ```
   If it returns "no config", tell the user to run `/claudia-understand`
   first (which writes `.planning/config.json` as part of the one-time
   codebase bootstrap).
2. **Apply a setting** when a `key=value` is given:
   ```
   claudia config set <key> <value>
   ```
   The CLI rejects unknown keys and invalid values; surface the error
   message verbatim.

## Settings

| Key | Values | Effect |
|---|---|---|
| `mode` | `pair`, `yolo` | `pair` (default): executor stops after each task so you review and commit. `yolo`: executor commits and proceeds autonomously. Also drives the verify fix-loop and close PR creation. |
| `model_profile` | `quality`, `balanced`, `budget` | model per agent role |
| `agents.researcher` / `.planner` / `.verifier` | `true`, `false` | toggle quality agents |
| `execution.parallel` | `true`, `false` | parallel executor waves |

## Review gate

Editing config is local and reversible — show the before/after diff and
confirm verbally, but no full accept/cancel gate is needed.

## Rules

- Reject keys or values not in the schema; do not invent settings.
- The review gate and the secret scan are not configurable — there is no
  key to disable them. Refuse any request to do so.
