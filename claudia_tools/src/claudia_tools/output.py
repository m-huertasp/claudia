"""The result envelope and error model shared by every ``claudia`` command.

Every command produces a :class:`Result`. It is rendered either as the JSON
envelope ``{"ok", "data", "error"}`` (the default, for the orchestrating
model) or as human-readable text (``--text``). A failed result is written to
stderr and maps to a non-zero exit code.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
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
