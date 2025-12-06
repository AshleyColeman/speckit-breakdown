"""
Integration checks for schema drift detection.
"""
import sqlite3
import pytest
from pathlib import Path
from src.services.data_store_gateway import DataStoreGateway

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
