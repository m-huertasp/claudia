---
description: View or change the clavia workflow configuration in .planning/config.json — mode, model profile, agent toggles, parallelization — without reinstalling.
---

# Workflow settings

The user wants to view or change `.planning/config.json`.

Argument: `$ARGUMENTS` — optional. A `key=value` (e.g. `mode=yolo`,
`model_profile=quality`, `execution.parallel=true`) sets a value; empty shows
the current config.

## Steps

1. **Read `.planning/config.json`.** If it does not exist, tell the user to
   run `/clavia-new` first.
2. **If no argument**, show the current settings with a one-line explanation
   of each, and the valid values.
3. **If a `key=value`** was given, validate it against the schema below, then
   apply it.

## Settings

| Key | Values | Effect |
|---|---|---|
| `mode` | `interactive`, `yolo` | confirm each phase, or auto-proceed |
| `model_profile` | `quality`, `balanced`, `budget` | model per agent role |
| `agents.researcher` / `.planner` / `.verifier` | `true`, `false` | toggle quality agents |
| `execution.parallel` | `true`, `false` | parallel executor waves |

## Review gate

Editing config is local and reversible — show the before/after diff and
confirm, but no full accept/cancel gate is needed.

## Rules

- Reject keys or values not in the schema; do not invent settings.
- The review gate and the secret scan are not configurable — there is no key
  to disable them. Refuse any request to do so.
