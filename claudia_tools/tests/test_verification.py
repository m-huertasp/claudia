"""Tests for the human-checklist verification module."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools import verification
from claudia_tools.output import ClaudiaError


def _init(tmp_path: Path) -> Path:
    """Initialise a verification artifact in ``tmp_path`` and return the dir."""
    verification.init_verification(tmp_path, name="demo")
    return tmp_path


def test_init_creates_file_from_template(tmp_path: Path) -> None:
    verification.init_verification(tmp_path, name="demo")
    text = (tmp_path / "VERIFICATION.md").read_text(encoding="utf-8")

    assert "# Verification — demo" in text
    assert "<!-- claudia:checklist -->" in text


def test_init_refuses_existing(tmp_path: Path) -> None:
    verification.init_verification(tmp_path, name="demo")

    with pytest.raises(ClaudiaError, match="already exists"):
        verification.init_verification(tmp_path, name="demo")


def test_init_force_overwrites(tmp_path: Path) -> None:
    verification.init_verification(tmp_path, name="demo")

    verification.init_verification(tmp_path, name="other", force=True)

    assert "Verification — other" in (tmp_path / "VERIFICATION.md").read_text(encoding="utf-8")


def test_list_items_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ClaudiaError, match="no verification file"):
        verification.list_items(tmp_path)


def test_add_item_assigns_sequential_ids(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    first = verification.add_item(planning, "Check the output BAMs")
    second = verification.add_item(planning, "Open the MultiQC report")

    assert (first.id, second.id) == ("V1", "V2")
    items = verification.list_items(planning)
    assert [item.id for item in items] == ["V1", "V2"]
    assert items[0].description == "Check the output BAMs"


def test_confirm_item_ticks_checkbox(tmp_path: Path) -> None:
    planning = _init(tmp_path)
    verification.add_item(planning, "Run pipeline end to end")

    confirmed = verification.confirm_item(planning, "V1")

    assert confirmed.confirmed is True
    assert verification.list_items(planning)[0].confirmed is True


def test_confirm_unknown_item_raises(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    with pytest.raises(ClaudiaError, match="no checklist item 'V9'"):
        verification.confirm_item(planning, "V9")


def test_ready_false_for_empty_checklist(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    assert verification.ready(planning) is False


def test_ready_false_when_pending(tmp_path: Path) -> None:
    planning = _init(tmp_path)
    verification.add_item(planning, "Pending item")

    assert verification.ready(planning) is False


def test_ready_true_when_all_confirmed(tmp_path: Path) -> None:
    planning = _init(tmp_path)
    verification.add_item(planning, "Item 1")
    verification.add_item(planning, "Item 2")
    verification.confirm_item(planning, "V1")
    verification.confirm_item(planning, "V2")

    assert verification.ready(planning) is True


def test_require_ready_blocks_with_pending(tmp_path: Path) -> None:
    planning = _init(tmp_path)
    verification.add_item(planning, "Item A")
    verification.add_item(planning, "Item B")
    verification.confirm_item(planning, "V1")

    with pytest.raises(ClaudiaError, match="V2"):
        verification.require_ready(planning)


def test_require_ready_blocks_with_empty_checklist(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    with pytest.raises(ClaudiaError, match="empty"):
        verification.require_ready(planning)


def test_require_ready_passes_when_all_confirmed(tmp_path: Path) -> None:
    planning = _init(tmp_path)
    verification.add_item(planning, "Item")
    verification.confirm_item(planning, "V1")

    verification.require_ready(planning)  # no raise
