"""
CLI bindings for the `/speckit.db.prepare` command.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer

from src.lib.config_loader import BootstrapConfig, ConfigLoader
from src.lib.error_reporter import format_validation_report
from src.lib.logging import LogFormat, configure_logging
from src.services.bootstrap_options import BootstrapOptions
from src.services.bootstrap_orchestrator import BootstrapOrchestrator
from src.services.doc_discovery import DocumentationDiscoveryService
from src.services.data_store_gateway import DataStoreGateway
from src.services.upsert_service import UpsertService
from src.services.task_run_service import TaskRunService
from src.services.ai_job_service import AIJobService
from src.services.validation_pipeline import ValidationException

logger = logging.getLogger("speckit.db_prepare")


def register(app: typer.Typer) -> None:
    """Register the db_prepare command with the root Typer app."""

    @app.command("speckit.db.prepare")
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
        log_format: LogFormat = typer.Option(
            "human",
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

        NOTE: Implementation scaffolding only (Phase 1). Later phases will
        populate the orchestration flow.
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
        try:
            _run_bootstrap(config, options)
        except ValidationException as exc:
            logger.error("Bootstrap validation failed.")
            typer.echo(format_validation_report(exc.result))
            raise typer.Exit(code=1) from exc


def _run_bootstrap(config: BootstrapConfig, options: BootstrapOptions) -> None:
    """
    Execute the bootstrap pipeline using the configured orchestrator.
    """

    logger.info("Bootstrapping Speckit documentation", extra={"docs": str(config.docs_root)})
    logger.info("Storage target", extra={"storage": str(config.storage_path)})

    gateway = DataStoreGateway(config.storage_path)
    orchestrator = BootstrapOrchestrator(
        discovery_service=DocumentationDiscoveryService(config.docs_root),
        upsert_service=UpsertService(gateway),
        task_run_service=TaskRunService(),
        ai_job_service=AIJobService(),
        gateway=gateway,
    )

    summary = orchestrator.run(config=config, options=options)

    logger.info(
        "Bootstrap completed",
        extra={
            "projects": summary.project_count,
            "features": summary.feature_count,
            "specs": summary.spec_count,
            "tasks": summary.task_count,
            "dependencies": summary.dependency_count,
            "task_runs": summary.task_run_count,
            "ai_jobs": summary.ai_job_count,
        },
    )
