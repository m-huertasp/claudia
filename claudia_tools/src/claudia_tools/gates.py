"""Track review-gate acceptance and block workflow advancement.

A direction-locking artifact (``ROADMAP.md``, ``DECISIONS.md``, the task
breakdown) is only *accepted* once the user clears its review gate. Acceptance
is recorded in ``.planning/gates.json``; :func:`require_accepted` lets a
workflow step refuse to advance until its prerequisites are accepted.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from claudia_tools.output import ClaudiaError

_GATES_FILE = "gates.json"
_ARTIFACT_NAME = re.compile(r"[A-Za-z0-9_.:-]+")

# Logical artifacts that don't correspond to a same-named file on disk.
# Mapped to the file whose existence proves the artifact is real.
#
# ``DECISIONS:intent`` and ``DECISIONS:approach`` are written by the two
# inline-discuss invocations (from /claudia-brief and /claudia-plan
# respectively) so the calling workflow can tell its own discuss outcome
# from the other one's, even though both append to the same DECISIONS.md.
_LOGICAL_ARTIFACTS: dict[str, str] = {
    "STATE-tasks": "STATE.md",
    "DECISIONS:intent": "DECISIONS.md",
    "DECISIONS:approach": "DECISIONS.md",
}


def _validate_artifact(artifact: str) -> None:
    """Reject artifact names outside the safe character set.

    Raises
    ------
    ClaudiaError
        If ``artifact`` contains anything but letters, digits, ``.``, ``_``,
        or ``-`` — keeping path separators and other surprises out of the
        ledger keys.
    """
    if not _ARTIFACT_NAME.fullmatch(artifact):
        raise ClaudiaError(
            f"invalid artifact name '{artifact}' — use letters, digits, '.', '_', '-'"
        )


def _gates_path(planning_dir: Path) -> Path:
    """Return the path of the gates ledger inside ``planning_dir``."""
    return Path(planning_dir) / _GATES_FILE


def _load(planning_dir: Path) -> dict[str, Any]:
    """Return the gates ledger, or an empty mapping if it does not exist."""
    path = _gates_path(planning_dir)
    if not path.exists():
        return {}
    try:
        ledger: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ClaudiaError(f"invalid JSON in {path}: {exc}") from exc
    return ledger


def _save(planning_dir: Path, gates: dict[str, Any]) -> None:
    """Write the gates ledger to disk."""
    _gates_path(planning_dir).write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")


def _artifact_file(planning_dir: Path, artifact: str) -> Path:
    """Return the on-disk file whose existence proves ``artifact`` is real.

    Most artifacts back themselves: ``ROADMAP.md`` lives at
    ``<planning>/ROADMAP.md``. A few — like ``STATE-tasks`` — are logical
    artifacts mapped to the file that actually holds them.
    """
    backing = _LOGICAL_ARTIFACTS.get(artifact, artifact)
    return Path(planning_dir) / backing


def accept(planning_dir: Path, artifact: str) -> dict[str, Any]:
    """Record ``artifact`` as having cleared its review gate.

    Refuses to accept an artifact whose backing file is not on disk —
    review-gate acceptance must follow, not lead, the artifact itself.

    Returns
    -------
    dict
        ``{"artifact", "status", "at", "first_accept", "previous_at"}``
        so callers can audit whether this was a fresh acceptance or a
        re-stamp of a prior one.

    Raises
    ------
    ClaudiaError
        If the artifact name is unsafe, or the backing file is missing.
    """
    _validate_artifact(artifact)
    backing = _artifact_file(planning_dir, artifact)
    if not backing.is_file():
        raise ClaudiaError(
            f"cannot accept '{artifact}': no artifact on disk at {backing}"
        )
    Path(planning_dir).mkdir(parents=True, exist_ok=True)
    gates = _load(planning_dir)
    previous = gates.get(artifact, {}) if isinstance(gates.get(artifact), dict) else {}
    was_accepted = _entry_status(previous) == "accepted"
    timestamp = datetime.now(UTC).isoformat()
    gates[artifact] = {"status": "accepted", "at": timestamp}
    _save(planning_dir, gates)
    return {
        "artifact": artifact,
        "status": "accepted",
        "at": timestamp,
        "first_accept": not was_accepted,
        "previous_at": previous.get("at") if was_accepted else None,
    }


def cancel(planning_dir: Path, artifact: str) -> None:
    """Record that ``artifact``'s review gate was cancelled by the user.

    Unlike :func:`accept`, ``cancel`` does not require the backing file —
    a draft may never have been written. The cancellation is recorded so
    the calling workflow can detect it via :func:`is_cancelled` (or
    ``claudia gate check``) and halt instead of advancing state.
    """
    _validate_artifact(artifact)
    Path(planning_dir).mkdir(parents=True, exist_ok=True)
    gates = _load(planning_dir)
    gates[artifact] = {
        "status": "cancelled",
        "at": datetime.now(UTC).isoformat(),
    }
    _save(planning_dir, gates)


def revoke(planning_dir: Path, artifact: str) -> None:
    """Remove any recorded acceptance/cancellation for ``artifact``.

    Raises
    ------
    ClaudiaError
        If ``artifact`` was never accepted or cancelled (so the user can
        tell that the no-op was actually a no-op).
    """
    _validate_artifact(artifact)
    gates = _load(planning_dir)
    if artifact not in gates:
        raise ClaudiaError(
            f"cannot revoke '{artifact}': no recorded acceptance or cancellation"
        )
    gates.pop(artifact)
    _save(planning_dir, gates)


def _entry_status(entry: object) -> str | None:
    """Return the normalised status from a ledger entry, or None."""
    if not isinstance(entry, dict):
        return None
    if entry.get("status") in ("accepted", "cancelled"):
        return str(entry["status"])
    # Backward-compat with the pre-cancel ledger shape ({"accepted": True}).
    if entry.get("accepted"):
        return "accepted"
    return None


def is_accepted(planning_dir: Path, artifact: str) -> bool:
    """Return whether ``artifact`` has cleared its review gate."""
    return _entry_status(_load(planning_dir).get(artifact)) == "accepted"


def is_cancelled(planning_dir: Path, artifact: str) -> bool:
    """Return whether ``artifact``'s review gate was cancelled."""
    return _entry_status(_load(planning_dir).get(artifact)) == "cancelled"


def require_accepted(planning_dir: Path, *artifacts: str) -> None:
    """Raise if any of ``artifacts`` has not cleared its review gate.

    Raises
    ------
    ClaudiaError
        Naming every artifact that is still blocked.
    """
    blocked = [a for a in artifacts if not is_accepted(planning_dir, a)]
    if blocked:
        raise ClaudiaError(f"blocked — review gate not cleared for: {', '.join(blocked)}")


def status(planning_dir: Path) -> dict[str, Any]:
    """Return the full gates ledger.

    Raises
    ------
    ClaudiaError
        If no ledger has ever been written (no gate has been accepted or
        cancelled yet). Callers should treat the error as "empty ledger"
        rather than a hard failure.
    """
    path = _gates_path(planning_dir)
    if not path.exists():
        raise ClaudiaError(
            f"no gates ledger at {path}; no gate has been accepted or cancelled yet"
        )
    return _load(planning_dir)
