"""The result envelope and error model shared by every ``claudia`` command.

Every command produces a :class:`Result`. It is rendered either as the JSON
envelope ``{"ok", "data", "error"}`` (the default, for the orchestrating
model) or as human-readable text (``--text``). A failed result is written to
stderr and maps to a non-zero exit code.

This module also exposes :func:`file_lock` and :func:`atomic_write`, the two
primitives every state-mutating command uses to make its read-modify-write
cycle safe under concurrent invocation.
"""

from __future__ import annotations

import fcntl
import json
import os
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_ERROR = 1


class ClaudiaError(Exception):
    """An expected, user-facing failure.

    Raised by the library for conditions the user can act on (a missing file,
    an invalid value). The CLI catches it and renders a failed envelope rather
    than a traceback.
    """


@dataclass(frozen=True)
class Result:
    """The outcome of a command.

    Attributes
    ----------
    ok
        Whether the command succeeded.
    data
        The payload on success; ``None`` on failure.
    error
        The error message on failure; ``None`` on success.
    """

    ok: bool
    data: Any = None
    error: str | None = None

    @classmethod
    def success(cls, data: Any = None) -> Result:
        """Return a successful result carrying ``data``."""
        return cls(ok=True, data=data, error=None)

    @classmethod
    def failure(cls, message: str) -> Result:
        """Return a failed result carrying ``message``."""
        return cls(ok=False, data=None, error=message)

    def to_envelope(self) -> dict[str, Any]:
        """Return the ``{ok, data, error}`` envelope as a plain dict."""
        return {"ok": self.ok, "data": self.data, "error": self.error}


def _render_text(data: Any) -> str:
    """Render a payload as human-readable text."""
    if data is None:
        return "ok"
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        return "\n".join(f"{key}: {value}" for key, value in data.items())
    if isinstance(data, list):
        return "\n".join(str(item) for item in data)
    return str(data)


def render(result: Result, *, as_text: bool = False) -> str:
    """Render ``result`` as a string.

    Parameters
    ----------
    result
        The result to render.
    as_text
        When ``True``, produce human-readable text; otherwise the JSON
        envelope.
    """
    if as_text:
        return _render_text(result.data) if result.ok else f"error: {result.error}"
    return json.dumps(result.to_envelope(), indent=2)


def emit(result: Result, *, as_text: bool = False) -> int:
    """Print ``result`` to the right stream and return its exit code.

    Successful results go to stdout; failures go to stderr.
    """
    stream = sys.stdout if result.ok else sys.stderr
    print(render(result, as_text=as_text), file=stream)
    return EXIT_OK if result.ok else EXIT_ERROR


@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    """Take a process-exclusive advisory lock for ``path``.

    The lock is held on a sibling ``<path>.lock`` file (not on ``path``
    itself) so the lock survives the atomic rename that :func:`atomic_write`
    performs on commit. Blocks until the lock is acquired.

    Wrap the entire read-modify-write cycle::

        with file_lock(path):
            text = path.read_text(encoding="utf-8")
            new_text = mutate(text)
            atomic_write(path, new_text)
    """
    lock_path = Path(str(path) + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def atomic_write(path: Path, text: str) -> None:
    """Replace ``path`` with ``text`` via ``tempfile`` + :func:`os.replace`.

    The temp file is created in the same directory as ``path`` so the
    rename is atomic on every POSIX filesystem. On failure the temp file
    is best-effort removed and the original ``path`` is left untouched.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise
