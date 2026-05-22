"""Tests for the STATE.md state module."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools.output import ClaudiaError
from claudia_tools.state import (
    add_task,
    init_state,
    read_status,
    read_tasks,
    remove_task,
    set_status_field,
    set_task_done,
)


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


def test_init_state_writes_template(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    target = init_state(planning, name="myproj")

    assert target == planning / "STATE.md"
    text = target.read_text(encoding="utf-8")
    assert text.startswith("# State — myproj")
    assert "current_phase: 1" in text


def test_init_state_refuses_existing_without_force(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    init_state(planning)

    with pytest.raises(ClaudiaError, match="already exists"):
        init_state(planning)


def test_init_state_force_overwrites(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    init_state(planning, name="first")

    init_state(planning, name="second", force=True)

    assert (planning / "STATE.md").read_text(encoding="utf-8").startswith("# State — second")


def test_set_status_field_auto_creates_state_md(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"
    assert not state_path.exists()

    set_status_field(state_path, "last_command", "/claudia-understand")

    assert state_path.exists()
    status = read_status(state_path)
    assert status["last_command"] == "/claudia-understand"
    assert status["current_phase"] == "1"  # template default preserved


def test_set_status_field_after_auto_create_supports_further_sets(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"

    set_status_field(state_path, "last_command", "/a")
    set_status_field(state_path, "next_step", "/b")

    status = read_status(state_path)
    assert status["last_command"] == "/a"
    assert status["next_step"] == "/b"


def test_add_task_on_fresh_state_starts_at_t1(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"

    task = add_task(state_path, "First task")

    assert task.id == "T1"
    assert task.title == "First task"
    assert task.done is False
    tasks = read_tasks(state_path)
    assert [(t.id, t.title) for t in tasks] == [("T1", "First task")]


def test_add_task_auto_creates_state_md(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"
    assert not state_path.exists()

    add_task(state_path, "Bootstrap task")

    assert state_path.exists()


def test_add_task_increments_id_monotonically(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"
    init_state(planning)

    a = add_task(state_path, "A")
    b = add_task(state_path, "B")
    c = add_task(state_path, "C")

    assert (a.id, b.id, c.id) == ("T1", "T2", "T3")


def test_add_task_does_not_reuse_removed_ids(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"
    init_state(planning)
    add_task(state_path, "A")
    add_task(state_path, "B")
    remove_task(state_path, "T1")

    next_task = add_task(state_path, "C")

    assert next_task.id == "T3"  # not T1 — ids are stable


def test_add_task_rejects_empty_title(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="must not be empty"):
        add_task(planning_dir / "STATE.md", "   ")


def test_remove_task_unknown_id_raises(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"
    init_state(planning)
    add_task(state_path, "A")

    with pytest.raises(ClaudiaError, match="no task 'T99'"):
        remove_task(state_path, "T99")


def test_add_task_preserves_done_state_of_others(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"
    init_state(planning)
    add_task(state_path, "First")
    set_task_done(state_path, "T1", done=True)

    add_task(state_path, "Second")

    tasks = read_tasks(state_path)
    by_id = {t.id: t for t in tasks}
    assert by_id["T1"].done is True
    assert by_id["T2"].done is False


def test_add_task_replaces_template_placeholder(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    state_path = planning / "STATE.md"
    init_state(planning)
    assert "none yet" in state_path.read_text(encoding="utf-8")

    add_task(state_path, "Real task")

    text = state_path.read_text(encoding="utf-8")
    assert "none yet" not in text
    assert "- [ ] T1 — Real task" in text
