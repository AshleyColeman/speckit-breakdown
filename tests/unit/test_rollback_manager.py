from unittest.mock import Mock

import pytest
from src.services.rollback_manager import RollbackManager, transactional_context

class TestRollbackManager:

    def test_add_action(self):
        manager = RollbackManager()
        mock_fn = Mock()
        
        manager.add_action("test_action", mock_fn)
        
        assert len(manager.actions) == 1
        assert manager.actions[0].description == "test_action"
        assert manager.actions[0].fn == mock_fn

    def test_rollback_executes_actions_in_reverse_order(self):
        manager = RollbackManager()
        full_list = []
        
        manager.add_action("first", lambda: full_list.append("first"))
        manager.add_action("second", lambda: full_list.append("second"))
        
        manager.rollback()
        
        assert full_list == ["second", "first"]
        assert len(manager.actions) == 0

    def test_rollback_handles_exceptions_gracefully(self):
        manager = RollbackManager()
        mock_success = Mock()
        
        def failing_action():
            raise ValueError("Boom")
            
        manager.add_action("success", mock_success)
        manager.add_action("fail", failing_action)
        
        # Should not raise exception
        manager.rollback()
        
        mock_success.assert_called_once()
        assert len(manager.actions) == 0

    def test_transactional_context_rolls_back_on_error(self):
        manager = RollbackManager()
        mock_action = Mock()
        
        with pytest.raises(ValueError):
            with transactional_context(manager):
                manager.add_action("cleanup", mock_action)
                # Ensure it's added
                assert len(manager.actions) == 1
                raise ValueError("Oops")
        
        # Rollback should have triggered
        mock_action.assert_called_once()
        assert len(manager.actions) == 0

    def test_transactional_context_does_not_rollback_on_success(self):
        manager = RollbackManager()
        mock_action = Mock()
        
        with transactional_context(manager):
            manager.add_action("cleanup", mock_action)
        
        # Rollback should NOT trigger
        mock_action.assert_not_called()
        # Actions remain registered (responsibility of caller to clear if needed, or they persist for lifecycle)
        assert len(manager.actions) == 1
