"""
Integration tests for malformed documentation detection.
"""

from pathlib import Path
from typer.testing import CliRunner
from src.cli import app
from tests.fixtures.projects.malformed_docs import create_malformed_project

runner = CliRunner()

def test_malformed_doc_warning(tmp_path: Path):
    """
    Test that malformed documents (placeholders/short descriptions) produce warnings.
    """
    project_dir = tmp_path / "malformed"
    create_malformed_project(project_dir)
    
    result = runner.invoke(app, ["--docs-path", str(project_dir), "--dry-run"])
    
    assert result.exit_code == 0  # Warnings are not blocking by default unless configured
    assert "VALIDATION WARNINGS" in result.stdout
    assert "Task title contains placeholder" in result.stdout
    assert "Task acceptance criteria is missing or too short" in result.stdout
