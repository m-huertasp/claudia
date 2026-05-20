"""Tests for the template renderer."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools.output import ClaudiaError
from claudia_tools.templates import render, render_file, template_variables


def test_template_variables() -> None:
    assert template_variables("# {{ name }} — {{phase}}") == {"name", "phase"}


def test_render_substitutes_all_placeholders() -> None:
    result = render("Project {{ name }}, phase {{ phase }}", {"name": "claudia", "phase": 1})

    assert result == "Project claudia, phase 1"


def test_render_ignores_extra_variables() -> None:
    assert render("hi {{ name }}", {"name": "x", "unused": "y"}) == "hi x"


def test_render_missing_variable_raises() -> None:
    with pytest.raises(ClaudiaError, match="missing template variable\\(s\\): name"):
        render("hi {{ name }}", {})


def test_render_file(tmp_path: Path) -> None:
    template = tmp_path / "t.md"
    template.write_text("# {{ title }}", encoding="utf-8")

    assert render_file(template, {"title": "Roadmap"}) == "# Roadmap"


def test_render_file_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(ClaudiaError, match="no template"):
        render_file(tmp_path / "absent.md", {})
