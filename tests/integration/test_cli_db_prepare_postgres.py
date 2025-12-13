"""
Integration test for the CLI command `speckit.db.prepare` against PostgreSQL.
Ensures the slash command works end-to-end as a black box.
"""
import os
import pytest
import psycopg2
from pathlib import Path
from tempfile import TemporaryDirectory
from typer.testing import CliRunner

from src.cli import app
from src.services.data_store_gateway import DataStoreGateway

# Use user-provided DB URL or fallback
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/action_db")
runner = CliRunner()

PROJECT_NAME = "CLI Test Project"

def _clean_test_data(conn):
    """Clean up any test data from the database."""
    with conn.cursor() as cursor:
        # Delete dependencies first (Foreign Key constraints)
        cursor.execute("DELETE FROM task_dependencies WHERE successor_id IN (SELECT id FROM tasks WHERE metadata->>'code' LIKE 'cli-test-%')")
        cursor.execute("DELETE FROM task_dependencies WHERE predecessor_id IN (SELECT id FROM tasks WHERE metadata->>'code' LIKE 'cli-test-%')")
        
        # Delete Tasks
        cursor.execute("DELETE FROM tasks WHERE metadata->>'code' LIKE 'cli-test-%'")
        
        # Delete Specs
        cursor.execute("DELETE FROM specs WHERE name LIKE 'CLI Test Spec%'")
        
        # Delete Features
        cursor.execute("DELETE FROM features WHERE name = 'CLI Test Feature'")
        
        # Delete Projects
        cursor.execute("DELETE FROM projects WHERE name = %s", (PROJECT_NAME,))

@pytest.fixture(scope="module")
def db_connection():
    """Verify connection and clean up before/after."""
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
    except Exception as e:
        pytest.skip(f"Database not available: {e}")
        return

    # Pre-test cleanup
    _clean_test_data(conn)
    
    yield conn
    
    # Post-test cleanup DISABLED for manual verification
    # _clean_test_data(conn)
    conn.close()

@pytest.fixture
def cli_docs_root():
    """Create sample docs structure for CLI test."""
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        (root / "features").mkdir()
        (root / "specs").mkdir()
        (root / "tasks").mkdir()
        (root / "dependencies").mkdir()

        (root / "project.md").write_text("""---
name: CLI Test Project
description: Integration test via CLI
repository_path: https://github.com/cli-test
---
# CLI Test Project
""")

        (root / "features" / "CLI-TEST-feat.md").write_text("""---
priority: P1
project_code: CLI Test Project
---
# CLI Test Feature
""")

        (root / "specs" / "CLI-TEST-spec.md").write_text("""---
feature_code: CLI Test Feature
---
# CLI Test Spec
""")
    
        (root / "specs" / "CLI-TEST-spec-2.md").write_text("""---
feature_code: CLI Test Feature
---
# CLI Test Spec 2
""")
    
        (root / "tasks" / "CLI-TEST-task-A.md").write_text("""---
feature_code: CLI Test Feature
status: pending
task_type: implementation
---
# CLI-TEST-task-A
""")
        (root / "tasks" / "CLI-TEST-task-B.md").write_text("""---
feature_code: CLI Test Feature
status: pending
task_type: implementation
dependencies:
  - CLI-TEST-task-A
---
# CLI-TEST-task-B
""")
        (root / "tasks" / "CLI-TEST-task-C.md").write_text("""---
feature_code: CLI Test Feature
status: pending
task_type: implementation
dependencies:
  - CLI-TEST-task-A
---
# CLI-TEST-task-C
""")
        (root / "tasks" / "CLI-TEST-task-D.md").write_text("""---
feature_code: CLI Test Feature
status: pending
task_type: implementation
dependencies:
  - CLI-TEST-task-B
  - CLI-TEST-task-C
---
# CLI-TEST-task-D
""")
        (root / "tasks" / "CLI-TEST-task-E.md").write_text("""---
feature_code: CLI Test Feature
status: pending
task_type: implementation
dependencies:
  - CLI-TEST-task-D
---
# CLI-TEST-task-E
# CLI-TEST-task-E
""")
        (root / "tasks" / "CLI-TEST-task-F.md").write_text("""---
feature_code: CLI Test Feature
status: pending
task_type: implementation
dependencies:
  - CLI-TEST-task-A
---
# CLI-TEST-task-F
""")
        (root / "tasks" / "CLI-TEST-task-G.md").write_text("""---
feature_code: CLI Test Feature
status: pending
task_type: implementation
dependencies:
  - CLI-TEST-task-A
---
# CLI-TEST-task-G
""")

        
        yield root

