---
description: Comprehensive Python code review for a single file or a repo/folder. Generates a local review artifact.
agent: code-reviewer
---

# Python Code Review

> Designed to run with the `@code-reviewer` agent. Invoke as: `@code-reviewer /python-review <path>`

**Input**: $ARGUMENTS

---

## Python Review Mode

Comprehensive Python-specific code review — reads full files, runs static analysis, generates a local review artifact.

### Phase 1 — PARSE

Parse the input to determine the review target:

| Input | Action |
|---|---|
| `.py` file path (e.g. `app/routes/user.py`) | Review that single file |
| Folder / repo path (e.g. `src/` or `.`) | Recursively find all `.py` files under it |
| No input | Default to current working directory |

Resolve the path to absolute. If the target does not exist, stop with an error.

Derive the **artifact name** from the target:
- Single file → basename without extension (e.g. `user.py` → `user`)
- Folder → folder name (e.g. `src/` → `src`, `.` → repo root name)

Artifact will be written to `.github/py-<NAME>-review.md`.

### Phase 2 — CONTEXT

Build review context:

1. **Project rules** — Read `copilot-instructions.md` and any contributing guidelines found in the repo
2. **Python version** — Check `pyproject.toml`, `setup.py`, or `.python-version` for the target Python version
3. **Framework detection** — Detect Django / FastAPI / Flask from dependencies and apply framework-specific checks (see Framework-Specific Checks section in Phase 3)
4. **File list** — Enumerate all `.py` files in scope; for a single file, the list has one entry

### Phase 3 — REVIEW

Read each file **in full**. Apply the review checklist across 7 categories:

| Category | What to Check |
|---|---|
| **Correctness** | Logic errors, off-by-ones, null handling, edge cases, race conditions |
| **Type Safety** | Missing type hints on public functions, type mismatches, `Any` overuse |
| **Pattern Compliance** | PEP 8, naming conventions, import order, project-specific conventions |
| **Security** | SQL/command injection, `eval`/`exec`, unsafe pickle/YAML, hardcoded secrets, path traversal |
| **Performance** | N+1 queries, unbounded loops, inefficient string concatenation, large in-memory payloads |
| **Completeness** | Missing docstrings on public symbols, missing error handling, print instead of logging |
| **Maintainability** | Mutable defaults, magic numbers, deep nesting, dead code, non-Pythonic idioms |

Assign a severity to each finding:

| Severity | Meaning |
|---|---|
| **CRITICAL** | Security vulnerability or data-loss risk — must fix |
| **HIGH** | Bug or logic error likely to cause issues — should fix |
| **MEDIUM** | Code quality issue or missing best practice — fix recommended |
| **LOW** | Style nit or minor suggestion — optional |

#### Confidence-Based Filtering

Only report issues you are **>80% confident** are real problems:
- **Report** genuine bugs, security issues, and code quality problems
- **Skip** stylistic preferences unless they violate project or PEP 8 conventions
- **Consolidate** similar issues (e.g., "5 functions missing type hints" not 5 separate findings)
- **Prioritize** issues that could cause bugs, security vulnerabilities, or data loss

#### CRITICAL — Must Fix

- SQL/command injection (`f`-strings or `%` formatting in queries)
- Unsafe `eval()`/`exec()` with user input
- Unsafe `pickle` deserialization
- Hardcoded credentials, API keys, or tokens
- `yaml.load()` without `Loader=yaml.SafeLoader`
- Bare `except:` clauses that swallow all errors

```python
# BAD: SQL injection via f-string
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD: parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

```python
# BAD: unsafe YAML load
data = yaml.load(stream)

# GOOD:
data = yaml.safe_load(stream)
```

```python
# BAD: bare except swallows everything
try:
    process()
except:
    pass

# GOOD: catch specific exceptions, log and re-raise
try:
    process()
except ValueError as e:
    logger.error("Invalid input: %s", e)
    raise
```

#### HIGH — Should Fix

- Missing type hints on public functions and methods
- Mutable default arguments (`def f(items=[]):`)
- Silently swallowed exceptions (`except Exception: pass`)
- Not using context managers for file/network/DB resources
- Using `type(x) == Y` instead of `isinstance(x, Y)`
- C-style loops where a comprehension or built-in would be clearer
- Race conditions in shared state without locks

```python
# BAD: mutable default, no type hints, no context manager
def load_data(path, cache=[]):
    f = open(path)
    data = f.read()
    f.close()
    return data

# GOOD:
def load_data(path: str, cache: list | None = None) -> str:
    if cache is None:
        cache = []
    with open(path) as f:
        return f.read()
```

```python
# BAD: type equality check, C-style loop
result = []
for i in range(len(items)):
    if type(items[i]) == str:
        result.append(items[i].upper())

