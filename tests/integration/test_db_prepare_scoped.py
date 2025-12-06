"""
Integration tests for purposeful scoping and skipping of entities.
"""
from pathlib import Path
from typer.testing import CliRunner
from src.cli import app
from tests.fixtures.projects.scoped_project import create_scoped_project

runner = CliRunner()

def test_project_filtering(tmp_path: Path):
    """Test that --project ignores non-matching projects."""
    project_dir = tmp_path / "scoped_project"
    create_scoped_project(project_dir)
    
    # Run for Project A (Match)
    result_match = runner.invoke(app, ["--docs-path", str(project_dir), "--project", "P-A"])
    assert result_match.exit_code == 0
    assert "Projects: 1" in result_match.stdout
    assert "Features: 1" in result_match.stdout

    # Run for Project B (Mismatch)
    result_mismatch = runner.invoke(app, ["--docs-path", str(project_dir), "--project", "P-B"])
    assert result_mismatch.exit_code == 0
    # Should result in empty bootstrap or explicitly 0
    assert "Projects: 0" in result_mismatch.stdout
    assert "Features: 0" in result_mismatch.stdout

def test_skip_flags(tmp_path: Path):
    """Test that --skip-task-runs and --skip-ai-jobs work."""
    project_dir = tmp_path / "scoped_project"
    create_scoped_project(project_dir)
    
    # Run with skips
    result = runner.invoke(app, [
        "--docs-path", str(project_dir), 
        "--project", "P-A",
        "--skip-task-runs",
        "--skip-ai-jobs"
    ])
    assert result.exit_code == 0
    
    assert "Task Runs: 0" in result.stdout
    assert "AI Jobs: 0" in result.stdout