def test_cli_db_prepare_postgres_success(db_connection, cli_docs_root):
    """
    Verify that `speckit.db.prepare` correctly pushes data to Postgres.
    """
    # ... (rest of test)
    """
    Verify that `speckit.db.prepare` correctly pushes data to Postgres.
    """
    
    # args: --docs-path <tmp> --db-url <url>
    result = runner.invoke(app, [
        "--docs-path", str(cli_docs_root),
        "--db-url", DB_URL,
        "--enable-experimental-postgres",
        "--verbose" 
    ], catch_exceptions=False)
    
    # Assert successful execution
    print(result.stdout)
    assert result.exit_code == 0, f"CLI Command failed with exit code {result.exit_code}. Output:\n{result.stdout}"
    assert "Bootstrap completed successfully." in result.stdout
    assert "Projects: 1" in result.stdout
    assert "Features: 1" in result.stdout
    assert "Specs: 2" in result.stdout
    assert "Tasks: 7" in result.stdout

    # Assert Database State
    with db_connection.cursor() as cursor:
        # Check Project
        cursor.execute("SELECT id FROM projects WHERE name = %s", (PROJECT_NAME,))
        proj_row = cursor.fetchone()
        assert proj_row is not None, "Project not found in DB"
        proj_id = proj_row[0]
        
        # Check Feature linked to Project
        cursor.execute("SELECT id FROM features WHERE project_id = %s AND name = 'CLI Test Feature'", (proj_id,))
        feat_rows = cursor.fetchall()
        assert len(feat_rows) == 1, "Feature not found or not linked to project"
        feat_id = feat_rows[0][0]

        # Check Spec 1 linked to Feature
        cursor.execute("SELECT id FROM specs WHERE feature_id = %s AND name = 'CLI Test Spec'", (feat_id,))
        spec_rows = cursor.fetchall()
        assert len(spec_rows) == 1, "Spec 1 not found or not linked to feature"

        # Check Spec 2 linked to Feature
        cursor.execute("SELECT id FROM specs WHERE feature_id = %s AND name = 'CLI Test Spec 2'", (feat_id,))
        spec2_rows = cursor.fetchall()
        assert len(spec2_rows) == 1, "Spec 2 not found or not linked to feature"

        # Check Tasks
        tasks = {}
        for char in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            code_slug = f'cli-test-task-{char.lower()}'
            cursor.execute("SELECT id, status, step_order FROM tasks WHERE metadata->>'code' = %s", (code_slug,))
            row = cursor.fetchone()
            assert row is not None, f"Task {char} not found"
            tasks[char] = {'id': row[0], 'status': row[1], 'step_order': row[2]}
        
        # Verify Step Order Logic (Topological Sort)
        # A (Root) -> 1
        # B (Deps A) -> 2
        # C (Deps A) -> 2
        # F (Deps A) -> 2 (Parallel)
        # G (Deps A) -> 2 (Parallel)
        # D (Deps B, C) -> 3
        # E (Deps D) -> 4
        assert tasks['A']['step_order'] == 1, f"Task A step_order {tasks['A']['step_order']} != 1"
        assert tasks['B']['step_order'] == 2, f"Task B step_order {tasks['B']['step_order']} != 2"
        assert tasks['C']['step_order'] == 2, f"Task C step_order {tasks['C']['step_order']} != 2"
        assert tasks['F']['step_order'] == 2, f"Task F step_order {tasks['F']['step_order']} != 2"
        assert tasks['G']['step_order'] == 2, f"Task G step_order {tasks['G']['step_order']} != 2"
        assert tasks['D']['step_order'] == 3, f"Task D step_order {tasks['D']['step_order']} != 3"
        assert tasks['E']['step_order'] == 4, f"Task E step_order {tasks['E']['step_order']} != 4"
        
        # Check Dependencies
        cursor.execute("SELECT predecessor_id, successor_id FROM task_dependencies")
        rows = cursor.fetchall()
        
        # Verify A -> B
        cursor.execute("SELECT 1 FROM task_dependencies WHERE predecessor_id = %s AND successor_id = %s", (tasks['A']['id'], tasks['B']['id']))
        assert cursor.fetchone() is not None, "Missing dependency A -> B"

        # Verify A -> C
        cursor.execute("SELECT 1 FROM task_dependencies WHERE predecessor_id = %s AND successor_id = %s", (tasks['A']['id'], tasks['C']['id']))
        assert cursor.fetchone() is not None, "Missing dependency A -> C"
        
        # Verify A -> F and A -> G (Parallel)
        cursor.execute("SELECT 1 FROM task_dependencies WHERE predecessor_id = %s AND successor_id = %s", (tasks['A']['id'], tasks['F']['id']))
        assert cursor.fetchone() is not None, "Missing dependency A -> F"
        cursor.execute("SELECT 1 FROM task_dependencies WHERE predecessor_id = %s AND successor_id = %s", (tasks['A']['id'], tasks['G']['id']))
        assert cursor.fetchone() is not None, "Missing dependency A -> G"

        # Verify B -> D
        cursor.execute("SELECT 1 FROM task_dependencies WHERE predecessor_id = %s AND successor_id = %s", (tasks['B']['id'], tasks['D']['id']))
        assert cursor.fetchone() is not None, "Missing dependency B -> D"

        # Verify C -> D
        cursor.execute("SELECT 1 FROM task_dependencies WHERE predecessor_id = %s AND successor_id = %s", (tasks['C']['id'], tasks['D']['id']))
        assert cursor.fetchone() is not None, "Missing dependency C -> D"

        # Verify D -> E
        cursor.execute("SELECT 1 FROM task_dependencies WHERE predecessor_id = %s AND successor_id = %s", (tasks['D']['id'], tasks['E']['id']))
        assert cursor.fetchone() is not None, "Missing dependency D -> E"


