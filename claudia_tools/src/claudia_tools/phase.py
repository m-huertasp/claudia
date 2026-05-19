"""Read roadmap phases and transition their status.

``ROADMAP.md`` lists one ``## Phase N — Title`` heading per phase. Each phase's
status sits in an inline marked region named ``status-N`` so the CLI can move
a phase between states without rewriting the surrounding prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from claudia_tools.markers import has_region, read_region, replace_region
from claudia_tools.output import ClaudiaError

_PHASE_HEADING = re.compile(r"^## Phase (?P<num>\d+) — (?P<title>.+)$", re.MULTILINE)

STATUSES = ("not started", "in progress", "complete")


@dataclass(frozen=True)
class Phase:
    """A single roadmap phase.

    Attributes
    ----------
    number
        The phase number.
    title
        The phase title.
    status
        One of :data:`STATUSES`.
    """

    number: int
    title: str
    status: str


def _read(path: Path) -> str:
    """Return the text of ``path``."""
    return Path(path).read_text(encoding="utf-8")


def read_phases(path: Path) -> list[Phase]:
    """Return every phase declared in ``ROADMAP.md``, in order.

    Raises
    ------
    ClaudiaError
        If a phase heading has no matching ``status-N`` marked region.
    """
    text = _read(path)
    phases: list[Phase] = []
    for match in _PHASE_HEADING.finditer(text):
        number = int(match["num"])
        region = f"status-{number}"
        if not has_region(text, region):
            raise ClaudiaError(f"phase {number} has no '{region}' marked region")
        phases.append(
            Phase(number=number, title=match["title"].strip(), status=read_region(text, region))
        )
    return phases


def current_phase(path: Path) -> Phase:
    """Return the first phase that is not yet complete.

    Raises
    ------
    ClaudiaError
        If every phase is complete.
    """
    for phase in read_phases(path):
        if phase.status != "complete":
            return phase
    raise ClaudiaError("all phases are complete")


def set_phase_status(path: Path, number: int, status: str) -> Phase:
    """Set the status of phase ``number`` and return the updated phase.

    Raises
    ------
    ClaudiaError
        If ``status`` is not a valid status or ``number`` is not in the roadmap.
    """
    if status not in STATUSES:
        raise ClaudiaError(f"status must be one of {list(STATUSES)}, got '{status}'")
    phases = {phase.number: phase for phase in read_phases(path)}
    if number not in phases:
        raise ClaudiaError(f"no phase {number} in roadmap")
    text = _read(path)
    Path(path).write_text(
        replace_region(text, f"status-{number}", status), encoding="utf-8"
    )
    return Phase(number=number, title=phases[number].title, status=status)
