"""Tests for the marked-region engine."""

from __future__ import annotations

import pytest

from claudia_tools.markers import (
    MarkerError,
    has_region,
    read_region,
    region_names,
    replace_region,
)

BLOCK = "intro\n<!-- claudia:tasks -->\n- [ ] T1\n<!-- /claudia:tasks -->\noutro\n"
INLINE = "**Status:** <!-- claudia:status-1 -->not started<!-- /claudia:status-1 -->\n"
MULTI = (
    "<!-- claudia:a -->one<!-- /claudia:a -->\n"
    "<!-- claudia:b -->two<!-- /claudia:b -->\n"
)


def test_read_block_region() -> None:
    assert read_region(BLOCK, "tasks") == "\n- [ ] T1\n"


def test_read_inline_region() -> None:
    assert read_region(INLINE, "status-1") == "not started"


def test_replace_region_preserves_markers_and_prose() -> None:
    updated = replace_region(BLOCK, "tasks", "\n- [x] T1\n")

    assert "- [x] T1" in updated
    assert "intro" in updated and "outro" in updated
    assert updated.count("<!-- claudia:tasks -->") == 1


def test_replace_region_round_trips() -> None:
    updated = replace_region(INLINE, "status-1", "complete")

    assert read_region(updated, "status-1") == "complete"


def test_region_names_in_document_order() -> None:
    assert region_names(MULTI) == ["a", "b"]


def test_read_each_of_multiple_regions() -> None:
    assert read_region(MULTI, "a") == "one"
    assert read_region(MULTI, "b") == "two"


def test_missing_region_raises() -> None:
    with pytest.raises(MarkerError, match="no opening marker"):
        read_region(BLOCK, "absent")


def test_unclosed_region_raises() -> None:
    with pytest.raises(MarkerError, match="no closing marker"):
        read_region("<!-- claudia:x -->dangling", "x")


def test_has_region() -> None:
    assert has_region(BLOCK, "tasks") is True
    assert has_region(BLOCK, "absent") is False