def test_cli_db_prepare_postgres_requires_explicit_enablement(tmp_path):
    root = tmp_path / "project_gate"
    root.mkdir()
    (root / "features").mkdir()
    (root / "specs").mkdir()
    (root / "tasks").mkdir()
    (root / "dependencies").mkdir()

    (root / "project.md").write_text("""---
name: Gate Test Project
description: Gate test via CLI
repository_path: https://github.com/gate-test
---
# Gate Test Project
""")
    (root / "features" / "GATE-feat.md").write_text("""---
priority: P1
project_code: Gate Test Project
---
# Gate Test Feature
""")
    (root / "specs" / "GATE-spec.md").write_text("""---
feature_code: Gate Test Feature
---
# Gate Test Spec
""")
    (root / "tasks" / "GATE-task.md").write_text("""---
feature_code: Gate Test Feature
status: pending
task_type: implementation
---
# Gate Test Task
""")

    result = runner.invoke(
        app,
        ["--docs-path", str(root), "--db-url", f"{DB_URL}"],
        catch_exceptions=False,
    )

    assert result.exit_code != 0
    assert "experimental" in result.stdout.lower()
    assert "--enable-experimental-postgres" in result.stdout

def test_cli_dependency_inconsistency_failure(tmp_path):
    """
    Negative test to verify that the CLI rejects invalid dependency states.
    Scenario: Task B is 'ready' but depends on Task A which is 'pending'.
    Rule: Successor cannot be 'ready' unless predecessor is 'completed'.
    """
    # Setup simple project structure
    root = tmp_path / "project_failure"
    root.mkdir()
    (root / "project.md").write_text("# Failure Project\nCode: FAIL-PROJ")
    
    feats = root / "features"
    feats.mkdir()
    (root / "specs").mkdir()
    (root / "dependencies").mkdir()
    (feats / "FAIL-feat.md").write_text("""---
project_code: FAIL-PROJ
---
# Fail Feature
""")

    tasks = root / "tasks"
    tasks.mkdir()
    
    # Task A: Pending
    (tasks / "FAIL-task-A.md").write_text("""---
feature_code: FAIL-feat
status: pending
task_type: implementation
---
# FAIL-task-A
""")

    # Task B: Ready (Invalid! Depends on A)
    (tasks / "FAIL-task-B.md").write_text("""---
feature_code: FAIL-feat
status: ready
task_type: implementation
dependencies:
  - FAIL-task-A
---
# FAIL-task-B
""")

    result = runner.invoke(
        app,
        [
            "--docs-path",
            str(root),
            "--db-url",
            f"{DB_URL}",
            "--enable-experimental-postgres",
            "--force",
        ],
        catch_exceptions=False,
    )
    
    print("\n=== FAILURE TEST OUTPUT ===")
    print(result.stdout)
    
    # Should fail validation
    assert result.exit_code != 0
    assert "Task 'fail-task-b' is 'ready' but dependency 'fail-task-a' is 'pending'" in result.stdout.lower() or \
           "dependencies must be 'completed'" in result.stdout.lower()
