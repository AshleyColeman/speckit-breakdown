"""
Integration tests for validation scenarios in db_prepare.
"""

import shutil
from pathlib import Path

from typer.testing import CliRunner

from src.cli import app
from tests.fixtures.projects.validation_circular import create_circular_project
from tests.fixtures.projects.validation_duplicate import create_duplicate_project

runner = CliRunner()

def test_circular_dependency_detection(tmp_path: Path):
    """
    Test that a circular dependency in tasks is detected and halts execution.
    """
    project_dir = tmp_path / "valid_circular"
    create_circular_project(project_dir)
    
    result = runner.invoke(app, ["--docs-path", str(project_dir), "--dry-run"])
    
    assert result.exit_code == 1
    assert "Bootstrap failed" in result.stdout
    assert "circular dependency detected" in result.stdout.lower()
    assert "validation errors (blocking)" in result.stdout.lower()


def test_duplicate_id_detection(tmp_path: Path):
    """
    Test that duplicate IDs across entities are detected and halt execution.
    """
    project_dir = tmp_path / "valid_duplicate"
    create_duplicate_project(project_dir)
    
    result = runner.invoke(app, ["--docs-path", str(project_dir), "--dry-run"])
    
    assert result.exit_code == 1
    assert "Duplicate Task Code found" in result.stdout
