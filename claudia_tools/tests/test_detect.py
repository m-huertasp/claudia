"""Tests for project-type detection."""

from __future__ import annotations

from pathlib import Path

from claudia_tools.detect import (
    NEXTFLOW,
    PYTHON,
    SUPPORTED_LANGUAGES,
    UNKNOWN,
    detect_project_type,
)


def test_detects_python_only(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

    result = detect_project_type(tmp_path)

    assert result.primary == PYTHON
    assert result.languages == [PYTHON]
    assert result.evidence[PYTHON] == ["pyproject.toml"]


def test_detects_nextflow_only(tmp_path: Path) -> None:
    (tmp_path / "main.nf").write_text("workflow {}\n", encoding="utf-8")
    (tmp_path / "nextflow.config").write_text("", encoding="utf-8")

    result = detect_project_type(tmp_path)

    assert result.primary == NEXTFLOW
    assert "main.nf" in result.evidence[NEXTFLOW]


def test_precedence_nextflow_over_python(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / "main.nf").write_text("", encoding="utf-8")

    result = detect_project_type(tmp_path)

    assert result.primary == NEXTFLOW
    assert result.languages == [NEXTFLOW, PYTHON]


def test_unknown_when_no_markers(tmp_path: Path) -> None:
    result = detect_project_type(tmp_path)

    assert result.primary == UNKNOWN
    assert result.languages == []
    assert result.evidence == {}


def test_unknown_result_exposes_supported_set(tmp_path: Path) -> None:
    result = detect_project_type(tmp_path)

    assert result.supported == list(SUPPORTED_LANGUAGES)
    # Hint should be available on successful detections too.
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    assert detect_project_type(tmp_path).supported == list(SUPPORTED_LANGUAGES)


def test_picks_up_nf_files_in_modules(tmp_path: Path) -> None:
    modules = tmp_path / "modules" / "tool_a"
    modules.mkdir(parents=True)
    (modules / "main.nf").write_text("process A {}\n", encoding="utf-8")

    result = detect_project_type(tmp_path)

    assert result.primary == NEXTFLOW
    assert any("modules" in path for path in result.evidence[NEXTFLOW])
