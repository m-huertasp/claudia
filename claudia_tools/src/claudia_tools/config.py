"""Read, validate, and update ``.planning/config.json``.

Configuration is addressed with dotted keys (``agents.planner``,
``execution.parallel``). Every key is checked against a fixed schema — the CLI
never invents settings, and invalid values are rejected rather than written.
"""

from __future__ import annotations

import copy
import json
from importlib import resources
from pathlib import Path
from typing import Any

from claudia_tools.output import ClaudiaError

_ENUMS: dict[str, set[str]] = {
    "mode": {"interactive", "yolo"},
    "model_profile": {"quality", "balanced", "budget"},
}
_BOOL_KEYS = frozenset(
    {"agents.researcher", "agents.planner", "agents.verifier", "execution.parallel"}
)
_ALLOWED = frozenset(_ENUMS) | _BOOL_KEYS


def init_config(planning_dir: Path, force: bool = False) -> Path:
    """Write the bundled default config to ``planning_dir/config.json``.

    Returns the path written.

    Raises
    ------
    ClaudiaError
        If the target already exists and ``force`` is False.
    """
    target = Path(planning_dir) / "config.json"
    if target.exists() and not force:
        raise ClaudiaError(
            f"config already exists at {target}; pass --force to overwrite"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    default = resources.files("claudia_tools.data").joinpath("config-default.json")
    target.write_text(default.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def read_config(path: Path) -> dict[str, Any]:
    """Return the parsed ``config.json``.

    Raises
    ------
    ClaudiaError
        If the file is missing or not valid JSON.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ClaudiaError(f"no config at {path}") from exc
    try:
        parsed: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ClaudiaError(f"invalid JSON in {path}: {exc}") from exc
    return parsed


def get_value(path: Path, key: str) -> Any:
    """Return the value of dotted ``key`` from the config.

    Raises
    ------
    ClaudiaError
        If ``key`` is not in the schema or is not set in the file.
    """
    if key not in _ALLOWED:
        raise ClaudiaError(f"unknown config key '{key}'")
    node: Any = read_config(path)
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ClaudiaError(f"config key '{key}' is not set")
        node = node[part]
    return node


def _coerce(key: str, value: Any) -> Any:
    """Validate and coerce ``value`` for ``key`` against the schema."""
    if key in _BOOL_KEYS:
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"true", "false"}:
            return text == "true"
        raise ClaudiaError(f"'{key}' must be true or false, got '{value}'")
    if key not in _ENUMS:
        raise ClaudiaError(f"no coercion rule for config key '{key}'")
    allowed = _ENUMS[key]
    if value not in allowed:
        raise ClaudiaError(f"'{key}' must be one of {sorted(allowed)}, got '{value}'")
    return value


def set_value(path: Path, key: str, value: Any) -> dict[str, Any]:
    """Validate ``value``, set dotted ``key``, write the file, return the config.

    Raises
    ------
    ClaudiaError
        If ``key`` is unknown or ``value`` is invalid for it.
    """
    if key not in _ALLOWED:
        raise ClaudiaError(f"unknown config key '{key}'")
    coerced = _coerce(key, value)
    config = copy.deepcopy(read_config(path))
    parts = key.split(".")
    node = config
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = coerced
    Path(path).write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return config
