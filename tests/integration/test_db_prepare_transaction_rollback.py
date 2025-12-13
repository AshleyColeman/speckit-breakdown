"""Integration test for transactional persistence per run.

Ensures that if persistence fails mid-run, all writes are rolled back.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.services.bootstrap_options import BootstrapOptions
from src.services.bootstrap_orchestrator import BootstrapOrchestrator
from src.services.data_store_gateway import DataStoreGateway
from tests.fixtures.projects.full_project import create_full_project


def _count_rows(db_path: Path, table: str) -> int:
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return int(cur.fetchone()[0])


def test_sqlite_rollback_on_mid_run_failure(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_full_project(project_dir)

    db_path = tmp_path / "db.sqlite"
    gateway = DataStoreGateway(db_path)

    original_create_or_update_specs = gateway.create_or_update_specs

    def failing_create_or_update_specs(specs):
        original_create_or_update_specs(specs)
        raise RuntimeError("intentional failure during persistence")

    gateway.create_or_update_specs = failing_create_or_update_specs

    orchestrator = BootstrapOrchestrator(project_dir, gateway)
    result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=False))

    assert result.success is False

    assert _count_rows(db_path, "projects") == 0
    assert _count_rows(db_path, "features") == 0
    assert _count_rows(db_path, "specs") == 0
    assert _count_rows(db_path, "tasks") == 0
    assert _count_rows(db_path, "task_dependencies") == 0
    assert _count_rows(db_path, "task_runs") == 0
    assert _count_rows(db_path, "ai_jobs") == 0
