---
description: Add or fix type annotations in a Python file to resolve ANN001/ANN002/ANN003 and missing return-type violations.
---

# Type Annotate

> Invoke as: `/type-annotate <path-to-python-file>`

**Input**: $ARGUMENTS

---

## Annotation Mode

Read the given Python file in full, then add or correct every missing or incorrect type annotation to conform to PEP 484 and resolve common flake8-annotations violations (ANN001, ANN002, ANN003, ANN201, ANN202, ANN204).

### Phase 1 — PARSE

Resolve the input path to absolute. If no argument is given, stop and ask the user for a file path. If the file does not exist or is not a `.py` file, stop with an error.

### Phase 2 — SCAN

Read the entire file. Identify every function, method, and class definition.

For each symbol determine:
- Which parameters lack a type annotation?
- Is the return type annotated?
- What types can be inferred from defaults, usage, docstrings, or context?
- Is it a `property`, `classmethod`, or `staticmethod`?

**Symbol inclusion rules:**

| Symbol | Include? |
|---|---|
| Public functions and methods (`foo`) | Yes |
| `__init__` | Yes — annotate parameters; return type is always `None` |
| Special methods (`__str__`, `__repr__`, etc.) | Yes — well-known return types apply |
| Private functions and methods (`_foo`, `__foo`) | Yes — annotations improve internal safety |
| Lambda expressions | No — not annotatable in-place |
| Module-level constants | No |

**ANN violation reference:**

| Code | Meaning |
|---|---|
| ANN001 | Missing annotation for a regular argument |
| ANN002 | Missing annotation for `*args` |
| ANN003 | Missing annotation for `**kwargs` |
| ANN201 | Missing return type for a public function |
| ANN202 | Missing return type for a private function |
| ANN204 | Missing return type for a special method |

### Phase 3 — WRITE

Add or correct annotations following the rules below. Edit the source file in-place.

#### Annotation rules

- Infer types from **default values** first (e.g. `x=0` → `int`, `flag=False` → `bool`, `name=None` → add `Optional[…]` or use `| None`).
- Infer types from **docstrings** (NumPy/SciPy or Google style) when a default is absent.
- Use **`Any`** only when the type genuinely cannot be determined — never as a shortcut.
- Prefer **`X | None`** (Python 3.10+) over `Optional[X]` unless the rest of the file uses `Optional`.
- Use **`collections.abc`** types (`Sequence`, `Mapping`, `Callable`, `Iterator`, …) for abstract containers; use `list[T]`, `dict[K, V]`, `tuple[T, ...]` for concrete ones.
- For `*args` use `*args: T` (type of each element, not the tuple). For `**kwargs` use `**kwargs: V` (type of each value).
- Add necessary imports (`from __future__ import annotations`, `from typing import …`, `from collections.abc import …`) at the top of the file if they are not already present.
- Do **not** change any logic, docstrings, or formatting outside the annotation itself.
- **ASK IF DOUBTS** — if a type is ambiguous and cannot be safely inferred, ask the user before guessing.

#### `self` and `cls`

Never annotate `self` or `cls`.

#### Return types

- Functions that end without a `return` statement, or only `return None`, get `-> None`.
- Generators get `-> Generator[YieldType, SendType, ReturnType]` or `-> Iterator[YieldType]` as appropriate.
- `__init__` always gets `-> None`.
- `__str__` / `__repr__` always get `-> str`.
- `__len__` always gets `-> int`.
- `__bool__` always gets `-> bool`.

#### Gold-standard before/after examples

**ANN001 — missing argument annotation:**

```python
# Before
def log_metadata(metadata: Dict[str, Any], DB_NAME=__file__) -> None:
    ...

# After
def log_metadata(metadata: Dict[str, Any], DB_NAME: str = __file__) -> None:
    ...
```

**ANN001 + ANN201 — missing argument and return annotations:**

```python
# Before
def fetch_records(db, limit=100):
    ...

# After
def fetch_records(db: Connection, limit: int = 100) -> list[Record]:
    ...
```

**ANN002 / ANN003 — *args / **kwargs:**

```python
# Before
def merge(*tables, **options):
    ...

# After
def merge(*tables: str, **options: Any) -> None:
    ...
```

### Phase 4 — REPORT

After editing the file, print a summary table:

| Symbol | Parameter / Return | Action |
|---|---|---|
| `function_name` | `param_name` | Added `int` / Already annotated / Inferred from default / Asked user / Skipped |
| `function_name` | return | Added `-> None` / Already annotated / Skipped |

List every annotation point examined. Flag any symbol where the type had to be assumed with a **[⚠ assumed]** note so the user can verify.

---

## Edge Cases

- **No argument given** — stop and ask for a file path.
- **Non-`.py` file** — stop with an error.
- **File is already fully annotated** — report "Already annotated" for every symbol; do not rewrite unnecessarily.
- **`from __future__ import annotations` present** — all annotations are treated as strings; this is fine; still add missing ones in string form.
- **Overloaded functions (`@overload`)** — annotate each overload signature individually; the implementation signature may use wider types.
- **Third-party types not imported** — add the import; if the package is unavailable at analysis time, use a string literal (`"ClassName"`) or `TYPE_CHECKING` guard.
- **ASK IF DOUBTS, do not suppose.**
