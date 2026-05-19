"""Shared pytest fixtures for the claudia-tools suite."""

from __future__ import annotations

from pathlib import Path

import pytest

STATE_MD = """# State — demo

<!-- claudia:status -->
- current_phase: 1
- last_command: /claudia-plan
- next_step: /claudia-execute
- updated: 2026-05-19
<!-- /claudia:status -->

## Open tasks

<!-- claudia:tasks -->
- [ ] T1 — Package scaffold
- [x] T2 — Output envelope
<!-- /claudia:tasks -->

## Notes for the next session

Human-owned prose the CLI must never touch.
"""

ROADMAP_MD = """# Roadmap — demo

## Phase 1 — Foundation
**Goal:** Lay the base.
**Status:** <!-- claudia:status-1 -->complete<!-- /claudia:status-1 -->

## Phase 2 — Build
**Goal:** Build on it.
**Status:** <!-- claudia:status-2 -->not started<!-- /claudia:status-2 -->
"""

CONFIG_JSON = """{
  "mode": "interactive",
  "model_profile": "balanced",
  "agents": { "researcher": true, "planner": true, "verifier": true },
  "execution": { "parallel": false }
}
"""


@pytest.fixture
def planning_dir(tmp_path: Path) -> Path:
    """Return a temporary ``.planning/`` directory with sample artifacts."""
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "STATE.md").write_text(STATE_MD, encoding="utf-8")
    (planning / "ROADMAP.md").write_text(ROADMAP_MD, encoding="utf-8")
    (planning / "config.json").write_text(CONFIG_JSON, encoding="utf-8")
    return planning
