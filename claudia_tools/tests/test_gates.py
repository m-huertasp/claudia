"""Tests for the review-gate module."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools.gates import (
    accept,
    cancel,
    is_accepted,
    is_cancelled,
    require_accepted,
    revoke,
    status,
)
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


def test_cancel_records_cancellation(planning_dir: Path) -> None:
    cancel(planning_dir, "DECISIONS:intent")

    assert is_cancelled(planning_dir, "DECISIONS:intent") is True
    assert is_accepted(planning_dir, "DECISIONS:intent") is False


def test_cancel_does_not_require_artifact_on_disk(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    cancel(planning, "DECISIONS:intent")  # no raise — draft may never have been written

    assert is_cancelled(planning, "DECISIONS:intent") is True


def test_accept_after_cancel_clears_cancellation(planning_dir: Path) -> None:
    cancel(planning_dir, "DECISIONS:intent")
    accept(planning_dir, "DECISIONS:intent")

    assert is_accepted(planning_dir, "DECISIONS:intent") is True
    assert is_cancelled(planning_dir, "DECISIONS:intent") is False


def test_revoke_clears_cancellation_too(planning_dir: Path) -> None:
    cancel(planning_dir, "DECISIONS:intent")
    revoke(planning_dir, "DECISIONS:intent")

    assert is_cancelled(planning_dir, "DECISIONS:intent") is False


def test_require_accepted_blocks_cancelled_artifact(planning_dir: Path) -> None:
    cancel(planning_dir, "DECISIONS:intent")

    with pytest.raises(ClaudiaError, match="DECISIONS:intent"):
        require_accepted(planning_dir, "DECISIONS:intent")


def test_legacy_ledger_shape_still_reads_as_accepted(planning_dir: Path) -> None:
    # Older claudia versions wrote {"accepted": true} without a "status" key.
    (planning_dir / "gates.json").write_text(
        '{"ROADMAP.md": {"accepted": true, "at": "2026-01-01T00:00:00+00:00"}}',
        encoding="utf-8",
    )

    assert is_accepted(planning_dir, "ROADMAP.md") is True


def test_accept_rejects_unsafe_colon_path_traversal(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="invalid artifact name"):
        accept(planning_dir, "../etc:passwd")


def test_accept_returns_first_accept_true_on_fresh_artifact(planning_dir: Path) -> None:
    result = accept(planning_dir, "ROADMAP.md")

    assert result["first_accept"] is True
    assert result["previous_at"] is None
    assert result["status"] == "accepted"
    assert result["artifact"] == "ROADMAP.md"


def test_accept_returns_first_accept_false_on_restamp(planning_dir: Path) -> None:
    first = accept(planning_dir, "ROADMAP.md")
    second = accept(planning_dir, "ROADMAP.md")

    assert second["first_accept"] is False
    assert second["previous_at"] == first["at"]


def test_revoke_errors_on_never_accepted_artifact(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="no recorded acceptance or cancellation"):
        revoke(planning_dir, "ROADMAP.md")


def test_status_errors_when_no_ledger_exists(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    with pytest.raises(ClaudiaError, match="no gates ledger"):
        status(planning)


def test_status_returns_after_first_accept(planning_dir: Path) -> None:
    accept(planning_dir, "ROADMAP.md")

    ledger = status(planning_dir)

    assert "ROADMAP.md" in ledger
