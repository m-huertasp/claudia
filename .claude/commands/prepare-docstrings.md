---
description: Create and/or homogenize all docstrings in a Python file using NumPy/SciPy format.
---

# Prepare Docstrings

> Invoke as: `/prepare-docstrings <path-to-python-file>`

**Input**: $ARGUMENTS

---

## Docstring Mode

Read the given Python file in full, then add or rewrite every public function, method, and class docstring to conform to the NumPy/SciPy standard.

### Phase 1 — PARSE

Resolve the input path to absolute. If no argument is given, stop and ask the user for a file path. If the file does not exist or is not a `.py` file, stop with an error.

### Phase 2 — SCAN

Read the entire file. Identify every function, method, and class definition.

For each symbol determine:
- Does it already have a docstring?
- Is the existing docstring already in NumPy/SciPy format?
- What parameters does it accept? Collect names and annotated types, excluding `self` and `cls`.
- What does it return (annotated type, if present)?
- Does the body contain any explicit `raise` statements?
- Is it a `property`, `classmethod`, or `staticmethod`?

**Symbol inclusion rules:**

| Symbol | Include? |
|---|---|
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
4. **Returns** — Return type and description. **Omit this section entirely if the function returns `None` or has no return statement.**
5. **Raises** — Only include when the function body contains explicit `raise` statements. **Omit entirely if no exceptions are raised.**

#### Parameter formatting

```
name : type
    Description of the parameter.
```

For `*args` use `*args : type` and for `**kwargs` use `**kwargs : type`. If no type annotation exists and the type cannot be inferred from context, use `any`.

#### Class docstrings

Document the class purpose and its `__init__` parameters in the class-level docstring. Do not add a separate docstring to `__init__`.

```python
class MyProcessor:
    """Process input data and emit transformed records.

    Parameters
    ----------
    config : Config
        Configuration object controlling processing behavior.
    verbose : bool, optional
        If True, emit progress logs. Default is False.
    """

    def __init__(self, config: Config, verbose: bool = False) -> None:
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
| `function_name` | Added / Rewritten / Already compliant / Skipped |

List every symbol examined. Use "Skipped" for private symbols and `__init__`. Flag any symbol that could not be processed with a warning.

---

## Edge Cases

- **No argument given** — stop and ask for a file path.
- **Non-`.py` file** — stop with an error.
- **File is already fully compliant** — report "Already compliant" for every symbol; do not rewrite unnecessarily.
- **Overloaded methods (`@overload`)** — skip the individual overloads; document the implementation signature only.
- **Abstract methods** — document as normal; note in the summary that the method is abstract if not already obvious.
- **ASK IF DOUBTS, do not suppose.**
