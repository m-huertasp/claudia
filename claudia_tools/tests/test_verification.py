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


def test_fix_attempts_starts_at_zero(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    status = verification.fix_attempts_status(planning)

    assert status == {"attempts": 0, "cap": 3, "cap_reached": False}


def test_fix_attempts_increment_bumps_counter(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    first = verification.fix_attempts_increment(planning)
    second = verification.fix_attempts_increment(planning)

    assert first["attempts"] == 1
    assert second["attempts"] == 2
    assert second["cap_reached"] is False


def test_fix_attempts_reaches_cap_at_third_increment(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    verification.fix_attempts_increment(planning)
    verification.fix_attempts_increment(planning)
    third = verification.fix_attempts_increment(planning)

    assert third == {"attempts": 3, "cap": 3, "cap_reached": True}


def test_fix_attempts_reset_zeroes_counter(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    verification.fix_attempts_increment(planning)
    verification.fix_attempts_increment(planning)

    verification.fix_attempts_reset(planning)

    assert verification.fix_attempts_status(planning)["attempts"] == 0


def test_fix_attempts_handles_missing_planning_dir(tmp_path: Path) -> None:
    planning = tmp_path / "nope"
    # planning dir does not exist yet — increment creates it on demand
    result = verification.fix_attempts_increment(planning)

    assert result["attempts"] == 1
    assert planning.is_dir()


def test_fix_attempts_rejects_corrupt_counter(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "verify-fix-attempts.txt").write_text("not-a-number", encoding="utf-8")

    with pytest.raises(ClaudiaError, match="invalid fix-attempts counter"):
        verification.fix_attempts_status(planning)


def test_fix_attempts_rejects_negative_counter(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "verify-fix-attempts.txt").write_text("-1", encoding="utf-8")

    with pytest.raises(ClaudiaError, match="negative fix-attempts counter"):
        verification.fix_attempts_status(planning)


def test_add_item_rejects_empty_description(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    with pytest.raises(ClaudiaError, match="must not be empty"):
        verification.add_item(planning, "")


def test_add_item_rejects_whitespace_only_description(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    with pytest.raises(ClaudiaError, match="must not be empty"):
        verification.add_item(planning, "   \t  ")


def test_add_item_strips_surrounding_whitespace(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    item = verification.add_item(planning, "  trim me  ")

    assert item.description == "trim me"


def test_exists_returns_false_when_no_verification_md(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    assert verification.exists(planning) is False


def test_exists_returns_true_after_init(tmp_path: Path) -> None:
    planning = _init(tmp_path)

    assert verification.exists(planning) is True
