"""Read and update ``STATE.md`` — the workflow's resume point.

``STATE.md`` holds two machine-owned marked regions: ``status`` (a list of
``key: value`` lines) and ``tasks`` (a Markdown checkbox list). Everything
else in the file is human-owned prose this module never touches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from claudia_tools.markers import read_region, replace_region
from claudia_tools.output import ClaudiaError
from claudia_tools.templates import render_to_file

_STATUS_REGION = "status"
_TASKS_REGION = "tasks"
_FILE = "STATE.md"

_STATUS_LINE = re.compile(r"^- (?P<key>[A-Za-z0-9_]+):[ \t]*(?P<value>.*)$", re.MULTILINE)
_TASK_LINE = re.compile(
    r"^(?P<indent> *)- \[(?P<mark>[ xX])\] (?P<id>\S+) — (?P<title>.*)$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Task:
    """A single planned task.

    Attributes
    ----------
    id
        The task identifier, e.g. ``"T1"``.
    title
        The task description.
    done
        Whether the task's checkbox is ticked.
    """

    id: str
    title: str
    done: bool


def _read(path: Path) -> str:
    """Return the text of ``path``.

    Raises
    ------
    ClaudiaError
        If the file does not exist, with a hint at the right next command.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ClaudiaError(
            f"no STATE.md at {path}; run /claudia-plan first to initialise it"
        ) from exc


def _write(path: Path, text: str) -> None:
    """Write ``text`` to ``path``."""
    Path(path).write_text(text, encoding="utf-8")


def init_state(
    planning_dir: Path,
    name: str = "project",
    force: bool = False,
    current_phase: str = "1",
    last_command: str = "",
    next_step: str = "",
) -> Path:
    """Render the bundled STATE.md template into ``planning_dir``.

    The ``updated`` field is set to today (ISO date). The status fields can
    be overridden via the keyword arguments; the task region stays at its
    template default of ``- (none yet — run /claudia-plan)``.

    Raises
    ------
    ClaudiaError
        If ``planning_dir/STATE.md`` already exists and ``force`` is False.
    """
    target = Path(planning_dir) / _FILE
    return render_to_file(
        "STATE",
        target,
        {
            "name": name,
            "current_phase": current_phase,
            "last_command": last_command,
            "next_step": next_step,
            "updated": date.today().isoformat(),
        },
        force=force,
    )


def read_status(path: Path) -> dict[str, str]:
    """Return the ``status`` region of ``STATE.md`` as an ordered dict."""
    region = read_region(_read(path), _STATUS_REGION)
    return {m["key"]: m["value"].strip() for m in _STATUS_LINE.finditer(region)}


def set_status_field(path: Path, key: str, value: str) -> dict[str, str]:
    """Set one field in the ``status`` region and return the updated status.

    If ``STATE.md`` does not exist yet, it is auto-created from the bundled
    template with default values; the caller's ``key=value`` is then
    applied. This keeps ``state set`` callable from early workflow steps
    (e.g. ``/claudia-understand``, ``/claudia-brief``) without a separate
    ``state init`` call.

    Raises
    ------
    ClaudiaError
        If ``key`` is not a recognised status field.
    """
    path = Path(path)
    if not path.exists():
        init_state(path.parent)
    text = _read(path)
    region = read_region(text, _STATUS_REGION)
    status = {m["key"]: m["value"].strip() for m in _STATUS_LINE.finditer(region)}
    if key not in status:
        raise ClaudiaError(f"unknown status field '{key}'")
    status[key] = str(value)
    body = "\n" + "\n".join(f"- {k}: {v}" for k, v in status.items()) + "\n"
    _write(path, replace_region(text, _STATUS_REGION, body))
    return status


def read_tasks(path: Path) -> list[Task]:
    """Return the task list from the ``tasks`` region of ``STATE.md``."""
    region = read_region(_read(path), _TASKS_REGION)
    return [
        Task(id=m["id"], title=m["title"].strip(), done=m["mark"] in "xX")
        for m in _TASK_LINE.finditer(region)
    ]


def set_task_done(path: Path, task_id: str, done: bool = True) -> Task:
    """Tick or untick the checkbox of task ``task_id`` and return it.

    Raises
    ------
    ClaudiaError
        If no task with that id exists in ``STATE.md``.
    """
    text = _read(path)
    region = read_region(text, _TASKS_REGION)
    mark = "x" if done else " "
    matched: list[re.Match[str]] = []

    def _replace(match: re.Match[str]) -> str:
        if match["id"] != task_id:
            return match.group(0)
        matched.append(match)
        return f"{match['indent']}- [{mark}] {match['id']} — {match['title']}"

    new_region = _TASK_LINE.sub(_replace, region)
    if not matched:
        raise ClaudiaError(f"no task '{task_id}' in {path}")
    _write(path, replace_region(text, _TASKS_REGION, new_region))
    return Task(id=task_id, title=matched[0]["title"].strip(), done=done)


def _format_tasks_region(tasks: list[Task]) -> str:
    """Render a tasks list back into the body of the ``tasks`` marked region."""
    if not tasks:
        return "\n- (none yet — run /claudia-plan)\n"
    lines = [f"- [{'x' if t.done else ' '}] {t.id} — {t.title}" for t in tasks]
    return "\n" + "\n".join(lines) + "\n"


def _next_task_id(tasks: list[Task]) -> str:
    """Return ``T<max+1>`` using monotonic numbering — no gap reuse."""
    highest = 0
    for task in tasks:
        match = re.fullmatch(r"T(\d+)", task.id)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"T{highest + 1}"


def add_task(path: Path, title: str) -> Task:
    """Append a new task to the ``tasks`` region and return it.

    The new task's id is the next monotonic ``T<N>`` after the highest
    existing numeric id (gaps from removed tasks are not reused, so ids
    stay stable across edits). Auto-creates ``STATE.md`` from the bundled
    template if missing.

    Raises
    ------
    ClaudiaError
        If ``title`` is empty after stripping whitespace.
    """
    title = title.strip()
    if not title:
        raise ClaudiaError("task title must not be empty")
    path = Path(path)
    if not path.exists():
        init_state(path.parent)
    text = _read(path)
    tasks = read_tasks(path)
    task = Task(id=_next_task_id(tasks), title=title, done=False)
    tasks.append(task)
    _write(path, replace_region(text, _TASKS_REGION, _format_tasks_region(tasks)))
    return task


def remove_task(path: Path, task_id: str) -> Task:
    """Remove ``task_id`` from the ``tasks`` region and return the removed task.

    Raises
    ------
    ClaudiaError
        If no task with that id exists.
    """
    text = _read(path)
    tasks = read_tasks(path)
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        raise ClaudiaError(f"no task '{task_id}' in {path}")
    removed = next(t for t in tasks if t.id == task_id)
    _write(path, replace_region(text, _TASKS_REGION, _format_tasks_region(remaining)))
    return removed
