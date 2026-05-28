---
name: python-patterns
description: Non-obvious Python patterns that Claude tends to skip or get wrong — typed decorators with ParamSpec, frozen/immutable dataclasses, exception chaining discipline, and EAFP vs LBYL decision rules. Use this skill when writing any Python code, especially decorators, value objects, error handling, or when asked to follow "best practices". Don't wait to be asked — activate proactively whenever the task involves Python.
---

# Python Patterns — Only What Claude Tends to Miss

This skill covers patterns where explicit guidance changes the output. It skips what Claude already does well (context managers, TypedDict, Counter, basic type hints).

## Typed Decorators with ParamSpec

The common mistake is writing `def wrapper(*args, **kwargs)` without proper type variables — callers lose type information. Always use `ParamSpec` so the wrapper preserves the decorated function's full signature.

```python
import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def retry(max_attempts: int = 3):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
            raise RuntimeError("unreachable")
        return wrapper
    return decorator
```

Why it matters: without `ParamSpec`, `wrapper(*args, **kwargs)` has type `(*Any, **Any) -> Any` — IDEs can't autocomplete arguments, mypy can't catch call-site errors.

## Frozen Dataclasses for Value Objects

The common mistake is using plain `@dataclass` for things that should be immutable. If an object represents a value (money, coordinates, a config snapshot), make it `frozen=True`. Add `slots=True` (Python 3.10+) for memory efficiency — it prevents accidental attribute addition and speeds up attribute access.

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)   # NOT just @dataclass
class Money:
    amount: float
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Amount must be non-negative, got {self.amount}")
        if not self.currency:
            raise ValueError("Currency must not be empty")

    def convert(self, rate: float, target: str) -> "Money":
        return Money(self.amount * rate, target)   # returns new object
```

Signs that frozen=True is right: the object is used as a dict key, represents a measurement/quantity, or you'd never expect it to change after creation.

## Exception Chaining — Always `raise X from e`

The common mistake is `raise CustomError(msg)` inside an `except` block — this loses the original traceback. Always use `raise CustomError(msg) from original_exc`.

```python
# Wrong — silently discards the original cause
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    raise ValueError("Failed to parse response")   # original traceback gone

# Right — chains the exceptions
try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ValueError("Failed to parse response") from exc   # full chain preserved
```

Python also provides `raise X from None` when you *intentionally* want to suppress the cause (e.g., presenting a clean public API without internal implementation details).

## EAFP vs LBYL — The Decision Rule

Both are valid Python. Choose based on the situation:

**Use EAFP (try/except)** when:
- The key/attribute/file is expected to exist most of the time (exception is the exception)
- There's a race condition between check and use (e.g., file existence)
- The check would require duplicating the access logic

```python
# EAFP — good when the key usually exists
def get_timeout(config: dict[str, int]) -> int:
    try:
        return config["timeout"]
    except KeyError:
        return 30
```

**Use LBYL (if check first)** when:
- The negative case is expected often (50%+ of calls)
- The exception would be expensive to construct (e.g., full stack trace for common path)
- The check is simpler than handling the exception

```python
# LBYL — good when None is a common expected value
def format_name(user: User | None) -> str:
    if user is None:
        return "Anonymous"
    return f"{user.first} {user.last}"
```

## Anti-Patterns Checklist

Before shipping Python code, verify:

```python
# Mutable default argument — ALWAYS a bug
def add(item, lst=[]):   # Bug: lst persists across calls
    lst.append(item)
    return lst

def add(item, lst=None):  # Correct
    if lst is None:
        lst = []
    lst.append(item)
    return lst

# isinstance(), not type() — type() fails for subclasses
if type(x) == list:   # Bad
if isinstance(x, list):  # Good

# is None, not == None — == can be overridden by __eq__
if x == None:   # Bad
if x is None:   # Good

# Bare except — catches KeyboardInterrupt, SystemExit, etc.
try:
    f()
except:   # Bad — swallows everything
    pass

try:
    f()
except SomeSpecificError as e:  # Good
    handle(e)

# String concatenation in loops — O(n²)
result = ""
for item in items:
    result += str(item)  # Bad

result = "".join(str(item) for item in items)  # Good
```

## Quick Reference

| Situation | Pattern |
|-----------|---------|
| Writing a decorator | Use `ParamSpec(P)` + `TypeVar(R)`, type as `Callable[P, R]` |
| Representing a value (money, point, config) | `@dataclass(frozen=True, slots=True)` |
| Wrapping an exception in a custom one | `raise MyError(msg) from original_exc` |
| Key usually present, missing is rare | EAFP (`try/except`) |
| Negative case is common or check is cheap | LBYL (`if` first) |
| Default mutable arg (list, dict, set) | Use `None` sentinel |