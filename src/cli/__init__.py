"""
Speckit CLI application entrypoint.
"""

from __future__ import annotations

import typer

from src.cli.commands.db_prepare import register as register_db_prepare

app = typer.Typer(help="Speckit developer tooling")
register_db_prepare(app)

__all__ = ["app"]
