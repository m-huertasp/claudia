---
description: Generate comprehensive pytest unit and integration tests for a Python module. Inspects functions, asks for intended behavior, and writes tests with fixtures and mocks.
agent: code-reviewer
---

# Pytest Test Generation

> Designed to run with the `@code-reviewer` agent. Invoke as: `@code-reviewer /pytest-gen <path>`

**Input**: $ARGUMENTS

---

## Pytest Generation Mode

Interactive, multi-phase test generation — reads the full module, discovers testable symbols, interrogates you about intended behavior, classifies tests, writes pytest code, and validates it runs.

### Phase 1 — PARSE

Parse the input to determine the target:

| Input | Action |
|---|---|
| `.py` file path (e.g. `src/utils/parser.py`) | Generate tests for that single module |
| Folder path (e.g. `src/utils/`) | Recursively find all `.py` files under it, skipping `__init__.py`, `conftest.py`, and any existing `test_*.py` |
| No input | Default to current working directory |

Resolve the path to absolute. If the target does not exist, stop with an error.

Derive the **output test file name** from the target:
- Single file → `test_<basename>` (e.g. `parser.py` → `test_parser.py`)
- Folder → one `test_<module>.py` per discovered file

Place output test files next to the source files, or inside a `tests/` folder if one already exists at the repo root. Respect the existing layout.

### Phase 2 — CONTEXT

Build test context before reading source:

1. **Project rules** — Read `copilot-instructions.md` and any contributing guidelines in the repo
2. **pytest configuration** — Check `pyproject.toml` (`[tool.pytest.ini_options]`), `pytest.ini`, or `setup.cfg` for markers, test paths, and plugins (e.g. `pytest-asyncio`, `pytest-django`, `anyio`)
3. **Existing fixtures** — Locate and read all `conftest.py` files from the repo root down to the target's directory; list available fixtures
4. **Existing tests** — Find any `test_*.py` or `*_test.py` files for the same module; note what is already covered to avoid duplication
5. **Dependencies** — Read `pyproject.toml` or `requirements*.txt` to identify third-party dependencies that will need mocking
6. **Python version** — Check `.python-version`, `pyproject.toml`, or `setup.py` for the target Python version; use appropriate syntax

### Phase 3 — INSPECT

Read the target module **in full**. For each local import, read one level deep to understand the contract.

Build an inventory of all testable symbols:

| Symbol type | Collect |
|---|---|
| Module-level functions | Name, signature (with type hints), docstring, return type |
| Classes | Name, `__init__` signature, all public methods |
| Async functions/methods | Flag as `async`; note `asyncio` / `anyio` requirement |
| Properties | Flag as read-only or read-write |
| Module-level constants | Skip — not directly testable |
| Private symbols (`_foo`) | Skip unless called by a public function under review |

For each symbol, identify:
- **External dependencies**: I/O, network calls, DB queries, subprocess, datetime, random — these need mocking
- **Side effects**: writes to files, modifies global state, raises exceptions
- **Complexity**: number of branches, loops, or conditional paths — drives parametrize needs

### Phase 4 — INTERROGATE

**STOP and ask the user before generating any tests.**

Present a structured question block for each function/method where the intended behavior is not fully clear from the signature, docstring, or implementation. Do not ask about trivial getters or functions whose behavior is entirely deterministic from reading the code.

Format questions as:

```
## Questions before test generation

For each item below, please describe the expected behavior, edge cases, or confirm the suggested answer.

### `function_name(arg1, arg2)`
- What should it return when `arg1` is empty / None / zero?
- Should it raise an exception for invalid inputs, or return a sentinel value?
- Are there any important boundary values we should test?
- [Suggested behavior based on code reading]: <your inference — user can confirm or correct>

### `ClassName.method_name()`
- ...
```

Wait for the user's responses. Incorporate them into test generation. If the user says "skip" or "not sure" for a function, generate basic happy-path tests only.

### Phase 5 — CLASSIFY

For each symbol, decide the test type using this decision table:

| Condition | Test type |
|---|---|
| Pure function, no external deps | **Unit** — no mocking needed |
| Uses stdlib only (e.g. `os.path`, `re`) | **Unit** — mock only if I/O-bound |
| Calls third-party library with network/DB/I/O | **Unit** — mock the external call |
| Integrates multiple internal modules | **Integration** — use real objects, mock only external boundaries |
| Interacts with a real DB or filesystem | **Integration** — use `tmp_path` or a test DB fixture |
| Async function | **Unit or Integration** — use `pytest-asyncio` with `@pytest.mark.asyncio` |

