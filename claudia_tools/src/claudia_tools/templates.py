"""Render workflow templates with variable substitution.

Templates use a ``{{ name }}`` placeholder syntax (surrounding whitespace
optional). Rendering is strict: if a placeholder has no supplied value, the
render fails rather than emitting an empty or half-filled artifact.

Templates may be referenced by **bundled name** (e.g. ``ROADMAP``) or by
**filesystem path** (e.g. ``./my-template.md``, ``/abs/path.md``). A bare
name with no path separator and no dot resolves to the matching
``<NAME>.md.template`` inside the ``claudia_tools.data`` package; anything
else is treated as a literal path on disk.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from importlib import resources
from pathlib import Path

from claudia_tools.output import ClaudiaError

_PLACEHOLDER = re.compile(r"\{\{\s*(?P<name>[A-Za-z0-9_]+)\s*\}\}")

_BUNDLED_PACKAGE = "claudia_tools.data"
_BUNDLED_SUFFIX = ".md.template"


def template_variables(text: str) -> set[str]:
    """Return the set of placeholder names used in ``text``."""
    return {match["name"] for match in _PLACEHOLDER.finditer(text)}


def render(template_text: str, variables: Mapping[str, object]) -> str:
    """Return ``template_text`` with every placeholder substituted.

    Raises
    ------
    ClaudiaError
        If the template uses a placeholder absent from ``variables``.
    """
    missing = sorted(template_variables(template_text) - set(variables))
    if missing:
        raise ClaudiaError(f"missing template variable(s): {', '.join(missing)}")
    return _PLACEHOLDER.sub(lambda match: str(variables[match["name"]]), template_text)


def bundled_template_names() -> list[str]:
    """Return the sorted list of bundled template names (e.g. ``["CONTEXT", ...]``)."""
    return sorted(
        entry.name.removesuffix(_BUNDLED_SUFFIX)
        for entry in resources.files(_BUNDLED_PACKAGE).iterdir()
        if entry.is_file() and entry.name.endswith(_BUNDLED_SUFFIX)
    )


def _is_bare_name(template_ref: str | Path) -> bool:
    """A bare bundled-name has no separator and no dot."""
    s = str(template_ref)
    return bool(s) and "/" not in s and "\\" not in s and "." not in s


@contextmanager
def _resolve(template_ref: str | Path) -> Iterator[Path]:
    """Yield a real filesystem ``Path`` for either a bundled name or a path."""
    if _is_bare_name(template_ref):
        resource = resources.files(_BUNDLED_PACKAGE).joinpath(
            f"{template_ref}{_BUNDLED_SUFFIX}"
        )
        if resource.is_file():
            with resources.as_file(resource) as path:
                yield Path(path)
                return
    yield Path(template_ref)


def render_file(template_ref: str | Path, variables: Mapping[str, object]) -> str:
    """Read the template at ``template_ref`` and return it rendered.

    ``template_ref`` may be a bundled name (e.g. ``ROADMAP``) or a filesystem
    path. The error message preserves the caller-supplied reference.

    Raises
    ------
    ClaudiaError
        If the template cannot be located, or a variable is missing.
    """
    with _resolve(template_ref) as path:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            hint = (
                f"; bundled names: {', '.join(bundled_template_names())}"
                if _is_bare_name(template_ref)
                else ""
            )
            raise ClaudiaError(f"no template at {template_ref}{hint}") from exc
    return render(text, variables)


def render_to_file(
    template_ref: str | Path,
    target_path: Path,
    variables: Mapping[str, object],
    force: bool = False,
) -> Path:
    """Render ``template_ref`` and write the result to ``target_path``.

    Returns the path written.

    Raises
    ------
    ClaudiaError
        If the target already exists and ``force`` is False, if the template
        cannot be located, or if a variable is missing.
    """
    target = Path(target_path)
    if target.exists() and not force:
        raise ClaudiaError(
            f"output already exists at {target}; pass --force to overwrite"
        )
    rendered = render_file(template_ref, variables)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    return target