# GOOD:
result = [item.upper() for item in items if isinstance(item, str)]
```

#### MEDIUM — Fix Recommended

- PEP 8 violations (naming, line length, spacing)
- Missing docstrings on public functions, classes, and modules
- `print()` statements instead of `logging`
- Magic numbers without named constants
- Not using f-strings for string formatting (Python 3.6+)
- Unnecessary intermediate list creation (use generators)
- Inefficient string concatenation in loops

#### LOW — Optional

- Minor naming improvements
- TODO/FIXME comments without issue references
- Redundant comments that restate the code

#### Framework-Specific Checks

**Django** — N+1 queries (use `select_related`/`prefetch_related`), missing migrations, raw SQL when ORM suffices, missing `transaction.atomic()`.

**FastAPI** — CORS misconfiguration, missing Pydantic request/response models, improper `async`/`await`, dependency injection patterns.

**Flask** — App/request context leaks, blueprint organisation, missing error handlers, configuration management.

### Phase 4 — VALIDATE

Run available static-analysis tools against the target path. Detect which tools are installed before running:

```bash
# Type checking
mypy <TARGET>

# Linting & formatting
ruff check <TARGET>
black --check <TARGET>
isort --check-only <TARGET>

# Security
bandit -r <TARGET>

# Tests (only if target is a folder/repo and pytest is available)
pytest --cov=<TARGET> --cov-report=term-missing
```

Skip tools that are not installed. Record **Pass / Fail / Skipped** for each.

### Phase 5 — DECIDE

Form a recommendation:

| Condition | Decision |
|---|---|
| Zero CRITICAL/HIGH issues, validation passes | **PASS** — approve |
| Only MEDIUM/LOW issues, validation passes | **WARNING** — merge with caution |
| Any HIGH issues or validation failures | **FAIL** — fix before merge |
| Any CRITICAL issues | **BLOCK** — must fix before merge |

### Phase 6 — REPORT

Create a **local** review artifact at `.github/py-<NAME>-review.md`. Do not post or publish anything.

```markdown
# Python Review: <TARGET>

**Reviewed**: <date>
**Decision**: PASS | WARNING | FAIL | BLOCK

## Summary
<1–2 sentence overall assessment>

## Findings

### CRITICAL
<findings or "None">

### HIGH
<findings or "None">

### MEDIUM
<findings or "None">

### LOW
<findings or "None">

## Validation Results

| Check | Result |
|---|---|
| mypy | Pass / Fail / Skipped |
| ruff | Pass / Fail / Skipped |
| black | Pass / Fail / Skipped |
| isort | Pass / Fail / Skipped |
| bandit | Pass / Fail / Skipped |
| pytest | Pass / Fail / Skipped |

## Files Reviewed
<list of .py files reviewed>
```

Report to the user where the artifact was written.

### Phase 7 — OUTPUT

Report to the user:

```
Python Review: <TARGET>
Decision: <PASS|WARNING|FAIL|BLOCK>

Issues: <critical_count> critical, <high_count> high, <medium_count> medium, <low_count> low
Validation: <pass_count>/<total_count> checks passed

Artifact: .github/py-<NAME>-review.md

Next steps:
  - <contextual suggestions based on decision>
```

---

## Common Fixes

### Add Type Hints

```python
# Before
def calculate(x, y):
    return x + y

# After
from typing import Union

def calculate(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
    return x + y
```

### Use Context Managers

```python
# Before
f = open("file.txt")
data = f.read()
f.close()

# After
with open("file.txt") as f:
    data = f.read()
```

### Use List Comprehensions

```python
# Before
result = []
for item in items:
    if item.active:
        result.append(item.name)

# After
result = [item.name for item in items if item.active]
```

### Fix Mutable Defaults

```python
# Before
def append(value, items=[]):
    items.append(value)
    return items

# After
def append(value, items=None):
    if items is None:
        items = []
    items.append(value)
    return items
```

### Use f-strings (Python 3.6+)

```python
# Before
greeting = "Hello, " + name + "!"
greeting2 = "Hello, {}".format(name)

# After
greeting = f"Hello, {name}!"
```

### Fix String Concatenation in Loops

```python
# Before
result = ""
for item in items:
    result += str(item)

# After
result = "".join(str(item) for item in items)
```

## Python Version Compatibility

Note when code uses features requiring a minimum Python version:

| Feature | Minimum Python |
|---------|----------------|
| Type hints | 3.5+ |
| f-strings | 3.6+ |
| Walrus operator (`:=`) | 3.8+ |
| Position-only parameters | 3.8+ |
| Match statements | 3.10+ |
| Type unions (`x \| None`) | 3.10+ |

Verify the project's `pyproject.toml` or `setup.py` declares the correct minimum version.

---

## Edge Cases

- **No `.py` files found** in the target folder → stop with a clear error.
- **Large codebases (>50 files)** → warn about scope; review source files first, then tests, then config.
- **Missing tools** → skip gracefully; note which tools were not available in the report.
- **ASK IF DOUBTS, do not suppose.**