"""Detect the primary project type of a repository.

Recognises Python libraries (`pyproject.toml`, `setup.py`, `requirements.txt`)
and Nextflow pipelines (`main.nf`, `nextflow.config`, any `*.nf` under
`modules/` or `workflows/`). Precedence: **nextflow > python > unknown** —
a repository that contains both is reported as primary-nextflow with
python listed as a secondary language.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PYTHON = "python"
NEXTFLOW = "nextflow"
UNKNOWN = "unknown"

_PYTHON_MARKERS = ("pyproject.toml", "setup.py", "requirements.txt")
_NEXTFLOW_MARKERS = ("main.nf", "nextflow.config")
_NEXTFLOW_SUBDIRS = ("modules", "workflows", "subworkflows")


@dataclass(frozen=True)
class Detection:
    """The result of detecting a repository's project type.

    Attributes
    ----------
    primary
        ``"nextflow"``, ``"python"``, or ``"unknown"``.
    languages
        Every language detected, in precedence order.
    evidence
        For each language, the list of marker file paths (relative to the
        repository root) that triggered the detection.
    """

    primary: str
    languages: list[str] = field(default_factory=list)
    evidence: dict[str, list[str]] = field(default_factory=dict)


def _find_python_evidence(root: Path) -> list[str]:
    """Return relative paths of any Python marker files under ``root``."""
    return [name for name in _PYTHON_MARKERS if (root / name).is_file()]


def _find_nextflow_evidence(root: Path) -> list[str]:
    """Return relative paths of any Nextflow marker files under ``root``."""
    found = [name for name in _NEXTFLOW_MARKERS if (root / name).is_file()]
    for subdir in _NEXTFLOW_SUBDIRS:
        path = root / subdir
        if not path.is_dir():
            continue
        for nf_file in sorted(path.rglob("*.nf")):
            found.append(str(nf_file.relative_to(root)))
            break  # one example is enough as evidence
    return found


def detect_project_type(root: Path) -> Detection:
    """Detect the primary project type of the repository at ``root``."""
    evidence: dict[str, list[str]] = {}
    nextflow = _find_nextflow_evidence(root)
    python = _find_python_evidence(root)
    if nextflow:
        evidence[NEXTFLOW] = nextflow
    if python:
        evidence[PYTHON] = python
    languages = [lang for lang in (NEXTFLOW, PYTHON) if lang in evidence]
    primary = languages[0] if languages else UNKNOWN
    return Detection(primary=primary, languages=languages, evidence=evidence)
