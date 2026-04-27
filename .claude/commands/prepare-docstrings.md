---
description: Create and/or homogenize all docstrings in a Python file using NumPy/SciPy format.
---

# Prepare Docstrings

> Invoke as: `/prepare-docstrings <path-to-python-file>`

**Input**: $ARGUMENTS

---

## Docstring Mode

Reads the given Python file in full, then adds or rewrites every public function, method, and class docstring to conform to the NumPy/SciPy standard.

### Phase 1 — PARSE

Resolve the input path to absolute. If the file does not exist or is not a `.py` file, stop with an error.

### Phase 2 — SCAN

Identify every function, method, and class definition in the file.

For each symbol determine:
- Does it already have a docstring?
- Is the existing docstring already in NumPy/SciPy format?
- What parameters does it accept (names and annotated types, if present)?
- What does it return (annotated type, if present)?
- Does the body contain any explicit `raise` statements?

### Phase 3 — WRITE

Add or rewrite docstrings following the rules below. Edit the source file in-place.

#### Docstring rules

**Style**: NumPy/SciPy format — section headings underlined with dashes (`----------`).

**Structure** (in order):

1. **Summary** — A single concise sentence on the first line.
2. **Description** *(optional)* — A short paragraph explaining the *how* or *why*, separated from the summary by a blank line. Omit if the summary is self-explanatory.
3. **Parameters** — List every argument with its type and a description.
   - If there are no parameters, write `None`.
4. **Returns** — Return type and description.
   - If there is no return value, write `None`.
5. **Raises** — **Only include this section when the function explicitly raises an exception.** If no exceptions are raised, omit the section entirely.

#### Gold-standard example

```python
def fetch_hgnc_data(hgnc_url: str) -> pd.DataFrame:
    """Read HGNC data from the specified URL into a pandas DataFrame.

    This method downloads the data, verifies its MD5 checksum, and parses it
    into a pandas DataFrame.

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
        If the download fails or if the MD5 checksum mismatch occurs.
    """
    try:
      LOG.debug(f"Downloading HGNC data from {hgnc_url} ...")
      response = requests.get(hgnc_url, timeout=10)
      response.raise_for_status()
      if hgnc_url == self.URL:
          self._check_md5(response.content)
      else:
          LOG.warning("Skipping MD5 checksum verification for non-default URL.")
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download HGNC data: {e}") from e
    except MD5MismatchError as e:
        raise RuntimeError(f"MD5 checksum mismatch: {e}") from e

    data = StringIO(response.text)
    df = pd.read_csv(data, sep="\t", dtype=str, na_filter=False, low_memory=False, usecols=self.COLUMNS)
    return df
```

### Phase 4 — REPORT

After editing the file, print a summary table:

| Symbol | Action |
|---|---|
| `function_name` | Added / Rewritten / Already compliant |

List only symbols that were changed or already compliant. Flag any symbol that could not be processed with a warning.
