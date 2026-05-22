"""Tests for the review-gate module."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools.gates import accept, is_accepted, require_accepted, revoke, status
from claudia_tools.output import ClaudiaError


def test_unaccepted_by_default(planning_dir: Path) -> None:
    assert is_accepted(planning_dir, "ROADMAP.md") is False


def test_accept_then_accepted(planning_dir: Path) -> None:
    accept(planning_dir, "ROADMAP.md")

    assert is_accepted(planning_dir, "ROADMAP.md") is True


def test_require_accepted_passes_when_cleared(planning_dir: Path) -> None:
    accept(planning_dir, "ROADMAP.md")
    accept(planning_dir, "DECISIONS.md")

    require_accepted(planning_dir, "ROADMAP.md", "DECISIONS.md")  # no raise


def test_require_accepted_blocks_and_names_artifacts(planning_dir: Path) -> None:
    accept(planning_dir, "ROADMAP.md")

    with pytest.raises(ClaudiaError, match="DECISIONS.md"):
        require_accepted(planning_dir, "ROADMAP.md", "DECISIONS.md")


def test_revoke_clears_acceptance(planning_dir: Path) -> None:
    accept(planning_dir, "ROADMAP.md")
    revoke(planning_dir, "ROADMAP.md")

    assert is_accepted(planning_dir, "ROADMAP.md") is False


def test_status_returns_ledger(planning_dir: Path) -> None:
    accept(planning_dir, "ROADMAP.md")

    assert "ROADMAP.md" in status(planning_dir)


def test_invalid_ledger_raises(planning_dir: Path) -> None:
    (planning_dir / "gates.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(ClaudiaError, match="invalid JSON"):
        is_accepted(planning_dir, "ROADMAP.md")


def test_accept_rejects_unsafe_artifact_name(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="invalid artifact name"):
        accept(planning_dir, "../../etc/passwd")


def test_accept_refuses_when_artifact_missing(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    with pytest.raises(ClaudiaError, match="no artifact on disk"):
        accept(planning, "ROADMAP.md")


def test_accept_state_tasks_maps_to_state_md(planning_dir: Path) -> None:
    accept(planning_dir, "STATE-tasks")

    assert is_accepted(planning_dir, "STATE-tasks") is True


def test_accept_state_tasks_refuses_when_state_md_missing(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    with pytest.raises(ClaudiaError, match="no artifact on disk"):
        accept(planning, "STATE-tasks")
