from unittest.mock import Mock, patch
import pytest
from src.lib.metrics import emit_bootstrap_summary
from dataclasses import dataclass

@dataclass
class SummaryDTO:
    features: int
    tasks: int

class TestMetrics:

    @patch("src.lib.metrics.logger")
    def test_emit_summary_logs_structured_data(self, mock_logger):
        summary = SummaryDTO(features=5, tasks=10)
        
        emit_bootstrap_summary(summary)
        
        mock_logger.info.assert_called_once_with(
            "Bootstrap summary", 
            extra={'features': 5, 'tasks': 10}
        )

    @patch("src.lib.metrics.logger")
    def test_emit_summary_handles_non_dataclass_objects(self, mock_logger):
        # Simulating a case where asdict fails (e.g. regular object)
        class RegularObj:
            def __init__(self):
                self.features = 1
                
        summary = RegularObj()
        
        # Should not raise exception
        emit_bootstrap_summary(summary)
        
        mock_logger.info.assert_called_once()
        # Verify it fell back to __dict__
        call_args = mock_logger.info.call_args
        assert call_args[1]['extra']['features'] == 1
