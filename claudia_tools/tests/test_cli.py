"""End-to-end tests for the claudia CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
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
    assert _data(_invoke(planning_dir, "config", "get", "mode")) == "pair"
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


def test_template_list_lists_bundled_names(planning_dir: Path) -> None:
    result = _invoke(planning_dir, "template", "list")
    names = _data(result)

    assert isinstance(names, list)
    assert {"CONTEXT", "ISSUE_BRIEF", "ROADMAP", "STATE"} <= set(names)


def test_detect_unknown_includes_supported_languages(planning_dir: Path, tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    result = _invoke(planning_dir, "detect", str(empty))
    data = _data(result)

    assert data["primary"] == "unknown"
    assert data["supported"] == ["nextflow", "python"]


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


def test_os_error_is_caught_as_envelope(planning_dir: Path, tmp_path: Path) -> None:
    a_directory = tmp_path / "adir"
    a_directory.mkdir()

    result = _invoke(planning_dir, "template", "render", str(a_directory))

    assert result.exit_code == 1


def test_os_error_message_does_not_leak_errno(planning_dir: Path, tmp_path: Path) -> None:
    """[Errno N] is an implementation detail of Python's OSError repr —
    user-facing CLI messages should not include it."""
    a_directory = tmp_path / "adir"
    a_directory.mkdir()

    result = _invoke(planning_dir, "template", "render", str(a_directory))
    envelope = json.loads(result.output)

    assert envelope["ok"] is False
    assert envelope["error"] is not None
    assert "[Errno" not in envelope["error"]


def test_state_get_on_missing_state_md_returns_clean_error(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    result = _invoke(planning, "state", "get")
    envelope = json.loads(result.output)

    assert envelope["ok"] is False
    assert "[Errno" not in envelope["error"]
    assert "/claudia-plan" in envelope["error"]  # hint at the right next command


def test_phase_list_on_missing_roadmap_returns_clean_error(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    result = _invoke(planning, "phase", "list")
    envelope = json.loads(result.output)

    assert envelope["ok"] is False
    assert "[Errno" not in envelope["error"]
    assert "/claudia-plan" in envelope["error"]


def test_config_init_via_cli(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    result = _invoke(planning, "config", "init")

    assert result.exit_code == 0
    assert (planning / "config.json").exists()


def test_template_render_to_file_via_cli(planning_dir: Path, tmp_path: Path) -> None:
    template = tmp_path / "t.md"
    template.write_text("# {{ title }}", encoding="utf-8")
    target = tmp_path / "out.md"

    result = _invoke(
        planning_dir,
        "template", "render", str(template),
        "--var", "title=Done",
        "--output", str(target),
    )

    assert result.exit_code == 0
    assert target.read_text(encoding="utf-8") == "# Done"


def test_detect_via_cli(planning_dir: Path, tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")

    result = _invoke(planning_dir, "detect", str(tmp_path))

    assert result.exit_code == 0
    assert _data(result)["primary"] == "python"


def test_env_capture_writes_file_via_cli(
    planning_dir: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from claudia_tools import env as env_mod

    class _Fake:
        stdout = "ver-9"
        stderr = ""
        returncode = 0

    monkeypatch.setattr(env_mod.subprocess, "run", lambda *_a, **_kw: _Fake())
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    target = tmp_path / "ENVIRONMENT.md"

    result = _invoke(
        planning_dir,
        "env", "capture", str(tmp_path),
        "--output", str(target),
        "--name", "demo",
    )

    assert result.exit_code == 0
    assert "primary: python" in target.read_text(encoding="utf-8")
    assert "- python: ver-9" in target.read_text(encoding="utf-8")


def test_env_capture_invalid_probe_exits_nonzero(
    planning_dir: Path, tmp_path: Path
) -> None:
    result = _invoke(planning_dir, "env", "capture", str(tmp_path), "--probe", "broken")

    assert result.exit_code == 1


def test_verify_init_add_confirm_ready_round_trip(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()

    assert _invoke(planning, "verify", "init", "--name", "demo").exit_code == 0
    assert _invoke(planning, "verify", "add", "Check output BAMs").exit_code == 0
    assert _invoke(planning, "verify", "add", "Open MultiQC report").exit_code == 0
    # Not ready yet — two pending items.
    assert _invoke(planning, "verify", "ready").exit_code == 1
    assert _invoke(planning, "verify", "confirm", "V1").exit_code == 0
    assert _invoke(planning, "verify", "ready").exit_code == 1
    assert _invoke(planning, "verify", "confirm", "V2").exit_code == 0
    # All confirmed.
    assert _invoke(planning, "verify", "ready").exit_code == 0


def test_verify_list_reflects_state(tmp_path: Path) -> None:
    planning = tmp_path / ".planning"
    planning.mkdir()
    _invoke(planning, "verify", "init")
    _invoke(planning, "verify", "add", "An item")

    items = _data(_invoke(planning, "verify", "list"))

    assert len(items) == 1
    assert items[0]["id"] == "V1"
    assert items[0]["confirmed"] is False
