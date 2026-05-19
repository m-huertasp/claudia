"""Read and update ``STATE.md`` — the workflow's resume point.

``STATE.md`` holds two machine-owned marked regions: ``status`` (a list of
``key: value`` lines) and ``tasks`` (a Markdown checkbox list). Everything
else in the file is human-owned prose this module never touches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from claudia_tools.markers import read_region, replace_region
from claudia_tools.output import ClaudiaError

_STATUS_REGION = "status"
_TASKS_REGION = "tasks"

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
    """Return the text of ``path``."""
    return Path(path).read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    """Write ``text`` to ``path``."""
    Path(path).write_text(text, encoding="utf-8")


def read_status(path: Path) -> dict[str, str]:
    """Return the ``status`` region of ``STATE.md`` as an ordered dict."""
    region = read_region(_read(path), _STATUS_REGION)
    return {m["key"]: m["value"].strip() for m in _STATUS_LINE.finditer(region)}


def set_status_field(path: Path, key: str, value: str) -> dict[str, str]:
    """Set one field in the ``status`` region and return the updated status.

    Raises
    ------
    ClaudiaError
        If ``key`` is not already a recognised status field.
    """
    status = read_status(path)
    if key not in status:
        raise ClaudiaError(f"unknown status field '{key}'")
    status[key] = str(value)
    body = "\n" + "\n".join(f"- {k}: {v}" for k, v in status.items()) + "\n"
    _write(path, replace_region(_read(path), _STATUS_REGION, body))
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
