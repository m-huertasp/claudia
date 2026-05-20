"""Tests for environment capture."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from claudia_tools import env
from claudia_tools.detect import PYTHON


class _FakeCompleted:
    """Stand-in for ``subprocess.CompletedProcess`` in tests."""

    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_probe_returns_first_line_of_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        env.subprocess, "run", lambda *_a, **_kw: _FakeCompleted(stdout="Python 3.11.5\nextra\n")
    )

    assert env._probe(("python", "--version")) == "Python 3.11.5"


def test_probe_falls_back_to_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        env.subprocess, "run", lambda *_a, **_kw: _FakeCompleted(stderr="nextflow 23.04.4")
    )

    assert env._probe(("nextflow", "-version")) == "nextflow 23.04.4"


def test_probe_returns_none_on_missing_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*_a: object, **_kw: object) -> None:
        raise FileNotFoundError

    monkeypatch.setattr(env.subprocess, "run", _raise)

    assert env._probe(("does-not-exist", "--version")) is None


def test_probe_returns_none_on_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*_a: object, **_kw: object) -> None:
        raise subprocess.TimeoutExpired(cmd="x", timeout=1)

    monkeypatch.setattr(env.subprocess, "run", _raise)

    assert env._probe(("slow", "--version")) is None


def test_probe_returns_none_on_nonzero_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        env.subprocess, "run", lambda *_a, **_kw: _FakeCompleted(stdout="bang", returncode=2)
    )

    assert env._probe(("broken", "--version")) is None


def test_capture_environment_includes_detection_and_tools(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    monkeypatch.setattr(env.subprocess, "run", lambda *_a, **_kw: _FakeCompleted(stdout="vX\n"))

    snapshot = env.capture_environment(tmp_path)

    assert snapshot.project_type.primary == PYTHON
    assert {tool.name for tool in snapshot.tools} >= {"python", "nextflow", "ruff"}
    assert all(tool.version == "vX" for tool in snapshot.tools)
    assert snapshot.captured_at  # ISO 8601 string is non-empty


def test_extra_probes_merge_with_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env.subprocess, "run", lambda *_a, **_kw: _FakeCompleted(stdout="custom"))

    snapshot = env.capture_environment(
        tmp_path, extra_probes={"bcftools": ("bcftools", "--version")}
    )

    names = {tool.name for tool in snapshot.tools}
    assert "bcftools" in names
    assert "python" in names  # defaults still present


def test_write_environment_file_renders_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "main.nf").write_text("", encoding="utf-8")
    monkeypatch.setattr(env.subprocess, "run", lambda *_a, **_kw: _FakeCompleted(stdout="v1.2.3"))
    snapshot = env.capture_environment(tmp_path)
    target = tmp_path / "ENVIRONMENT.md"

    env.write_environment_file(snapshot, "demo", target)

    text = target.read_text(encoding="utf-8")
    assert "# Environment — demo" in text
    assert "primary: nextflow" in text
    assert "- python: v1.2.3" in text


def test_write_environment_file_refuses_existing(tmp_path: Path) -> None:
    target = tmp_path / "ENVIRONMENT.md"
    target.write_text("existing", encoding="utf-8")
    snapshot = env.capture_environment(tmp_path)

    with pytest.raises(Exception, match="already exists"):
        env.write_environment_file(snapshot, "demo", target)
