"""Track the human-run verification checklist that gates ``/claudia-close``.

A ``.planning/VERIFICATION.md`` artifact holds a ``claudia:checklist`` marked
region of ``- [ ] V<N> — <description>`` lines. The verify workflow appends
items via :func:`add_item`; the user clears them via :func:`confirm_item`;
``/claudia-close`` refuses to proceed until :func:`ready` returns ``True``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from claudia_tools.markers import read_region, replace_region
from claudia_tools.output import ClaudiaError, atomic_write, file_lock
from claudia_tools.templates import render_to_file

_FILE = "VERIFICATION.md"
_REGION = "checklist"

# Verify's fix loop: each pass through ``/claudia-verify`` -> /claudia-execute
# bumps this counter; ``/claudia-verify`` escalates to the user once the cap
# is reached. The counter resets on a passing verify verdict.
_FIX_ATTEMPTS_FILE = "verify-fix-attempts.txt"
_FIX_ATTEMPTS_CAP = 3

_ITEM_LINE = re.compile(
    r"^(?P<indent> *)- \[(?P<mark>[ xX])\] (?P<id>V\d+) — (?P<desc>.*)$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ChecklistItem:
    """A single human-checklist entry.

    Attributes
    ----------
    id
        Identifier in the form ``V<N>`` (1-indexed).
    description
        Free-text description of what the user must check.
    confirmed
        Whether the user has ticked the box via ``claudia verify confirm``.
    """

    id: str
    description: str
    confirmed: bool


def _path(planning_dir: Path) -> Path:
    """Return the VERIFICATION.md path inside ``planning_dir``."""
    return Path(planning_dir) / _FILE


def _read(path: Path) -> str:
    """Return the text of ``path``.

    Raises
    ------
    ClaudiaError
        If the file does not exist.
    """
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ClaudiaError(
            f"no verification file at {path}; run `claudia verify init` first"
        ) from exc


def _parse_items(region: str) -> list[ChecklistItem]:
    """Parse :class:`ChecklistItem` entries out of a checklist region."""
    return [
        ChecklistItem(
            id=match["id"],
            description=match["desc"].strip(),
            confirmed=match["mark"] in "xX",
        )
        for match in _ITEM_LINE.finditer(region)
    ]


def init_verification(planning_dir: Path, name: str, force: bool = False) -> Path:
    """Render the bundled VERIFICATION.md template to ``planning_dir``.

    Raises
    ------
    ClaudiaError
        If the file already exists and ``force`` is False.
    """
    target = _path(planning_dir)
    template = resources.files("claudia_tools.data").joinpath("VERIFICATION.md.template")
    with resources.as_file(template) as template_path:
        return render_to_file(template_path, target, {"name": name}, force=force)


def exists(planning_dir: Path) -> bool:
    """Return whether ``.planning/VERIFICATION.md`` is on disk."""
    return _path(planning_dir).is_file()


def list_items(planning_dir: Path) -> list[ChecklistItem]:
    """Return every item in the checklist, in document order."""
    text = _read(_path(planning_dir))
    return _parse_items(read_region(text, _REGION))


def add_item(planning_dir: Path, description: str) -> ChecklistItem:
    """Append a new checklist item and return it.

    Raises
    ------
    ClaudiaError
        If ``description`` is empty after stripping whitespace.
    """
    description = description.strip()
    if not description:
        raise ClaudiaError("checklist item description must not be empty")
    path = _path(planning_dir)
    with file_lock(path):
        text = _read(path)
        region = read_region(text, _REGION)
        existing = _parse_items(region)
        item_id = f"V{len(existing) + 1}"
        new_line = f"- [ ] {item_id} — {description}"
        new_region = region.rstrip("\n") + "\n" + new_line + "\n"
        atomic_write(path, replace_region(text, _REGION, new_region))
    return ChecklistItem(id=item_id, description=description, confirmed=False)


def confirm_item(planning_dir: Path, item_id: str) -> ChecklistItem:
    """Tick the checkbox of ``item_id`` and return the updated item.

    Raises
    ------
    ClaudiaError
        If no item with that id is in the checklist.
    """
    path = _path(planning_dir)
    with file_lock(path):
        text = _read(path)
        region = read_region(text, _REGION)
        matched: list[re.Match[str]] = []

        def _replace(match: re.Match[str]) -> str:
            if match["id"] != item_id:
                return match.group(0)
            matched.append(match)
            return f"{match['indent']}- [x] {match['id']} — {match['desc']}"

        new_region = _ITEM_LINE.sub(_replace, region)
        if not matched:
            raise ClaudiaError(f"no checklist item '{item_id}' in {path}")
        atomic_write(path, replace_region(text, _REGION, new_region))
    return ChecklistItem(id=item_id, description=matched[0]["desc"].strip(), confirmed=True)


def ready(planning_dir: Path) -> bool:
    """Return whether every item in the checklist is confirmed.

    A checklist with **no items** counts as not ready — `/claudia-close` should
    require that `/claudia-verify` actually produced a checklist first.
    """
    items = list_items(planning_dir)
    return bool(items) and all(item.confirmed for item in items)


def require_ready(planning_dir: Path) -> None:
    """Raise unless every checklist item is confirmed.

    Raises
    ------
    ClaudiaError
        Listing the items that are still pending, or noting that the
        checklist is empty.
    """
    items = list_items(planning_dir)
    if not items:
        raise ClaudiaError(
            "verification checklist is empty — run /claudia-verify first"
        )
    pending = [item.id for item in items if not item.confirmed]
    if pending:
        raise ClaudiaError(
            f"blocked — verification items pending: {', '.join(pending)}"
        )


# --- fix-loop counter ------------------------------------------------------


def _fix_attempts_path(planning_dir: Path) -> Path:
    """Return the path of the fix-attempts counter file."""
    return Path(planning_dir) / _FIX_ATTEMPTS_FILE


def _read_fix_attempts(planning_dir: Path) -> int:
    """Return the current fix-attempts count, or 0 if no counter exists yet."""
    path = _fix_attempts_path(planning_dir)
    if not path.exists():
        return 0
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return 0
    try:
        value = int(raw)
    except ValueError as exc:
        raise ClaudiaError(
            f"invalid fix-attempts counter at {path}: {raw!r}"
        ) from exc
    if value < 0:
        raise ClaudiaError(f"negative fix-attempts counter at {path}: {value}")
    return value


def _write_fix_attempts(planning_dir: Path, value: int) -> None:
    """Persist the fix-attempts counter atomically."""
    Path(planning_dir).mkdir(parents=True, exist_ok=True)
    atomic_write(_fix_attempts_path(planning_dir), f"{value}\n")


def _bump_fix_attempts(planning_dir: Path) -> int:
    """Read-modify-write the fix-attempts counter under a lock; return new value."""
    path = _fix_attempts_path(planning_dir)
    with file_lock(path):
        new_value = _read_fix_attempts(planning_dir) + 1
        _write_fix_attempts(planning_dir, new_value)
    return new_value


def fix_attempts_status(planning_dir: Path) -> dict[str, int | bool]:
    """Return the current fix-attempts counter and cap."""
    attempts = _read_fix_attempts(planning_dir)
    return {
        "attempts": attempts,
        "cap": _FIX_ATTEMPTS_CAP,
        "cap_reached": attempts >= _FIX_ATTEMPTS_CAP,
    }


def fix_attempts_increment(planning_dir: Path) -> dict[str, int | bool]:
    """Increment the fix-attempts counter and return the new status."""
    new_value = _bump_fix_attempts(planning_dir)
    return {
        "attempts": new_value,
        "cap": _FIX_ATTEMPTS_CAP,
        "cap_reached": new_value >= _FIX_ATTEMPTS_CAP,
    }


def fix_attempts_reset(planning_dir: Path) -> dict[str, int | bool]:
    """Reset the fix-attempts counter to zero and return the new status."""
    _write_fix_attempts(planning_dir, 0)
    return {"attempts": 0, "cap": _FIX_ATTEMPTS_CAP, "cap_reached": False}
