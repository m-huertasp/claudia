"""The ``claudia`` command-line interface.

Wired fully in task T9. This module starts as the bare command group so the
``claudia`` console script and ``claudia --help`` resolve from task T1 on.
"""

from __future__ import annotations

import click

from claudia_tools import __version__


@click.group()
@click.version_option(__version__)
def main() -> None:
    """claudia — deterministic engine for the claudia workflow."""


if __name__ == "__main__":  # pragma: no cover
    main()
