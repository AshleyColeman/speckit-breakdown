"""
CLI bindings for the `/speckit.db.prepare` command.
"""

from __future__ import annotations

import errno
import hashlib
import logging
from pathlib import Path
from typing import Optional

import typer

from src.lib.error_reporter import ErrorReporter
from src.lib.config_loader import BootstrapConfig, ConfigLoader
from src.lib.locking import LockConfig, queue_lock
from src.lib.logging import LogFormat, configure_logging
from src.lib.metrics import emit_bootstrap_summary
from src.lib.resource_guard import ResourceGuard, ResourceLimits
from src.services.bootstrap_options import BootstrapOptions
from src.services.bootstrap_orchestrator import BootstrapOrchestrator
from src.services.data_store_gateway import DataStoreGateway
from src.services.rollback_manager import RollbackManager

logger = logging.getLogger("speckit.db_prepare")


def _lock_name_for_run(config: BootstrapConfig, target: str) -> str:
    digest = hashlib.sha256(f"{config.docs_root}::{target}".encode("utf-8")).hexdigest()[:12]
    return f"speckit_db_prepare_{digest}"


def register(app: typer.Typer) -> None:
    """Register the db_prepare command with the root Typer app."""

    @app.command("db.prepare")
    def db_prepare_command(  # noqa: D401
        docs_path: Optional[Path] = typer.Option(
            None,
            "--docs-path",
            help="Path to the documentation root (default: specs/).",
        ),
        storage_path: Optional[Path] = typer.Option(
            None,
            "--storage-path",
            help="Path to the SQLite database file (default: .speckit/db.sqlite).",
        ),
        db_url: Optional[str] = typer.Option(
            None,
            "--db-url",
            help="PostgreSQL connection string (overrides --storage-path).",
        ),
        enable_experimental_postgres: bool = typer.Option(
            False,
            "--enable-experimental-postgres",
            help="Enable experimental PostgreSQL backend (disabled by default).",
        ),
        log_format: LogFormat = typer.Option(
            LogFormat.HUMAN,
            "--log-format",
            help="Logging output format (human|json).",
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Increase log verbosity to DEBUG.",
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Validate documentation without writing to storage.",
        ),
        force: bool = typer.Option(
            False,
            "--force",
            help="Force overwrite mismatched entities during persistence.",
        ),
        project: Optional[str] = typer.Option(
            None,
            "--project",
            "-p",
            help="Limit processing to a single project identifier.",
        ),
        skip_task_runs: bool = typer.Option(
            False,
            "--skip-task-runs",
            help="Skip creation of task-run entities.",
        ),
        skip_ai_jobs: bool = typer.Option(
            False,
            "--skip-ai-jobs",
            help="Skip creation of AI job entities.",
        ),
    ) -> None:
        """
        Bootstrap Speckit documentation into system data storage.

        Parses projects, features, specs, and tasks (including nested structures).
        Verifies dependencies, calculates topological step orders, and persists
        data to the configured SQLite or PostgreSQL database.
        """

        configure_logging(level=logging.DEBUG if verbose else logging.INFO, fmt=log_format)
        config = ConfigLoader(docs_root=docs_path, storage_path=storage_path).materialize()
        options = BootstrapOptions(
            dry_run=dry_run,
            force=force,
            project=project,
            skip_task_runs=skip_task_runs,
            skip_ai_jobs=skip_ai_jobs,
        )
        _run_bootstrap(config, options, db_url, enable_experimental_postgres)


def _run_bootstrap(
    config: BootstrapConfig,
    options: BootstrapOptions,
    db_url: Optional[str] = None,
    enable_experimental_postgres: bool = False,
) -> None:
    """
    Execute the bootstrap pipeline using the configured orchestrator.
    """

    logger.info("Bootstrapping Speckit documentation", extra={"docs": str(config.docs_root)})
    gateway_target = db_url if db_url else config.storage_path
    lock_target = db_url if db_url else str(config.storage_path)

    if db_url:
        logger.info("Storage target", extra={"db_url": db_url})
    else:
        logger.info("Storage target", extra={"storage": str(config.storage_path)})

    if isinstance(db_url, str) and db_url.startswith("postgresql://") and not enable_experimental_postgres:
        typer.echo(
            "PostgreSQL support is experimental and disabled by default. "
            "Re-run with --enable-experimental-postgres. "
            "See docs/cli/db_prepare.md."
        )
        raise typer.Exit(code=1)

    lock_config = LockConfig(lock_dir=config.storage_path.parent / ".locks")
    queue_name = _lock_name_for_run(config, lock_target)

    try:
        with queue_lock(lock_config, queue_name, non_blocking=True):
            ResourceGuard(ResourceLimits(max_memory_mb=2048, max_cpu_percent=95, max_file_mb=50)).enforce_all()

            rollback_manager = RollbackManager()
            created_sqlite_db = False
            if not db_url and not config.storage_path.exists():
                created_sqlite_db = True
                rollback_manager.add_action(
                    "Remove newly created SQLite database file",
                    lambda: config.storage_path.unlink(missing_ok=True),
                )

            try:
                gateway = DataStoreGateway(gateway_target, enable_experimental_postgres=enable_experimental_postgres)
                orchestrator = BootstrapOrchestrator(config.docs_root, gateway)

                summary = orchestrator.run_bootstrap(options)
                emit_bootstrap_summary(summary)
            except Exception:
                rollback_manager.rollback()
                raise

            if not summary.success:
                if created_sqlite_db:
                    rollback_manager.rollback()
            else:
                rollback_manager.actions.clear()

    except BlockingIOError:
        typer.echo("Another speckit.db.prepare run is already in progress for this target. Try again later.")
        raise typer.Exit(code=1)
    except OSError as exc:
        if getattr(exc, "errno", None) in {errno.EWOULDBLOCK, errno.EAGAIN}:
            typer.echo("Another speckit.db.prepare run is already in progress for this target. Try again later.")
            raise typer.Exit(code=1)
        raise

    if summary.validation_result:
        report = ErrorReporter.format_report(summary.validation_result)
        typer.echo(report)

    if not summary.success:
        typer.echo("Bootstrap failed.")
        if summary.error_message:
            typer.echo(summary.error_message)
        raise typer.Exit(code=1)

    typer.echo("Bootstrap completed successfully.")
    typer.echo(
        f"Projects: {summary.project_count}, Features: {summary.feature_count}, "
        f"Specs: {summary.spec_count}, Tasks: {summary.task_count}, "
        f"Dependencies: {summary.dependency_count}, "
        f"Task Runs: {summary.task_run_count}, AI Jobs: {summary.ai_job_count}"
    )
