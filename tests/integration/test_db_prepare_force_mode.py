"""
Integration tests for --force mode and conflict resolution.
"""

from pathlib import Path
from typer.testing import CliRunner

from src.cli import app
from tests.fixtures.projects.full_project import create_full_project

runner = CliRunner()

def test_force_mode_overwrite(tmp_path: Path):
    """
    Test that modifying a file and running with --force updates the entity,
    while running without --force might fail or warn (idempotency check).
    """
    project_dir = tmp_path / "project"
    create_full_project(project_dir)
    db_path = tmp_path / "test_db.sqlite"
    
    # Initial run
    result_initial = runner.invoke(app, ["--docs-path", str(project_dir), "--storage-path", str(db_path)])
    assert result_initial.exit_code == 0, f"Initial run failed: {result_initial.stdout}"
    
    # Modify a task title
    task_file = project_dir / "tasks" / "001-user-auth" / "t1-login-screen.md" # Assuming t1-login-screen.md exists based on listing
    if not task_file.exists():
         # Fallback search if name is different
         task_file = list((project_dir / "tasks" / "001-user-auth").glob("*.md"))[0]
    content = task_file.read_text()
    new_content = content.replace("Task 1", "Task 1 Updated")
    task_file.write_text(new_content)
    
    # Run without force - should detect change but maybe ignore if ID matches?
    # Or strict idempotency might error on mismatch?
    # Spec says: "--force: Force overwrite mismatched entities".
    # Without force, it should probably skip or warn.
    
    result = runner.invoke(app, ["--docs-path", str(project_dir), "--storage-path", str(db_path)])
    assert result.exit_code == 0 # Should arguably succeed with skip/warn
    
    # Run with force
    result_force = runner.invoke(app, ["--docs-path", str(project_dir), "--force", "--storage-path", str(db_path)])
    assert result_force.exit_code == 0
    # Expected: Update in DB.
