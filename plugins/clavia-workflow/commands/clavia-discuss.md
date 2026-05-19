---
description: Pin down design decisions for the upcoming phase before planning — a Socratic Q&A that surfaces gray areas (API shapes, data structures, error handling) and records them in .planning/DECISIONS.md.
---

# Discuss the phase

A roadmap phase is one sentence — not enough to build it the way the user
imagines it. This command surfaces the design gray areas **before** planning,
so the plan reflects the user's intent. Output: appended entries in
`.planning/DECISIONS.md`.

Argument: `$ARGUMENTS` — optional phase number or topic. If empty, use the
current phase from `STATE.md`.

## Steps

1. **Read context** — `STATE.md` for the current phase, `ROADMAP.md` for its
   intent, `CONTEXT.md` for the stack, `DECISIONS.md` for choices already
   made.
2. **Find the gray areas.** Identify the underspecified decisions this phase
   needs: module layout, API/function shapes, data structures, error
   handling, edge cases, dependency choices.
3. **Ask, one cluster at a time.** Use `AskUserQuestion`. Present the decision
   and realistic options with trade-offs. Do not pick for the user. Use a
   `researcher` agent first if an option needs investigation.
4. **Record decisions** as you go, in the `DECISIONS.md` append-only format:
   question, decision, rationale in the user's words, alternatives rejected.

## Review gate

`DECISIONS.md` is **direction-locking**. Before writing, present the full set
of drafted entries and ask **accept / edit / cancel**. Apply edits per the
review-gate rule and re-present. Append on accept — never rewrite or delete
existing entries; supersede instead.

## Rules

- These are the user's decisions. Surface options and trade-offs; never
  decide for them.
- Stop when the phase is specified well enough to plan — do not over-discuss.
- Update `STATE.md`: next step = `/clavia-plan`.
