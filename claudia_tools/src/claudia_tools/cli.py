"""The ``claudia`` command-line interface.

Every command runs a library call, wraps the outcome in a :class:`Result`, and
emits it as the ``{ok, data, error}`` envelope (JSON by default, ``--text``
for humans). A :class:`ClaudiaError` becomes a failed envelope and a non-zero
exit code; it never reaches the user as a traceback.
"""

from __future__ import annotations

import shlex
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Any

import click

from claudia_tools import (
    __version__,
    config,
    detect,
    env,
    gates,
    phase,
    state,
    templates,
    verification,
)
from claudia_tools.output import ClaudiaError, Result, emit


def _run(ctx: click.Context, fn: Callable[[], Any]) -> None:
    """Run ``fn``, emit its result as an envelope, and exit with its code."""
    try:
        result = Result.success(fn())
    except ClaudiaError as exc:
        result = Result.failure(str(exc))
    except OSError as exc:
        result = Result.failure(f"file error: {exc}")
    ctx.exit(emit(result, as_text=ctx.obj["as_text"]))


def _planning(ctx: click.Context) -> Path:
    """Return the configured ``.planning/`` directory."""
    return Path(ctx.obj["planning_dir"])


def _parse_vars(pairs: tuple[str, ...]) -> dict[str, str]:
    """Parse ``key=value`` strings from repeated ``--var`` options."""
    parsed: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ClaudiaError(f"--var must be key=value, got '{pair}'")
        key, value = pair.split("=", 1)
        parsed[key] = value
    return parsed


