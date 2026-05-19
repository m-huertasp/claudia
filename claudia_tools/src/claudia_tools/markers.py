"""Read and replace HTML-comment-delimited regions inside Markdown.

The claudia workflow stores machine-owned data in *marked regions* so the CLI
can update it without disturbing the human-written prose around it. A region
is delimited by a matching pair of HTML comments::

    <!-- claudia:tasks -->
    ...machine-owned content...
    <!-- /claudia:tasks -->

Markers may sit on their own lines (block regions) or inline within a line.
"""

from __future__ import annotations

import re

from claudia_tools.output import ClaudiaError

_NAME = r"[A-Za-z0-9_-]+"
_OPEN_ANY = re.compile(rf"<!--\s*claudia:({_NAME})\s*-->")


class MarkerError(ClaudiaError):
    """Raised when a marked region is missing or malformed."""


def _marker_pair(name: str) -> tuple[re.Pattern[str], re.Pattern[str]]:
    """Return the compiled open/close marker patterns for ``name``."""
    escaped = re.escape(name)
    return (
        re.compile(rf"<!--\s*claudia:{escaped}\s*-->"),
        re.compile(rf"<!--\s*/claudia:{escaped}\s*-->"),
    )


def _region_span(text: str, name: str) -> tuple[int, int]:
    """Return the ``(start, end)`` offsets of the content inside region ``name``.

    Raises
    ------
    MarkerError
        If the open or close marker is missing.
    """
    open_re, close_re = _marker_pair(name)
    open_match = open_re.search(text)
    if open_match is None:
        raise MarkerError(f"no opening marker for region '{name}'")
    close_match = close_re.search(text, open_match.end())
    if close_match is None:
        raise MarkerError(f"no closing marker for region '{name}'")
    return open_match.end(), close_match.start()


def region_names(text: str) -> list[str]:
    """Return the names of every opened region, in document order."""
    return [match.group(1) for match in _OPEN_ANY.finditer(text)]


def has_region(text: str, name: str) -> bool:
    """Return whether ``text`` contains a complete region named ``name``."""
    try:
        _region_span(text, name)
    except MarkerError:
        return False
    return True


def read_region(text: str, name: str) -> str:
    """Return the content between the markers of region ``name``."""
    start, end = _region_span(text, name)
    return text[start:end]


def replace_region(text: str, name: str, new_content: str) -> str:
    """Return ``text`` with the content of region ``name`` replaced.

    The markers themselves are preserved; only the content between them
    changes.
    """
    start, end = _region_span(text, name)
    return text[:start] + new_content + text[end:]
