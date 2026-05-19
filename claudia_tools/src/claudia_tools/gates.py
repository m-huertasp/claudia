"""Track review-gate acceptance and block workflow advancement.

A direction-locking artifact (``ROADMAP.md``, ``DECISIONS.md``, the task
breakdown) is only *accepted* once the user clears its review gate. Acceptance
is recorded in ``.planning/gates.json``; :func:`require_accepted` lets a
workflow step refuse to advance until its prerequisites are accepted.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from claudia_tools.output import ClaudiaError

_GATES_FILE = "gates.json"


def _gates_path(planning_dir: Path) -> Path:
    """Return the path of the gates ledger inside ``planning_dir``."""
    return Path(planning_dir) / _GATES_FILE


def _load(planning_dir: Path) -> dict[str, Any]:
    """Return the gates ledger, or an empty mapping if it does not exist."""
    path = _gates_path(planning_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ClaudiaError(f"invalid JSON in {path}: {exc}") from exc


def _save(planning_dir: Path, gates: dict[str, Any]) -> None:
    """Write the gates ledger to disk."""
    _gates_path(planning_dir).write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")


def accept(planning_dir: Path, artifact: str) -> None:
    """Record ``artifact`` as having cleared its review gate."""
    gates = _load(planning_dir)
    gates[artifact] = {"accepted": True, "at": datetime.now(timezone.utc).isoformat()}
    _save(planning_dir, gates)


def revoke(planning_dir: Path, artifact: str) -> None:
    """Remove any recorded acceptance for ``artifact``."""
    gates = _load(planning_dir)
    gates.pop(artifact, None)
    _save(planning_dir, gates)


def is_accepted(planning_dir: Path, artifact: str) -> bool:
    """Return whether ``artifact`` has cleared its review gate."""
    return bool(_load(planning_dir).get(artifact, {}).get("accepted", False))


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
    """Return the full gates ledger."""
    return _load(planning_dir)
