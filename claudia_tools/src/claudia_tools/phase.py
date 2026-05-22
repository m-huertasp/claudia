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
from claudia_tools.output import ClaudiaError, atomic_write, file_lock

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
    """Return the text of ``path``.

    Raises
    ------
    ClaudiaError
        If the file does not exist, with a hint at the right next command.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ClaudiaError(
            f"no ROADMAP.md at {path}; run /claudia-plan first to render it"
        ) from exc


def _parse_phases(text: str) -> list[Phase]:
    """Parse every phase out of the given ROADMAP.md ``text``.

    Raises
    ------
    ClaudiaError
        If a phase has no ``status-N`` region or an unrecognised status.
    """
    phases: list[Phase] = []
    for match in _PHASE_HEADING.finditer(text):
        number = int(match["num"])
        region = f"status-{number}"
        if not has_region(text, region):
            raise ClaudiaError(f"phase {number} has no '{region}' marked region")
        status = read_region(text, region).strip()
        if status not in STATUSES:
            raise ClaudiaError(f"phase {number} has invalid status '{status}'")
        phases.append(Phase(number=number, title=match["title"].strip(), status=status))
    return phases


def read_phases(path: Path) -> list[Phase]:
    """Return every phase declared in ``ROADMAP.md``, in order.

    Raises
    ------
    ClaudiaError
        If a phase has no ``status-N`` region or an unrecognised status.
    """
    return _parse_phases(_read(path))


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
        If ``number`` is not in the roadmap, or ``status`` is not valid.
        Phase-existence is checked first so a user who passed both wrong
        arguments learns about the missing phase rather than the status.
    """
    with file_lock(Path(path)):
        text = _read(path)
        phases = {phase.number: phase for phase in _parse_phases(text)}
        if number not in phases:
            raise ClaudiaError(f"no phase {number} in roadmap")
        if status not in STATUSES:
            raise ClaudiaError(f"status must be one of {list(STATUSES)}, got '{status}'")
        atomic_write(Path(path), replace_region(text, f"status-{number}", status))
    return Phase(number=number, title=phases[number].title, status=status)
