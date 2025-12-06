"""
Unit tests for CLI option parsing and flag validation.
"""
from unittest.mock import patch
from typer.testing import CliRunner
from src.cli import app
from src.services.bootstrap_options import BootstrapOptions

runner = CliRunner()

def test_flag_parsing_defaults():
    """Test that default options are set correctly when no flags are provided."""
    with patch("src.cli.commands.db_prepare._run_bootstrap") as mock_run:
        result = runner.invoke(app, ["--docs-path", "specs/"])
        assert result.exit_code == 0
        
        args, _ = mock_run.call_args
        options: BootstrapOptions = args[1]
        
        assert options.dry_run is False
        assert options.force is False
        assert options.project is None
        assert options.skip_task_runs is False
        assert options.skip_ai_jobs is False

def test_flag_parsing_explicit():
    """Test that explicit flags are correctly parsed into BootstrapOptions."""
    with patch("src.cli.commands.db_prepare._run_bootstrap") as mock_run:
        result = runner.invoke(app, [
            "--docs-path", "specs/",
            "--dry-run",
            "--force",
            "--project", "P-123",
            "--skip-task-runs",
            "--skip-ai-jobs"
        ])
        assert result.exit_code == 0
        
        args, _ = mock_run.call_args
        options: BootstrapOptions = args[1]
        
        assert options.dry_run is True
        assert options.force is True
        assert options.project == "P-123"
        assert options.skip_task_runs is True
        assert options.skip_ai_jobs is True

def test_project_flag_short():
    """Test -p short flag for project."""
    with patch("src.cli.commands.db_prepare._run_bootstrap") as mock_run:
        result = runner.invoke(app, ["--docs-path", "specs/", "-p", "P-SHORT"])
        assert result.exit_code == 0
        
        args, _ = mock_run.call_args
        options: BootstrapOptions = args[1]
        assert options.project == "P-SHORT"
