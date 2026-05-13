---
name: prepare-docstrings
description: Create and/or homogenize all docstrings in a Python file using NumPy/SciPy format. Use this skill whenever the user asks to add, write, update, fix, improve, or homogenize docstrings in a Python file, mentions "NumPy format" or "SciPy format", or asks to document Python functions, methods, or classes — even if they don't explicitly say "docstrings". Also trigger when the user opens a Python file and asks to document it, make it more readable, or prepare it for a public API.
---

# Prepare Docstrings

> Invoke as: `/prepare-docstrings <path-to-python-file>`

**Input**: $ARGUMENTS

---

## Docstring Mode

Read the given Python file in full, then add or rewrite every public function, method, and class docstring to conform to the NumPy/SciPy standard. Also add a module-level docstring if missing.

### Phase 1 — PARSE

Resolve the input path to absolute. If no argument is given, stop and ask the user for a file path. If the file does not exist or is not a `.py` file, stop with an error.

### Phase 2 — SCAN

Read the entire file. Identify:

- The module itself (for a module-level docstring)
- Every function, method, and class definition

For each symbol determine:
- Does it already have a docstring?
- Is the existing docstring already in NumPy/SciPy format?
- What parameters does it accept? Collect names and annotated types, excluding `self` and `cls`.
- What does it return (annotated type, if present)? Does the body contain `yield` statements?
- Does the body contain any explicit `raise` statements, or calls to library methods that raise by contract (e.g. `raise_for_status()`, `check_call()`, `check_output()`)?
- Is it a `property`, `classmethod`, or `staticmethod`?
- Is it an `async def`?
- What class attributes are defined (for class-level docstrings)?

**Symbol inclusion rules:**

| Symbol | Include? |
|---|---|
| Module level | Yes — add a module docstring if missing |
| Public functions and methods (`foo`) | Yes |
| Public classes | Yes (document in the class-level docstring) |
| `__init__` | No — document its parameters in the class docstring instead |
| Special methods (`__str__`, `__repr__`, etc.) | Only if non-trivial |
| Private symbols (`_foo`, `__foo`) | No — skip entirely |
| Module-level constants | No |

### Phase 3 — WRITE

Add or rewrite docstrings following the rules below. Edit the source file in-place.

#### Docstring rules

**Style**: NumPy/SciPy format — section headings underlined with dashes.

**Structure** (in order):

1. **Summary** — A single concise sentence on the first line.
2. **Description** *(optional)* — A short paragraph explaining the *how* or *why*, separated from the summary by a blank line. Add only if necessary.
3. **Parameters** — List every argument (excluding `self` and `cls`) with its type and a one-line description. **Omit this section entirely if there are no parameters.**
4. **Returns** — Return type and description. **Omit if the function returns `None`, has no return statement, or is a generator (use `Yields` instead).**
5. **Yields** — For generator functions (those with `yield` in the body). Use this section instead of `Returns`.
6. **Raises** — Include when the function body contains explicit `raise` statements **or** calls library methods that are documented to raise as part of their contract (e.g. `response.raise_for_status()`, `subprocess.check_call()`, `socket.connect()`). For library calls, document the exception the library raises, not a generic `Exception`. **Omit if no exceptions are raised either explicitly or via such calls.**
7. **Attributes** — For class docstrings, list public instance and class attributes with their types. **Omit if the class has no public attributes worth documenting.**

#### Type annotation mapping

Translate Python type annotations into their NumPy docstring equivalents:

| Python annotation | Docstring type |
|---|---|
| `Optional[X]` or `X \| None` | `X, optional` |
| `list[X]` or `List[X]` | `list of X` |
| `dict[K, V]` or `Dict[K, V]` | `dict` |
| `tuple[X, Y]` or `Tuple[X, Y]` | `tuple` |
| No annotation (cannot infer) | `any` |

For default-valued parameters, append `, optional` to the type and add `Default is <value>.` at the end of the description.

#### Async functions

Document `async def` functions exactly like regular functions. Do not add any "async" qualifier to the docstring — the `async` keyword on the function definition is sufficient.

#### Parameter formatting

```
name : type
    Description of the parameter.
```

For `*args` use `*args : type` and for `**kwargs` use `**kwargs : type`. If no type annotation exists and the type cannot be inferred from context, use `any`.

#### Module-level docstrings

Place at the top of the file, before any imports. Keep to 1–3 sentences: what the module does and its main public interface.

```python
"""Utilities for downloading and validating HGNC reference data.

Provides functions to fetch, checksum-verify, and parse the HGNC dataset
into pandas DataFrames ready for downstream analysis.
"""
```

#### Class docstrings

Document the class purpose, its `__init__` parameters, and any notable public attributes in the class-level docstring. Do not add a separate docstring to `__init__`.

```python
class MyProcessor:
    """Process input data and emit transformed records.

    Parameters
    ----------
    config : Config
        Configuration object controlling processing behavior.
    verbose : bool, optional
        If True, emit progress logs. Default is False.

    Attributes
    ----------
    records_processed : int
        Running count of records emitted since instantiation.
    """

    def __init__(self, config: Config, verbose: bool = False) -> None:
        self.records_processed = 0
        ...
```

#### Gold-standard function example

```python
def fetch_hgnc_data(hgnc_url: str) -> pd.DataFrame:
    """Read HGNC data from the specified URL into a pandas DataFrame.

    Parameters
    ----------
    hgnc_url : str
        The URL to download the HGNC data from.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the HGNC data with columns specified in COLUMNS.

    Raises
    ------
    RuntimeError
        If the download fails or the MD5 checksum does not match.
    """
```

#### Gold-standard generator example

```python
def iter_records(path: str, chunk_size: int = 1000) -> Generator[list[dict], None, None]:
    """Yield successive chunks of records from a file.

    Parameters
    ----------
    path : str
        Path to the input file.
    chunk_size : int, optional
        Number of records per chunk. Default is 1000.

    Yields
    ------
    list of dict
        A list of up to `chunk_size` parsed records.
    """
```

#### Gold-standard no-return example (Raises and Returns omitted)

```python
def configure_logging(level: str) -> None:
    """Set the root logger level for the application.

    Parameters
    ----------
    level : str
        Logging level name (e.g. 'DEBUG', 'INFO', 'WARNING').
    """
```

### Phase 4 — REPORT

After editing the file, print a summary table:

| Symbol | Action |
|---|---|
| `module` | Added / Already compliant |
| `function_name` | Added / Rewritten / Already compliant / Skipped |

List every symbol examined. Use "Skipped" for private symbols and `__init__`. Flag any symbol that could not be processed with a warning.

---

## Edge Cases

- **No argument given** — stop and ask for a file path.
- **Non-`.py` file** — stop with an error.
- **File is already fully compliant** — report "Already compliant" for every symbol; do not rewrite unnecessarily.
- **Overloaded methods (`@overload`)** — skip the individual overloads; document the implementation signature only.
- **Abstract methods** — document as normal; note in the summary that the method is abstract if not already obvious.
- **Properties** — document the getter with a one-line summary and a `Returns` section; omit `Parameters`.
- **ASK IF DOUBTS, do not suppose.**