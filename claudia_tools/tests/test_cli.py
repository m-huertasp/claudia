"""End-to-end tests for the claudia CLI."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from claudia_tools.cli import main


def _invoke(planning_dir: Path, *args: str):
    """Invoke the CLI against ``planning_dir`` and return the click result."""
    return CliRunner().invoke(main, ["--planning-dir", str(planning_dir), *args])


def _data(result) -> object:
    """Return the ``data`` payload from a successful JSON envelope."""
    envelope = json.loads(result.output)
    assert envelope["ok"] is True
    return envelope["data"]


def test_help_lists_all_groups() -> None:
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    for group in ("state", "config", "phase", "template", "gate"):
        assert group in result.output


def test_state_get(planning_dir: Path) -> None:
    result = _invoke(planning_dir, "state", "get")

    assert result.exit_code == 0
    assert _data(result)["current_phase"] == "1"


def test_state_set_persists(planning_dir: Path) -> None:
    assert _invoke(planning_dir, "state", "set", "next_step", "/done").exit_code == 0

    assert _data(_invoke(planning_dir, "state", "get"))["next_step"] == "/done"


def test_state_tasks(planning_dir: Path) -> None:
    tasks = _data(_invoke(planning_dir, "state", "tasks"))

    assert [t["id"] for t in tasks] == ["T1", "T2"]


def test_state_task_done(planning_dir: Path) -> None:
    result = _invoke(planning_dir, "state", "task-done", "T1")

    assert _data(result)["done"] is True


def test_config_get_and_set(planning_dir: Path) -> None:
    assert _data(_invoke(planning_dir, "config", "get", "mode")) == "interactive"
    assert _invoke(planning_dir, "config", "set", "mode", "yolo").exit_code == 0
    assert _data(_invoke(planning_dir, "config", "get", "mode")) == "yolo"


def test_phase_list_and_current(planning_dir: Path) -> None:
    assert len(_data(_invoke(planning_dir, "phase", "list"))) == 2
    assert _data(_invoke(planning_dir, "phase", "current"))["number"] == 2


def test_phase_set_status(planning_dir: Path) -> None:
    result = _invoke(planning_dir, "phase", "set-status", "2", "in progress")

    assert _data(result)["status"] == "in progress"


def test_template_render(planning_dir: Path, tmp_path: Path) -> None:
    template = tmp_path / "t.md"
    template.write_text("# {{ title }}", encoding="utf-8")

    result = _invoke(planning_dir, "template", "render", str(template), "--var", "title=Done")

    assert _data(result) == "# Done"


def test_gate_accept_then_check_passes(planning_dir: Path) -> None:
    assert _invoke(planning_dir, "gate", "accept", "ROADMAP.md").exit_code == 0

    assert _invoke(planning_dir, "gate", "check", "ROADMAP.md").exit_code == 0


def test_gate_check_blocked_exits_nonzero(planning_dir: Path) -> None:
    assert _invoke(planning_dir, "gate", "check", "ROADMAP.md").exit_code == 1


def test_error_command_exits_nonzero(planning_dir: Path) -> None:
    assert _invoke(planning_dir, "config", "set", "bogus", "x").exit_code == 1


def test_text_output_is_not_json(planning_dir: Path) -> None:
    result = CliRunner().invoke(
        main, ["--planning-dir", str(planning_dir), "--text", "state", "get"]
    )

    assert result.exit_code == 0
    assert "current_phase: 1" in result.output
