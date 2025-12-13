
"""
Integration test for PostgreSQL backend.

Requires DATABASE_URL to be set or assumes default local Docker instance.
"""
import os
import pytest
import psycopg2
from pathlib import Path
from tempfile import TemporaryDirectory
import contextlib

from src.services.data_store_gateway import DataStoreGateway
from src.services.bootstrap_orchestrator import BootstrapOrchestrator
from src.services.bootstrap_options import BootstrapOptions

# Use user-provided DB URL or fallback
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/action_db")

PROJECT_NAME = "Test Postgres Project"


def test_postgres_requires_explicit_enablement():
    with pytest.raises(ValueError, match="experimental"):
        DataStoreGateway(DB_URL)

def _clean_test_data(conn):
    """Clean up any test data from the database."""
    with conn.cursor() as cursor:
        # Delete dependencies first (Foreign Key constraints)
        cursor.execute("DELETE FROM task_dependencies WHERE successor_id IN (SELECT id FROM tasks WHERE metadata->>'code' LIKE 'test-task%')")
        cursor.execute("DELETE FROM task_dependencies WHERE predecessor_id IN (SELECT id FROM tasks WHERE metadata->>'code' LIKE 'test-task%')")
        
        # Delete Tasks (identified by metadata code)
        cursor.execute("DELETE FROM tasks WHERE metadata->>'code' LIKE 'test-task%'")
        
        # Delete Specs/Features/Projects (identified by name)
        cursor.execute("DELETE FROM specs WHERE name = 'Test Spec'")
        cursor.execute("DELETE FROM features WHERE name = 'Test Feature'")
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
    
    # Post-test cleanup
    _clean_test_data(conn)
    conn.close()

@pytest.fixture
def sample_docs():
    """Create sample docs with TEST- prefix."""
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        (root / "features").mkdir()
        (root / "specs").mkdir()
        (root / "tasks").mkdir()
        (root / "dependencies").mkdir()

        (root / "project.md").write_text("""---
code: test-postgres-project
name: Test Postgres Project
description: Integration test for Postgres
repository_path: https://github.com/test
---
# Test Postgres Project
""")

        # Feature Code derived from filename TEST-feat.md -> 'test-feat'
        (root / "features" / "TEST-feat.md").write_text("""---
priority: P1
project_code: Test Postgres Project
---
# Test Feature
""")

        (root / "specs" / "TEST-spec.md").write_text("""---
feature_code: Feature Name For Lookup
---
# Test Spec
""".replace("Feature Name For Lookup", "Test Feature"))

        (root / "tasks" / "TEST-task.md").write_text("""---
feature_code: Feature Name For Lookup
status: pending
task_type: implementation
---
# Test Task
""".replace("Feature Name For Lookup", "Test Feature"))
        
        yield root

def test_postgres_bootstrap_success(db_connection, sample_docs):
    """Verify full bootstrap into Postgres."""
    
    # Initialize Gateway with DB URL
    gateway = DataStoreGateway(DB_URL, enable_experimental_postgres=True)

    # Orchestrator wraps persistence in gateway.transaction(); ensure it's available.
    # The real DataStoreGateway provides it, but this keeps the test resilient if the
    # gateway is swapped/mocked in future.
    if not hasattr(gateway, "transaction"):
        @contextlib.contextmanager
        def transaction():
            yield
        gateway.transaction = transaction
    
    # Run Orchestrator
    orchestrator = BootstrapOrchestrator(sample_docs, gateway)
    
    result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=False))
    
    assert result.success is True
    assert result.error_message is None

    assert gateway.get_project("Test Postgres Project") is not None
    assert gateway.get_feature("Test Feature") is not None
    assert gateway.get_spec("Test Spec") is not None
    assert gateway.get_task("test-task") is not None
    
    # Verify in DB
    with db_connection.cursor() as cursor:
        # Check Project by Name
        cursor.execute("SELECT id, name FROM projects WHERE name = %s", (PROJECT_NAME,))
        proj_row = cursor.fetchone()
        assert proj_row is not None
        proj_id = proj_row[0]
        
        # Check Feature by Name
        cursor.execute("SELECT id FROM features WHERE project_id = %s AND name = 'Test Feature'", (proj_id,))
        feat_rows = cursor.fetchall()
        assert len(feat_rows) == 1
        
        # Check Spec by Name
        cursor.execute("SELECT id FROM specs WHERE feature_id = %s AND name = 'Test Spec'", (feat_rows[0][0],))
        spec_rows = cursor.fetchall()
        assert len(spec_rows) >= 1

        # Check Task by Metadata Code (slugified from filename 'TEST-task.md' -> 'test-task')
        cursor.execute("SELECT id, status FROM tasks WHERE metadata->>'code' = 'test-task'")
        task_row = cursor.fetchone()
        assert task_row is not None


def test_postgres_does_not_use_slug_name_heuristics(db_connection, sample_docs):
    """Verify Postgres persistence does not guess project links via slug/name normalization."""

    _clean_test_data(db_connection)

    docs_root = sample_docs
    (docs_root / "features" / "TEST-feat.md").write_text("""---
priority: P1
project_code: test-postgres-project
---
# Test Feature
""")

    gateway = DataStoreGateway(DB_URL, enable_experimental_postgres=True)
    if not hasattr(gateway, "transaction"):
        @contextlib.contextmanager
        def transaction():
            yield
        gateway.transaction = transaction
    orchestrator = BootstrapOrchestrator(docs_root, gateway)

    result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=False))

    assert result.success is False
