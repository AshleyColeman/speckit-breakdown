"""
Speckit CLI application entrypoint.
"""

from __future__ import annotations

import typer

from src.cli.commands.db_prepare import register as register_db_prepare
from src.cli.commands.validate import register as register_validate
from src.cli.commands.init import register as register_init
from src.cli.commands.migrate import register as register_migrate
from src.cli.commands.doctor import register as register_doctor
from src.cli.commands.doctor import register as register_doctor
from src.cli.commands.breakdown import register as register_breakdown
from src.cli.commands.tasks import register as register_tasks
from src.cli.commands.parallelize import register as register_parallelize
from src.cli.commands.specify import register as register_specify
from src.cli.commands.plan import register as register_plan
from src.cli.commands.context import register as register_context

app = typer.Typer(help="Speckit developer tooling")
register_db_prepare(app)
register_validate(app)
register_init(app)
register_migrate(app)
register_doctor(app)
register_breakdown(app)
register_tasks(app)
register_parallelize(app)
register_specify(app)
register_plan(app)
register_context(app)

__all__ = ["app"]
