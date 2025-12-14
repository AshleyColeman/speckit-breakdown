from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from src.cli import app
from tests.fixtures.projects.validation_circular import create_circular_project

runner = CliRunner()


def test_rollback_removes_new_db_on_failure(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_circular_project(project_dir)

    db_path = tmp_path / "test_db.sqlite"
    assert not db_path.exists()

    result = runner.invoke(app, ["--docs-path", str(project_dir), "--storage-path", str(db_path)])
    assert result.exit_code == 1

    assert not db_path.exists()
