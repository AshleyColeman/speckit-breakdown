"""
Integration tests for the happy-path bootstrap flow (US1).
"""

from __future__ import annotations

from unittest import mock

import pytest

from src.lib.config_loader import BootstrapConfig
from src.services.bootstrap_options import BootstrapOptions
from src.services.bootstrap_orchestrator import BootstrapOrchestrator
from src.services.data_store_gateway import DataStoreGateway
from src.services.doc_discovery import DocumentationDiscoveryService
from src.services.task_run_service import TaskRunService
from src.services.ai_job_service import AIJobService
from src.services.upsert_service import UpsertService


def test_db_prepare_success_parses_and_persists(project_fixture: pytest.FixtureRequest) -> None:
    fixture_root = project_fixture("full_project")
    config = BootstrapConfig(docs_root=fixture_root, storage_path=fixture_root / "db.sqlite")
    options = BootstrapOptions(dry_run=False)

    gateway = DataStoreGateway(storage_path=config.storage_path)
    orchestrator = BootstrapOrchestrator(
        discovery_service=DocumentationDiscoveryService(config.docs_root),
        upsert_service=UpsertService(gateway),
        task_run_service=TaskRunService(),
        ai_job_service=AIJobService(),
        gateway=gateway,
    )

    with (
        mock.patch.object(gateway, "create_or_update_projects") as projects_mock,
        mock.patch.object(gateway, "create_or_update_features") as features_mock,
        mock.patch.object(gateway, "create_or_update_specs") as specs_mock,
        mock.patch.object(gateway, "create_or_update_tasks") as tasks_mock,
        mock.patch.object(gateway, "create_task_dependencies") as deps_mock,
        mock.patch.object(gateway, "create_task_runs") as task_runs_mock,
        mock.patch.object(gateway, "create_ai_jobs") as ai_jobs_mock,
    ):
        summary = orchestrator.run(config=config, options=options)

    assert summary.project_count == 1
    assert summary.feature_count == 1
    assert summary.spec_count == 1
    assert summary.task_count == 2
    assert summary.dependency_count == 1
    assert summary.task_run_count == 2
    assert summary.ai_job_count == 1

    projects_mock.assert_called_once()
    features_mock.assert_called_once()
    specs_mock.assert_called_once()
    tasks_mock.assert_called_once()
    deps_mock.assert_called_once()
    task_runs_mock.assert_called_once()
    ai_jobs_mock.assert_called_once()
