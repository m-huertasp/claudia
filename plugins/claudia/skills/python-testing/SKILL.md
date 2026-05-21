---
name: python-testing
description: Guides writing pytest tests for Python code using TDD. Activate whenever the user asks to write tests, generate a test suite, add coverage, test a function or class, or do TDD on new Python code. Also activate when they share Python code and say "add tests", "write tests for this", "how do I test this", or start implementing a new feature and haven't mentioned tests yet. Use this skill proactively — don't wait to be asked explicitly.
---

**Before writing any test code: check what testing tools the project uses.**

```bash
# Find the test runner and config
cat pyproject.toml 2>/dev/null | grep -A10 "\[tool.pytest"
cat pytest.ini 2>/dev/null
cat setup.cfg 2>/dev/null | grep -A5 "\[tool:pytest"
# Check if uv or poetry manages the env
ls pyproject.toml uv.lock poetry.lock 2>/dev/null
# Look at existing tests to learn patterns
find . -name "test_*.py" -o -name "*_test.py" | head -5
```

Also check for an existing `conftest.py` — it tells you about shared fixtures, database setup, auth helpers, and other conventions you should reuse rather than reinvent.

## The Core Loop: TDD

For any non-trivial functionality, follow the red-green-refactor cycle:

1. **RED** — Write the test first. Run it; watch it fail. A test that fails for the right reason means your test is correct.
2. **GREEN** — Write the minimal implementation to make it pass. Resist adding more than the test demands.
3. **REFACTOR** — Clean up with confidence, since the tests are green.

```bash
# Confirm the test fails first (RED)
pytest tests/test_user_service.py::test_create_user_rejects_duplicate_email -v
# Implement (GREEN), then
pytest tests/test_user_service.py -v
# Full suite to check for regressions
pytest --tb=short
```

The key discipline: **don't skip step 1**. Writing the test first clarifies what the code is supposed to do, surfaces API design issues early, and guarantees the test is actually testing something.

## Test Anatomy (AAA Pattern)

Every test should be readable as three blocks:

```python
def test_discount_applies_above_threshold():
    # Arrange
    cart = Cart(items=[Item(price=60)])

    # Act
    discounted = apply_discount(cart, threshold=50, rate=0.1)

    # Assert
    assert discounted.total == 54.0
```

Keep tests short. If setup is getting complex, extract a fixture. If the assertion is elaborate, you're testing too many things at once.

## What to Test

**Unit tests** — pure functions, business logic, model methods. Fast, isolated, no I/O.

**Integration tests** — database queries, API endpoints, file operations. Slower, use real dependencies or close fakes (e.g., SQLite `:memory:` instead of mocking every ORM call).

**When to mock** — mock when the dependency is: slow, nondeterministic, or has side effects you can't control (external HTTP APIs, email sending, time). Don't mock your own code or the database when an in-memory version is easy to set up — mocks that mirror your own API can hide real bugs.

## Fixtures

Use fixtures to eliminate setup duplication without losing clarity:

```python
# conftest.py — shared across the test suite
@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)

@pytest.fixture
def user(db):
    u = User(email="alice@example.com")
    db.add(u)
    db.commit()
    return u
```

**Fixture scope** — default is `function` (fresh per test). Use `scope="module"` or `scope="session"` only for expensive setup (real network connections, large datasets) where shared state is safe. When in doubt, use function scope — it prevents hidden test coupling.

**`autouse=True`** is useful for things that must always run (resetting global config, clearing caches), but use it sparingly so each test's dependencies stay obvious.

## Parametrization

Use `@pytest.mark.parametrize` instead of writing nearly-identical tests:

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("missing-at.com",   False),
    ("@nodomain",        False),
    ("",                 False),
], ids=["valid", "no-at", "no-user", "empty"])
def test_email_validation(email, valid):
    assert validate_email(email) is valid
```

Test IDs (the `ids` arg) make failure output readable: `FAILED test_email_validation[no-at]` vs `FAILED test_email_validation[1]`.

## Mocking

```python
from unittest.mock import patch, MagicMock

@patch("myapp.notifications.send_email")
def test_user_creation_sends_welcome_email(mock_send):
    create_user("alice@example.com")
    mock_send.assert_called_once_with("alice@example.com", subject="Welcome")
```

**Patch at the point of use**, not at the definition. If `myapp.users` imports `send_email` from `myapp.notifications`, patch `myapp.users.send_email`.

For side effects (simulate a network error, vary responses):

```python
mock_http.side_effect = [
    requests.Timeout("first call times out"),
    {"status": "ok"},  # second call succeeds
]
```

## Testing Exceptions

```python
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_input_message():
    with pytest.raises(ValueError, match="must be positive"):
        process(-1)
```

Don't `try/except` in tests — use `pytest.raises`. The `match` argument takes a regex and checks the exception message.

## Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_user():
    result = await fetch_user(id=1)
    assert result["name"] == "Alice"
```

Requires `pytest-asyncio`. If the whole module is async tests, add `pytestmark = pytest.mark.asyncio` at the top rather than decorating every function.

## Running Tests

```bash
# Adapt to the project's tool: `uv run pytest` or `poetry run pytest` or plain `pytest`
pytest -v                             # verbose
pytest -x                             # stop at first failure
pytest --tb=short                     # compact tracebacks
pytest tests/test_users.py::test_create_user  # specific test
pytest -k "email"                     # by name pattern
pytest --cov=myapp --cov-report=term-missing  # coverage
pytest -m "not slow"                  # skip marked tests
pytest --lf                           # rerun last failures
```

## Coverage

Aim for **80%+** overall; **100%** on critical paths (auth, payments, data validation).

```bash
pytest --cov=myapp --cov-report=term-missing --cov-report=html
```

Gaps that matter: untested error branches, edge cases, boundary values. Don't chase 100% everywhere — testing getters/setters has diminishing returns. Focus on behavior that could break silently.

## Test Organization

```
tests/
├── conftest.py          # shared fixtures
├── unit/
│   ├── test_models.py
│   └── test_services.py
├── integration/
│   ├── test_api.py
│   └── test_db.py
└── e2e/
    └── test_user_flow.py
```

Use `pytest.ini` or `pyproject.toml` to register custom markers so they don't generate warnings:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-markers"]
markers = [
    "slow: marks tests as slow (deselect with -m 'not slow')",
    "integration: requires a running database",
]
```

## Common Mistakes to Avoid

- **Testing implementation, not behavior**: If your test breaks when you rename a private method but the behavior is unchanged, it's too tightly coupled.
- **Shared mutable state between tests**: Always reset or isolate. A test that passes in isolation but fails in a full run is hiding a coupling bug.
- **Assertions that can't fail**: `assert result is not None` passes even when `result` is an empty list or wrong type. Be specific.
- **Giant test functions**: If a test is >20 lines, it's testing too many things. Split it.
- **Mocking so much that nothing real runs**: If your test mocks out 5 layers of your own code, you're not testing your code.
