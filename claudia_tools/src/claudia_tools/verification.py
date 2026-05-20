"""Track the human-run verification checklist that gates ``/claudia-ship``.

A ``.planning/VERIFICATION.md`` artifact holds a ``claudia:checklist`` marked
region of ``- [ ] V<N> — <description>`` lines. The verify workflow appends
items via :func:`add_item`; the user clears them via :func:`confirm_item`;
``/claudia-ship`` refuses to proceed until :func:`ready` returns ``True``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from claudia_tools.markers import read_region, replace_region
from claudia_tools.output import ClaudiaError
from claudia_tools.templates import render_to_file

_FILE = "VERIFICATION.md"
_REGION = "checklist"

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


def list_items(planning_dir: Path) -> list[ChecklistItem]:
    """Return every item in the checklist, in document order."""
    text = _read(_path(planning_dir))
    return _parse_items(read_region(text, _REGION))


def add_item(planning_dir: Path, description: str) -> ChecklistItem:
    """Append a new checklist item and return it."""
    path = _path(planning_dir)
    text = _read(path)
    region = read_region(text, _REGION)
    existing = _parse_items(region)
    item_id = f"V{len(existing) + 1}"
    new_line = f"- [ ] {item_id} — {description}"
    new_region = region.rstrip("\n") + "\n" + new_line + "\n"
    path.write_text(replace_region(text, _REGION, new_region), encoding="utf-8")
    return ChecklistItem(id=item_id, description=description, confirmed=False)


def confirm_item(planning_dir: Path, item_id: str) -> ChecklistItem:
    """Tick the checkbox of ``item_id`` and return the updated item.

    Raises
    ------
    ClaudiaError
        If no item with that id is in the checklist.
    """
    path = _path(planning_dir)
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
    path.write_text(replace_region(text, _REGION, new_region), encoding="utf-8")
    return ChecklistItem(id=item_id, description=matched[0]["desc"].strip(), confirmed=True)


def ready(planning_dir: Path) -> bool:
    """Return whether every item in the checklist is confirmed.

    A checklist with **no items** counts as not ready — `/claudia-ship` should
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
