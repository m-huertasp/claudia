"""Tests for the roadmap phase module."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools.output import ClaudiaError
from claudia_tools.phase import current_phase, read_phases, set_phase_status


def test_read_phases(planning_dir: Path) -> None:
    phases = read_phases(planning_dir / "ROADMAP.md")

    assert [p.number for p in phases] == [1, 2]
    assert phases[0].title == "Foundation"
    assert phases[0].status == "complete"
    assert phases[1].status == "not started"


def test_current_phase_is_first_incomplete(planning_dir: Path) -> None:
    assert current_phase(planning_dir / "ROADMAP.md").number == 2


def test_set_phase_status_persists(planning_dir: Path) -> None:
    roadmap = planning_dir / "ROADMAP.md"

    updated = set_phase_status(roadmap, 2, "in progress")

    assert updated.status == "in progress"
    assert read_phases(roadmap)[1].status == "in progress"


def test_set_invalid_status_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="status must be one of"):
        set_phase_status(planning_dir / "ROADMAP.md", 1, "done-ish")


def test_set_unknown_phase_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="no phase 9"):
        set_phase_status(planning_dir / "ROADMAP.md", 9, "complete")


def test_current_phase_all_complete_raises(planning_dir: Path) -> None:
    roadmap = planning_dir / "ROADMAP.md"
    set_phase_status(roadmap, 2, "complete")

    with pytest.raises(ClaudiaError, match="all phases are complete"):
        current_phase(roadmap)


def test_read_phases_rejects_invalid_status(planning_dir: Path) -> None:
    roadmap = planning_dir / "ROADMAP.md"
    roadmap.write_text(
        roadmap.read_text(encoding="utf-8").replace("not started", "wip"),
        encoding="utf-8",
    )

    with pytest.raises(ClaudiaError, match="invalid status 'wip'"):
        read_phases(roadmap)
