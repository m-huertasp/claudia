---
description: Single entry point for the claudia framework. Routes `/claudia <verb> [args]` to the matching skill (explicit-verb mode) or, when the first token is not a known verb, falls through to natural-language routing. Verbs include understand, plan, execute, close, rules, pr-review, write-issue, add-type-hints, prepare-docstrings.
---

# claudia

Invoke the `claudia:claudia` skill (the dispatcher) with `$ARGUMENTS`.

The dispatcher handles both explicit-verb routing
(`/claudia <verb> [args]`) and natural-language routing
(`/claudia <free-form text>`). See
[skills/claudia/SKILL.md](../skills/claudia/SKILL.md) for the
authoritative routing table and behaviour.

**Argument:** `$ARGUMENTS` — empty, an explicit verb followed by its
arguments, or free-form natural language.
