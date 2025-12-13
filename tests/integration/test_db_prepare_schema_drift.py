"""
Integration checks for schema drift detection.
"""
import sqlite3
import pytest
from pathlib import Path
from src.services.data_store_gateway import DataStoreGateway
from src.models.entities import ProjectDTO, FeatureDTO, TaskDTO, TaskDependencyDTO

def test_schema_drift_detection(tmp_path: Path):
    """Test that gateway detects missing columns."""
    db_path = tmp_path / "drift.sqlite"
    
    # manually create an older version of the schema (e.g. missing 'metadata')
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE projects (code TEXT PRIMARY KEY, name TEXT, description TEXT)")
        conn.commit()
        
    gateway = DataStoreGateway(db_path)
    
    # We expect verify_schema to raise or return False
    # Since I haven't implemented it yet, this test will fail or error if I call it via new method
    # Let's assume the method is verify_schema()
    
    with pytest.raises(Exception, match="Schema drift detected"):
        gateway.verify_schema()

def test_schema_valid(tmp_path: Path):
    """Test that clean schema passes verification."""
    db_path = tmp_path / "clean.sqlite"
    gateway = DataStoreGateway(db_path) # correct schema created in init
    
    # Should not raise
    gateway.verify_schema()


def test_sqlite_foreign_keys_enforced(tmp_path: Path) -> None:
    db_path = tmp_path / "fk.sqlite"
    gateway = DataStoreGateway(db_path)

    gateway.create_or_update_projects([
        ProjectDTO(code="p1", name="Project", description="desc")
    ])
    gateway.create_or_update_features([
        FeatureDTO(code="f1", project_code="p1", name="Feature", description="desc", priority="P1")
    ])
    gateway.create_or_update_tasks([
        TaskDTO(
            code="t1",
            feature_code="f1",
            title="Task",
            status="pending",
            task_type="implementation",
            acceptance="",
        )
    ])

    with pytest.raises(sqlite3.IntegrityError):
        gateway.create_task_dependencies([
            TaskDependencyDTO(task_code="t1", depends_on="does-not-exist")
        ])