Record the classification for each symbol. Report the full list to the user before proceeding:

```
Classification summary:
  Unit tests:        function_a, function_b, MyClass.method_x
  Integration tests: MyClass.method_y (uses DB), function_c (calls external API)
  Skipped:           _internal_helper (private)
```

### Phase 6 — GENERATE

Write tests following these conventions:

#### File structure

```python
"""Tests for <module_path>."""

import pytest
from unittest.mock import MagicMock, patch, call
# third-party mocks as needed

from <module_path> import <SymbolUnderTest>


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def <fixture_name>():
    ...


# ── <ClassName or "Functions"> ───────────────────────────────────────────────

class Test<SymbolName>:
    def test_<scenario>(self, ...):
        ...
```

#### Test naming

Use the pattern `test_<what>_<when>_<expected>`:
- `test_parse_empty_string_returns_empty_list`
- `test_connect_timeout_raises_connection_error`
- `test_calculate_total_with_discount_returns_reduced_amount`

#### Required coverage per symbol

For each function/method, generate at minimum:
- **Happy path** — typical valid inputs producing expected output
- **Edge cases** — empty collections, zero values, boundary values, `None` inputs (informed by Phase 4 answers)
- **Error paths** — invalid types, out-of-range values, expected exceptions (use `pytest.raises`)
- **Parametrized cases** — use `@pytest.mark.parametrize` when 3+ input variants test the same logic

#### Mocking rules

- Mock at the **point of use**, not at the definition: `patch("mymodule.requests.get")` not `patch("requests.get")`
- Prefer `pytest-mock`'s `mocker` fixture over bare `unittest.mock.patch` if `pytest-mock` is in the project's dependencies
- Never mock the symbol under test itself
- Assert mock calls when the call itself is the behavior being tested (e.g., verifying an API was called with correct args)

#### Async tests

```python
@pytest.mark.asyncio
async def test_fetch_data_returns_parsed_response(mocker):
    mocker.patch("mymodule.aiohttp.ClientSession.get", ...)
    result = await fetch_data("https://example.com")
    assert result == expected
```

#### Example patterns

```python
# Parametrize for multiple input variants
@pytest.mark.parametrize("value,expected", [
    (0, 0),
    (1, 1),
    (-1, 1),
    (100, 100),
])
def test_absolute_value(value, expected):
    assert absolute_value(value) == expected


# Exception assertion
def test_parse_invalid_json_raises_value_error():
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse("{not: valid}")


# Mock with call assertion
def test_send_notification_calls_smtp_once(mocker):
    mock_smtp = mocker.patch("mymodule.smtplib.SMTP")
    send_notification("user@example.com", "Hello")
    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()


# tmp_path for filesystem tests
def test_write_report_creates_file(tmp_path):
    output = tmp_path / "report.csv"
    write_report(str(output), data=[1, 2, 3])
    assert output.exists()
    assert output.read_text().startswith("1")
```

### Phase 7 — VALIDATE

Run available tools to validate the generated tests. Check which are installed before running:

```bash
# Verify tests are collected without errors
pytest --collect-only <test_file_path>

# Run the generated tests
pytest <test_file_path> -v

# Check coverage if pytest-cov is available
pytest <test_file_path> -v --cov=<source_module> --cov-report=term-missing
```

Record **Pass / Fail / Skipped** for each check. If tests fail:
1. Read the error output carefully
2. Fix the test (not the source) if the failure is a test authoring error
3. Flag failures caused by bugs in the source module — report them, do not silently alter the test to pass

### Phase 8 — REPORT

Report to the user:

```
Pytest Generation: <TARGET>

Tests written: <N> test functions across <M> test files
  Unit:         <count>
  Integration:  <count>

Validation:
  Collection:   Pass / Fail
  Execution:    <pass_count>/<total_count> tests passed
  Coverage:     <percentage>% of <source_module> (if available)

Output files:
  <list of test files created>

Gaps / open items:
  - <any functions skipped, and why>
  - <any source bugs discovered during test authoring>
  - <any fixtures the user should add to conftest.py>
```

---

## Edge Cases

- **No public symbols found** — stop with a clear message; ask if the user wants to test private functions explicitly.
- **Module has no imports** — pure module; generate unit tests with no mocking setup.
- **Existing test file already covers >80% of functions** — report what is covered, ask whether to extend or overwrite.
- **Async code without `pytest-asyncio` installed** — note the missing dependency and include an install instruction in the report.
- **Functions with no docstring and ambiguous behavior** — always ask in Phase 4; never guess silently.
- **ASK IF DOUBTS, do not suppose.**
