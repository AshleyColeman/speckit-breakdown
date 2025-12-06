"""
Unit tests for DataStoreGateway retry logic.
"""
import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.services.data_store_gateway import DataStoreGateway
from src.models.entities import ProjectDTO

def test_sqlite_retry_success(tmp_path: Path):
    """Test that operation retries on locking error and eventually succeeds."""
    gateway = DataStoreGateway(tmp_path / "db.sqlite")
    project = ProjectDTO(code="P-1", name="Test", description="Desc")
    
    # Mock sqlite3.connect to raise OperationalError twice then succeed
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        
        # Side effect: Raises error 2 times, then returns connection
        mock_connect.side_effect = [
            sqlite3.OperationalError("database is locked"),
            sqlite3.OperationalError("database is locked"),
            mock_conn
        ]
        
        gateway.create_or_update_projects([project])
        
        # Should have called connect 3 times
        assert mock_connect.call_count == 3
        # Should have executed insert
        # We need to check if the mocked cursor executed.
        # gateway code: 
        # with sqlite3.connect(...) as conn:
        #     cursor = conn.cursor()
        #     cursor.execute(...)
        # Context manager enter returns self (conn)
        mock_conn.__enter__.return_value = mock_conn
        assert mock_cursor.executemany.called

def test_sqlite_retry_failure(tmp_path: Path):
    """Test that operation raises after max retries."""
    gateway = DataStoreGateway(tmp_path / "db.sqlite")
    project = ProjectDTO(code="P-1", name="Test", description="Desc")
    
    with patch("sqlite3.connect") as mock_connect:
        mock_connect.side_effect = sqlite3.OperationalError("database is locked")
        
        with pytest.raises(sqlite3.OperationalError, match="database is locked"):
            gateway.create_or_update_projects([project])
        
        # 1 initial + 3 retries = 4 calls (default matches implementation?)
        # Implementation has range(retries=3). 
        # Loop runs 3 times. If all fail, it raises.
        # Wait, my logic in decorator:
        # for i in range(retries): ...
        # If max retries is 3, it tries 3 times total? Or initial + 3?
        # range(3) -> 0, 1, 2. So 3 attempts total.
        assert mock_connect.call_count == 3
