---
name: add-type-hints
description: Add Python type annotations to every function and method in a file, inferring each type as confidently as possible from defaults, the function body, docstrings, and call sites — and asking the user whenever a type cannot be determined with high confidence instead of guessing. Use this skill whenever the user asks to add, fill in, infer, or complete type hints / type annotations for a Python file, mentions "typing", "mypy", "annotate this", asks to make a file type-safe or pass a type checker, or opens an untyped Python file and asks to modernize or harden it. Trigger even if they don't say the words "type hints" — "add types to this module" or "make this typed" should activate it too.
---

# Add Type Hints

> Invoke as: `/add-type-hints <path-to-python-file>`

**Input**: $ARGUMENTS

The goal is a *correct* annotation on every function, not a *complete* one. A wrong type hint is worse than a missing one — it makes a type checker lie and misleads every future reader. So the governing rule of this skill is: **annotate what the evidence supports, and ask the user about the rest.** Never reach for `Any` or a plausible-looking guess just to fill the slot.

---

## Phase 1 — PARSE

Resolve the input path to absolute. If no argument is given, stop and ask the user for a file path. If the file does not exist or is not a `.py` file, stop with an error.

## Phase 2 — SCAN

Read the **entire** file — you cannot annotate a function without seeing how it is used. Identify every `def` and `async def`: module-level functions, methods, nested functions, properties.

For each one, record what is already there:

- Which parameters are already annotated — **leave those untouched**.
- Whether the return type is already annotated — leave it.
- `self` / `cls` — never annotate these.
- `*args` / `**kwargs` — annotate only if the element type is genuinely clear; these are often left bare.

Also note the file's existing conventions so your additions blend in:

- Is `from __future__ import annotations` present, or what Python version do `pyproject.toml` / existing syntax imply? This decides whether to write `list[int]` / `X | None` (modern) or `List[int]` / `Optional[X]` (pre-3.10). **Match the file** — do not mix styles.
- What is already imported from `typing` / `collections.abc`.
- If the project ships a `python-patterns` skill or typing rules, skim them — they may mandate, e.g., `collections.abc.Callable` over `typing.Callable`.

## Phase 3 — INFER (with a confidence level)

For every missing annotation, gather evidence and assign a confidence. Treat these sources as strong-to-weak:

**Parameters**

- **Default value** — `def f(retries=3)` → `int`; `flag=False` → `bool`; `name=""` → `str`. A literal default is strong evidence. A `None` default means the *real* type is `T | None` — infer `T` from the rest of the body, and if `T` itself is unclear, that is a question for the user.
- **Body usage** — `path.endswith(...)` → `str`; `items.append(...)` / `len(items)` + indexing → a list; `x / 2`, `x * rate` → numeric; `for k, v in d.items()` → a mapping; calls like `user.email` point to a known class in the file.
- **Docstring** — a NumPy/Google docstring with a typed `Parameters` section is strong evidence; reconcile it with body usage rather than trusting it blindly (docstrings drift).
- **Call sites** — search the whole file (and obvious sibling modules) for calls to the function; the literal arguments passed in often pin the type down.

**Return type**

- Every `return` statement with a value — unify them. All return the same concrete type → use it. Mixed → a union, or ask if the union looks accidental.
- No `return`, or only bare `return` / only `return None` → `-> None`. This is almost always high-confidence; apply it.
- `yield` in the body → a generator: `Iterator[T]` (or `Generator[Y, S, R]` if it uses `.send`). Infer `T` from the yielded expression.
- An `async def` whose body returns `T` → the annotation is still `-> T` (the `async` keyword does the rest); an async generator yields → `AsyncIterator[T]`.

**Confidence tiers**

- **HIGH** — the evidence is direct and unambiguous (literal default, a method call that only one type supports, a single concrete return). Apply it.
- **MEDIUM** — strongly implied but with a plausible alternative (e.g. body uses only `len()` and iteration, so `Sequence[X]` vs `list[X]`; or an int-vs-float numeric). Prefer the more general correct type (`Sequence`, `float`) and apply it, but list it in the report so the user can see the call was made.
- **LOW** — genuinely underdetermined: a parameter only passed through to another untyped function, a `**kwargs` forwarded opaquely, a container whose element type never shows, a return that depends on an untyped external call. **Do not annotate these from a guess.** Collect them for Phase 4.

Never use `Any` as a substitute for asking. `Any` is a deliberate choice ("this is intentionally dynamic"), not a fallback for "I didn't work it out."

## Phase 4 — RESOLVE UNCERTAINTY

If Phase 3 produced any LOW-confidence items, **stop before writing** and ask the user about all of them at once — one batched question, not a trickle. For each uncertain slot give: the function and parameter/return, the candidates you considered, and the evidence for each, so the user can answer quickly.

Use the `AskUserQuestion` tool. Offer the realistic candidates as options (the user can always supply their own). Example framing:

> `parse_config(source)` — `source` is opened with `open(source)` in one branch and used as a `dict` in another. Is it a file path (`str | Path`), an already-loaded `dict`, or a union of both?

Only after the user answers do you proceed to write. If the user says "leave it" for an item, leave that slot unannotated rather than forcing a type — a deliberate blank is honest; a wrong hint is not.

## Phase 5 — WRITE

Edit the source file in-place.

- Add only the missing annotations; never alter ones that were already there.
- Add `-> None` to every function that does not return a value — these are easy to miss and a checker flags their absence.
- Add any imports your annotations now require (`from collections.abc import Iterator`, `from typing import Any`, etc.) in the file's existing import block, matching its grouping.
- If you used a forward reference to a class defined later in the file, quote it (`"MyClass"`) or rely on `from __future__ import annotations` if present.
- Keep the diff minimal and the style consistent with Phase 2's findings.

## Phase 6 — VERIFY

If a type checker is available in the project (`mypy`, `pyright` — check `pyproject.toml` / config files), run it on the file and confirm your additions did not introduce new errors. If a checker is not available, do a careful re-read instead. Report any pre-existing errors you noticed but do not fix unrelated code.

## Phase 7 — REPORT

Print a summary table covering every function examined:

| Function | Parameters annotated | Return | Confidence | Notes |
|---|---|---|---|---|
| `load_data` | `path: str` | `-> pd.DataFrame` | HIGH | |
| `merge` | `left, right: Sequence[Row]` | `-> list[Row]` | MEDIUM | `Sequence` chosen over `list` — inputs only iterated |
| `run_hook` | — | `-> None` | — | `cb` left unannotated per user (Phase 4) |

End with: how many annotations were added, how many slots were already typed, how many were left blank by user choice, and the type-checker result from Phase 6.

---

## Edge Cases

- **No argument given** — stop and ask for a file path.
- **Non-`.py` file** — stop with an error.
- **File already fully annotated** — report it; do not rewrite anything.
- **`@overload` stubs** — annotate each overload from its own signature; do not collapse them.
- **`@typing.no_type_check` / explicit `# type: ignore`** — respect the author's intent; skip and note it.
- **Decorated functions** — a decorator can change the effective signature (e.g. it returns a different callable). If the decorator is unfamiliar, treat the return type as LOW-confidence and ask.
- **Properties** — annotate the getter's return type; a setter's value parameter takes the getter's type.
- **Generated, vendored, or test-fixture files** — confirm with the user before editing if the file looks machine-generated.
- **When in doubt, ask — do not suppose.** A blank slot is recoverable; a confidently wrong annotation quietly corrupts every type check that follows.
