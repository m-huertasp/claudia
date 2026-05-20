"""Render workflow templates with variable substitution.

Templates use a ``{{ name }}`` placeholder syntax (surrounding whitespace
optional). Rendering is strict: if a placeholder has no supplied value, the
render fails rather than emitting an empty or half-filled artifact.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

from claudia_tools.output import ClaudiaError

_PLACEHOLDER = re.compile(r"\{\{\s*(?P<name>[A-Za-z0-9_]+)\s*\}\}")


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


def render_file(template_path: Path, variables: Mapping[str, object]) -> str:
    """Read the template at ``template_path`` and return it rendered.

    Raises
    ------
    ClaudiaError
        If the template file does not exist or a variable is missing.
    """
    try:
        text = Path(template_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ClaudiaError(f"no template at {template_path}") from exc
    return render(text, variables)


def render_to_file(
    template_path: Path,
    target_path: Path,
    variables: Mapping[str, object],
    force: bool = False,
) -> Path:
    """Render ``template_path`` and write the result to ``target_path``.

    Returns the path written.

    Raises
    ------
    ClaudiaError
        If the target already exists and ``force`` is False, if the template
        does not exist, or if a variable is missing.
    """
    target = Path(target_path)
    if target.exists() and not force:
        raise ClaudiaError(
            f"output already exists at {target}; pass --force to overwrite"
        )
    rendered = render_file(template_path, variables)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    return target
