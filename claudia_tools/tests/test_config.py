"""Tests for the config.json module."""

from __future__ import annotations

from pathlib import Path

import pytest

from claudia_tools.config import get_value, init_config, read_config, set_value
from claudia_tools.output import ClaudiaError


def test_read_config(planning_dir: Path) -> None:
    config = read_config(planning_dir / "config.json")

    assert config["mode"] == "pair"


def test_read_missing_config_raises(tmp_path: Path) -> None:
    with pytest.raises(ClaudiaError, match="no config"):
        read_config(tmp_path / "config.json")


def test_get_value_scalar_and_nested(planning_dir: Path) -> None:
    config = planning_dir / "config.json"

    assert get_value(config, "mode") == "pair"
    assert get_value(config, "agents.planner") is True


def test_get_unknown_key_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="unknown config key"):
        get_value(planning_dir / "config.json", "agents.bogus")


def test_set_enum_value_persists(planning_dir: Path) -> None:
    config = planning_dir / "config.json"

    set_value(config, "mode", "yolo")

    assert get_value(config, "mode") == "yolo"


def test_set_bool_value_coerces_string(planning_dir: Path) -> None:
    config = planning_dir / "config.json"

    set_value(config, "execution.parallel", "true")

    assert get_value(config, "execution.parallel") is True


def test_set_unknown_key_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="unknown config key"):
        set_value(planning_dir / "config.json", "speed", "fast")


def test_set_invalid_enum_value_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="must be one of"):
        set_value(planning_dir / "config.json", "model_profile", "turbo")


def test_set_mode_interactive_is_rejected(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="must be one of"):
        set_value(planning_dir / "config.json", "mode", "interactive")


def test_set_invalid_bool_value_raises(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="must be true or false"):
        set_value(planning_dir / "config.json", "execution.parallel", "maybe")


def test_set_value_does_not_mutate_a_prior_read(planning_dir: Path) -> None:
    config = planning_dir / "config.json"
    before = read_config(config)

    set_value(config, "mode", "yolo")

    assert before["mode"] == "pair"


def test_init_config_creates_default(tmp_path: Path) -> None:
    target = init_config(tmp_path)

    assert target == tmp_path / "config.json"
    assert read_config(target)["mode"] == "pair"


def test_init_config_refuses_when_exists(planning_dir: Path) -> None:
    with pytest.raises(ClaudiaError, match="already exists"):
        init_config(planning_dir)


def test_init_config_force_overwrites(planning_dir: Path) -> None:
    config_path = planning_dir / "config.json"
    set_value(config_path, "mode", "yolo")

    init_config(planning_dir, force=True)

    assert read_config(config_path)["mode"] == "pair"
