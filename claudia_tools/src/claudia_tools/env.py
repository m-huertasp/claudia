"""Capture the local environment a claudia project depends on.

Probes a fixed registry of bioinformatics-relevant tools (Python, uv, conda,
Nextflow, nf-test, container runtimes, lint/type/test tooling) by invoking
each tool's version flag via :mod:`subprocess`. A tool that is not on PATH,
times out, or exits non-zero records ``version=None`` — the capture never
fails on a missing tool.
"""

from __future__ import annotations

import subprocess  # noqa: S404 - tool-version probes use a fixed argv list
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path

from claudia_tools.detect import Detection, detect_project_type
from claudia_tools.templates import render_to_file

_PROBE_TIMEOUT_SECONDS = 5

DEFAULT_PROBES: dict[str, tuple[str, ...]] = {
    "python":      ("python3",     "--version"),
    "uv":          ("uv",          "--version"),
    "conda":       ("conda",       "--version"),
    "mamba":       ("mamba",       "--version"),
    "nextflow":    ("nextflow",    "-version"),
    "nf-test":     ("nf-test",     "--version"),
    "docker":      ("docker",      "--version"),
    "singularity": ("singularity", "--version"),
    "apptainer":   ("apptainer",   "--version"),
    "pytest":      ("pytest",      "--version"),
    "ruff":        ("ruff",        "--version"),
    "mypy":        ("mypy",        "--version"),
}


@dataclass(frozen=True)
class ToolVersion:
    """A single probed tool.

    Attributes
    ----------
    name
        The tool's short name (e.g. ``"nextflow"``).
    version
        The first line of the tool's version output, or ``None`` if the tool
        is not on PATH, timed out, or exited non-zero.
    command
        The argv joined with spaces — useful for the audit trail.
    """

    name: str
    version: str | None
    command: str


@dataclass(frozen=True)
class Environment:
    """A snapshot of the local environment.

    Attributes
    ----------
    project_type
        Result of :func:`claudia_tools.detect.detect_project_type`.
    tools
        Versions of every probed tool.
    captured_at
        ISO 8601 UTC timestamp of the capture.
    """

    project_type: Detection
    tools: list[ToolVersion] = field(default_factory=list)
    captured_at: str = ""


def _probe(cmd: tuple[str, ...]) -> str | None:
    """Run ``cmd`` and return the first line of its version output, or None."""
    try:
        result = subprocess.run(  # noqa: S603 - argv is a fixed tuple from the registry
            cmd,
            capture_output=True,
            text=True,
            timeout=_PROBE_TIMEOUT_SECONDS,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    output = (result.stdout or result.stderr).strip()
    return output.splitlines()[0] if output else None


def capture_environment(
    root: Path,
    extra_probes: dict[str, tuple[str, ...]] | None = None,
) -> Environment:
    """Return an :class:`Environment` snapshot of ``root``.

    Parameters
    ----------
    root
        The repository root to detect project type against.
    extra_probes
        Optional mapping merged into :data:`DEFAULT_PROBES`. Same-name keys
        override the default; new keys are added.
    """
    probes = dict(DEFAULT_PROBES)
    if extra_probes:
        probes.update(extra_probes)
    tools = [
        ToolVersion(name=name, version=_probe(cmd), command=" ".join(cmd))
        for name, cmd in probes.items()
    ]
    return Environment(
        project_type=detect_project_type(root),
        tools=tools,
        captured_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )


def _render_project_type(detection: Detection) -> str:
    """Format a :class:`Detection` for the ``claudia:project-type`` region."""
    lines = [f"- primary: {detection.primary}"]
    if detection.languages:
        lines.append(f"- languages: {', '.join(detection.languages)}")
    for language, paths in detection.evidence.items():
        lines.append(f"- evidence ({language}): {', '.join(paths)}")
    return "\n".join(lines)


def _render_tools(tools: list[ToolVersion]) -> str:
    """Format a list of :class:`ToolVersion` for the ``claudia:tools`` region."""
    return "\n".join(
        f"- {tool.name}: {tool.version if tool.version is not None else 'not installed'}"
        for tool in tools
    )


def write_environment_file(
    snapshot: Environment,
    name: str,
    target: Path,
    force: bool = False,
) -> Path:
    """Render the bundled ENVIRONMENT.md template for ``snapshot`` to ``target``.

    Returns the path written.

    Raises
    ------
    ClaudiaError
        If ``target`` exists and ``force`` is False.
    """
    template = resources.files("claudia_tools.data").joinpath("ENVIRONMENT.md.template")
    variables = {
        "name": name,
        "captured_at": snapshot.captured_at,
        "project_type": _render_project_type(snapshot.project_type),
        "tools": _render_tools(snapshot.tools),
    }
    with resources.as_file(template) as template_path:
        return render_to_file(template_path, target, variables, force=force)