def _parse_probes(probes: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Parse ``name='cmd args'`` strings from repeated ``--probe`` options."""
    parsed: dict[str, tuple[str, ...]] = {}
    for probe in probes:
        if "=" not in probe:
            raise ClaudiaError(f"--probe must be name='cmd args', got '{probe}'")
        name, command = probe.split("=", 1)
        argv = tuple(shlex.split(command))
        if not argv:
            raise ClaudiaError(f"--probe '{name}' has no command")
        parsed[name] = argv
    return parsed


def _environment_dict(snapshot: env.Environment) -> dict[str, Any]:
    """Convert an :class:`env.Environment` to a plain dict for JSON output."""
    return {
        "project_type": asdict(snapshot.project_type),
        "tools": [asdict(tool) for tool in snapshot.tools],
        "captured_at": snapshot.captured_at,
    }


@click.group()
@click.option("--text", "as_text", is_flag=True, help="Human-readable output instead of JSON.")
@click.option(
    "--planning-dir",
    default=".planning",
    type=click.Path(file_okay=False, path_type=Path),
    help="Path to the .planning/ directory.",
)
@click.version_option(__version__)
@click.pass_context
def main(ctx: click.Context, as_text: bool, planning_dir: Path) -> None:
    """claudia — deterministic engine for the claudia workflow."""
    ctx.obj = {"as_text": as_text, "planning_dir": planning_dir}


# --- state -----------------------------------------------------------------


@click.group()
def state_cmd() -> None:
    """Read and update STATE.md."""


@state_cmd.command("init")
@click.option("--name", "project_name", default="project", help="Project name in the heading.")
@click.option("--force", is_flag=True, help="Overwrite an existing STATE.md.")
@click.pass_context
def state_init(ctx: click.Context, project_name: str, force: bool) -> None:
    """Write a fresh .planning/STATE.md from the bundled template."""
    _run(ctx, lambda: str(state.init_state(_planning(ctx), project_name, force=force)))


@state_cmd.command("get")
@click.pass_context
def state_get(ctx: click.Context) -> None:
    """Show the STATE.md status fields."""
    _run(ctx, lambda: state.read_status(_planning(ctx) / "STATE.md"))


@state_cmd.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def state_set(ctx: click.Context, key: str, value: str) -> None:
    """Set a STATE.md status field."""
    _run(ctx, lambda: state.set_status_field(_planning(ctx) / "STATE.md", key, value))


@state_cmd.command("tasks")
@click.pass_context
def state_tasks(ctx: click.Context) -> None:
    """List the open tasks."""
    _run(ctx, lambda: [asdict(t) for t in state.read_tasks(_planning(ctx) / "STATE.md")])


@state_cmd.command("task-done")
@click.argument("task_id")
@click.option("--undo", is_flag=True, help="Untick the task instead.")
@click.pass_context
def state_task_done(ctx: click.Context, task_id: str, undo: bool) -> None:
    """Tick (or, with --undo, untick) a task's checkbox."""
    _run(ctx, lambda: asdict(state.set_task_done(_planning(ctx) / "STATE.md", task_id, not undo)))


# --- config ----------------------------------------------------------------


@click.group()
def config_cmd() -> None:
    """Read and update config.json."""


@config_cmd.command("init")
@click.option("--force", is_flag=True, help="Overwrite an existing config.json.")
@click.pass_context
def config_init(ctx: click.Context, force: bool) -> None:
    """Write the bundled default config to .planning/config.json."""
    _run(ctx, lambda: str(config.init_config(_planning(ctx), force=force)))


@config_cmd.command("get")
@click.argument("key", required=False)
@click.pass_context
def config_get(ctx: click.Context, key: str | None) -> None:
    """Show the whole config, or one dotted KEY."""
    path = _planning(ctx) / "config.json"
    _run(ctx, lambda: config.read_config(path) if key is None else config.get_value(path, key))


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set a dotted config KEY to VALUE."""
    _run(ctx, lambda: config.set_value(_planning(ctx) / "config.json", key, value))


# --- phase -----------------------------------------------------------------


@click.group()
def phase_cmd() -> None:
    """Inspect and transition roadmap phases."""


@phase_cmd.command("list")
@click.pass_context
def phase_list(ctx: click.Context) -> None:
    """List every roadmap phase."""
    _run(ctx, lambda: [asdict(p) for p in phase.read_phases(_planning(ctx) / "ROADMAP.md")])


@phase_cmd.command("current")
@click.pass_context
def phase_current(ctx: click.Context) -> None:
    """Show the first incomplete phase."""
    _run(ctx, lambda: asdict(phase.current_phase(_planning(ctx) / "ROADMAP.md")))


@phase_cmd.command("set-status")
@click.argument("number", type=int)
@click.argument("status")
@click.pass_context
def phase_set_status(ctx: click.Context, number: int, status: str) -> None:
    """Set phase NUMBER to STATUS."""
    _run(ctx, lambda: asdict(phase.set_phase_status(_planning(ctx) / "ROADMAP.md", number, status)))


# --- template --------------------------------------------------------------


@click.group()
def template_cmd() -> None:
    """Render workflow templates."""


@template_cmd.command("render")
@click.argument("template_ref")
@click.option("--var", "variables", multiple=True, help="A key=value substitution.")
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    help="Write the rendered text to this path instead of returning it.",
)
@click.option("--force", is_flag=True, help="Overwrite the output path if it exists.")
@click.pass_context
def template_render(
    ctx: click.Context,
    template_ref: str,
    variables: tuple[str, ...],
    output_path: Path | None,
    force: bool,
) -> None:
    """Render TEMPLATE_REF with the given --var substitutions.

    TEMPLATE_REF is either a bundled name (e.g. ``ROADMAP``, ``STATE``) or a
    path to a template file. Bundled names resolve to the matching
    ``<NAME>.md.template`` shipped with claudia.
    """
    parsed = _parse_vars(variables)
    if output_path is None:
        _run(ctx, lambda: templates.render_file(template_ref, parsed))
    else:
        _run(
            ctx,
            lambda: str(
                templates.render_to_file(template_ref, output_path, parsed, force=force)
            ),
        )


# --- gate ------------------------------------------------------------------


@click.group()
def gate_cmd() -> None:
    """Manage review-gate acceptance."""


@gate_cmd.command("accept")
@click.argument("artifact")
@click.pass_context
def gate_accept(ctx: click.Context, artifact: str) -> None:
    """Record ARTIFACT as having cleared its review gate."""

    def _accept() -> str:
        gates.accept(_planning(ctx), artifact)
        return f"{artifact} accepted"

    _run(ctx, _accept)


@gate_cmd.command("revoke")
@click.argument("artifact")
@click.pass_context
def gate_revoke(ctx: click.Context, artifact: str) -> None:
    """Clear any recorded acceptance for ARTIFACT."""

    def _revoke() -> str:
        gates.revoke(_planning(ctx), artifact)
        return f"{artifact} revoked"

    _run(ctx, _revoke)


@gate_cmd.command("check")
@click.argument("artifacts", nargs=-1, required=True)
@click.pass_context
def gate_check(ctx: click.Context, artifacts: tuple[str, ...]) -> None:
    """Fail unless every named ARTIFACT has cleared its review gate."""

    def _check() -> str:
        gates.require_accepted(_planning(ctx), *artifacts)
        return "all review gates cleared"

    _run(ctx, _check)


@gate_cmd.command("status")
@click.pass_context
def gate_status(ctx: click.Context) -> None:
    """Show the review-gate ledger."""
    _run(ctx, lambda: gates.status(_planning(ctx)))


# --- detect ----------------------------------------------------------------


@main.command("detect")
@click.argument(
    "root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
)
@click.pass_context
def detect_cmd(ctx: click.Context, root: Path) -> None:
    """Detect the primary project type of ROOT (default: cwd)."""
    _run(ctx, lambda: asdict(detect.detect_project_type(root)))


# --- env -------------------------------------------------------------------


@click.group()
def env_cmd() -> None:
    """Capture environment reproducibility data."""


@env_cmd.command("capture")
@click.argument(
    "root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    help="Write a rendered ENVIRONMENT.md to this path.",
)
@click.option("--force", is_flag=True, help="Overwrite the output path if it exists.")
@click.option(
    "--probe",
    "probes",
    multiple=True,
    help="Extra probe: name='cmd args'.",
)
@click.option(
    "--name",
    "project_name",
    default=None,
    help="Project name for the artifact (default: ROOT directory name).",
)
@click.pass_context
def env_capture(
    ctx: click.Context,
    root: Path,
    output_path: Path | None,
    force: bool,
    probes: tuple[str, ...],
    project_name: str | None,
) -> None:
    """Capture the environment of ROOT (default: cwd)."""

    def _do() -> Any:
        extras = _parse_probes(probes)
        snapshot = env.capture_environment(root, extra_probes=extras)
        if output_path is None:
            return _environment_dict(snapshot)
        name = project_name or Path(root).resolve().name
        return str(env.write_environment_file(snapshot, name, output_path, force=force))

    _run(ctx, _do)


# --- verify ----------------------------------------------------------------


@click.group()
def verify_cmd() -> None:
    """Manage the human-checklist verification artifact."""


@verify_cmd.command("init")
@click.option("--name", "project_name", default="project", help="Project name in the heading.")
@click.option("--force", is_flag=True, help="Overwrite an existing VERIFICATION.md.")
@click.pass_context
def verify_init(ctx: click.Context, project_name: str, force: bool) -> None:
    """Write a fresh .planning/VERIFICATION.md from the bundled template."""
    _run(
        ctx,
        lambda: str(verification.init_verification(_planning(ctx), project_name, force=force)),
    )


@verify_cmd.command("add")
@click.argument("description")
@click.pass_context
def verify_add(ctx: click.Context, description: str) -> None:
    """Append DESCRIPTION as a new checklist item."""
    _run(ctx, lambda: asdict(verification.add_item(_planning(ctx), description)))


@verify_cmd.command("confirm")
@click.argument("item_id")
@click.pass_context
def verify_confirm(ctx: click.Context, item_id: str) -> None:
    """Tick the checkbox of ITEM_ID (e.g. V1)."""
    _run(ctx, lambda: asdict(verification.confirm_item(_planning(ctx), item_id)))


@verify_cmd.command("list")
@click.pass_context
def verify_list(ctx: click.Context) -> None:
    """List every checklist item."""
    _run(ctx, lambda: [asdict(item) for item in verification.list_items(_planning(ctx))])


@verify_cmd.command("ready")
@click.pass_context
def verify_ready(ctx: click.Context) -> None:
    """Exit 0 if every checklist item is confirmed; non-zero otherwise."""

    def _check() -> str:
        verification.require_ready(_planning(ctx))
        return "verification checklist clear"

    _run(ctx, _check)


main.add_command(state_cmd, "state")
main.add_command(config_cmd, "config")
main.add_command(phase_cmd, "phase")
main.add_command(template_cmd, "template")
main.add_command(gate_cmd, "gate")
main.add_command(env_cmd, "env")
main.add_command(verify_cmd, "verify")


if __name__ == "__main__":  # pragma: no cover
    main()
