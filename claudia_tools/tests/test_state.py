"""Tests for the STATE.md state module."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools.output import ClaudiaError
from claudia_tools.state import read_status, read_tasks, set_status_field, set_task_done


def test_read_status_fields(planning_dir: Path) -> None:
    status = read_status(planning_dir / "STATE.md")

    assert status["current_phase"] == "1"
    assert status["next_step"] == "/claudia-execute"


def test_set_status_field_persists(planning_dir: Path) -> None:
    state = planning_dir / "STATE.md"

    set_status_field(state, "next_step", "/claudia-verify")

    assert read_status(state)["next_step"] == "/claudia-verify"


def test_set_status_field_keeps_human_prose(planning_dir: Path) -> None:
    state = planning_dir / "STATE.md"

    set_status_field(state, "current_phase", "2")

    assert "Human-owned prose" in state.read_text(encoding="utf-8")


def test_set_unknown_status_field_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="unknown status field"):
        set_status_field(planning_dir / "STATE.md", "bogus", "x")


def test_read_tasks(planning_dir: Path) -> None:
    tasks = read_tasks(planning_dir / "STATE.md")

    assert [t.id for t in tasks] == ["T1", "T2"]
    assert tasks[0].done is False
    assert tasks[1].done is True


def test_set_task_done_ticks_checkbox(planning_dir: Path) -> None:
    state = planning_dir / "STATE.md"

    returned = set_task_done(state, "T1")

    assert returned.done is True
    assert read_tasks(state)[0].done is True


def test_set_task_done_can_untick(planning_dir: Path) -> None:
    state = planning_dir / "STATE.md"

    set_task_done(state, "T2", done=False)

    assert read_tasks(state)[1].done is False


def test_set_task_done_unknown_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="no task 'T9'"):
        set_task_done(planning_dir / "STATE.md", "T9")


def test_consecutive_status_updates_both_persist(planning_dir: Path) -> None:
    state = planning_dir / "STATE.md"

    set_status_field(state, "next_step", "/a")
    set_status_field(state, "last_command", "/b")

    status = read_status(state)
    assert status["next_step"] == "/a"
    assert status["last_command"] == "/b"
