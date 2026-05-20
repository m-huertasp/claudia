"""Tests for the result envelope and error model."""

from __future__ import annotations

import json

from claudia_tools.output import EXIT_ERROR, EXIT_OK, ClaudiaError, Result, emit, render


def test_success_builds_ok_envelope() -> None:
    result = Result.success({"phase": 1})

    assert result.to_envelope() == {"ok": True, "data": {"phase": 1}, "error": None}


def test_failure_builds_error_envelope() -> None:
    result = Result.failure("no phase 99")

    assert result.to_envelope() == {"ok": False, "data": None, "error": "no phase 99"}


def test_render_json_is_parseable() -> None:
    rendered = render(Result.success({"a": 1}))

    assert json.loads(rendered) == {"ok": True, "data": {"a": 1}, "error": None}


def test_render_text_success_variants() -> None:
    assert render(Result.success(None), as_text=True) == "ok"
    assert render(Result.success("hello"), as_text=True) == "hello"
    assert render(Result.success({"k": "v"}), as_text=True) == "k: v"
    assert render(Result.success(["a", "b"]), as_text=True) == "a\nb"
    assert render(Result.success(7), as_text=True) == "7"


def test_render_text_failure() -> None:
    assert render(Result.failure("boom"), as_text=True) == "error: boom"


def test_emit_success_returns_ok_code(capsys) -> None:
    code = emit(Result.success("done"))

    assert code == EXIT_OK
    assert "done" not in capsys.readouterr().err


def test_emit_failure_returns_error_code_on_stderr(capsys) -> None:
    code = emit(Result.failure("bad"), as_text=True)
    captured = capsys.readouterr()

    assert code == EXIT_ERROR
    assert "error: bad" in captured.err
    assert captured.out == ""


def test_claudia_error_is_an_exception() -> None:
    assert issubclass(ClaudiaError, Exception)
