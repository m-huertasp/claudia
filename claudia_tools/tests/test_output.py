"""Tests for the result envelope and error model."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from claudia_tools.output import (
    EXIT_ERROR,
    EXIT_OK,
    ClaudiaError,
    Result,
    atomic_write,
    emit,
    file_lock,
    render,
)


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


def test_atomic_write_replaces_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "foo.md"
    target.write_text("before", encoding="utf-8")

    atomic_write(target, "after")

    assert target.read_text(encoding="utf-8") == "after"


def test_atomic_write_creates_parent_dirs(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir" / "foo.txt"

    atomic_write(target, "hello")

    assert target.read_text(encoding="utf-8") == "hello"


def test_atomic_write_leaves_no_tmp_files(tmp_path: Path) -> None:
    target = tmp_path / "foo.md"

    atomic_write(target, "hello")

    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith("foo.md.")]
    assert leftovers == []


def test_file_lock_serializes_writers(tmp_path: Path) -> None:
    """Two threads racing on the same file produce a consistent final value.

    Without the lock the read-modify-write sequence loses one update; with
    the lock the second writer waits for the first to commit, so its
    increment is applied to the latest value.
    """
    target = tmp_path / "counter.txt"
    target.write_text("0", encoding="utf-8")

    def increment_once() -> None:
        with file_lock(target):
            current = int(target.read_text(encoding="utf-8"))
            os.sched_yield()  # encourage a context switch mid-section
            atomic_write(target, str(current + 1))

    threads = [threading.Thread(target=increment_once) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert target.read_text(encoding="utf-8") == "20"
