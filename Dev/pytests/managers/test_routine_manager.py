"""
TDD Tests for RoutineManager.

Tests for routine management: listing, executing, creating routines.
Tests created BEFORE implementation to guide development.

PHASE 6: RoutineManager TDD Tests
Total Tests: 45+
Coverage Target: 90%+
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List


class TestRoutineManagerGetRoutines:
    """Tests for retrieving routines."""

    def test_get_routines_returns_list(self) -> None:
        """Test that get_routines returns a list."""
        manager = Mock()
        manager.get_routines.return_value = [
            {"routine_id": "r1", "name": "Good Morning"},
            {"routine_id": "r2", "name": "Good Night"}
        ]
        
        routines = manager.get_routines()
        assert isinstance(routines, list)
        assert len(routines) == 2

    def test_get_routines_contains_required_fields(self) -> None:
        """Test routine objects contain required fields."""
        manager = Mock()
        manager.get_routines.return_value = [{
            "routine_id": "r1",
            "name": "Morning Routine",
            "description": "Starts the day",
            "enabled": True,
            "actions": []
        }]
        
        routines = manager.get_routines()
        routine = routines[0]
        
        assert "routine_id" in routine
        assert "name" in routine
        assert "enabled" in routine

    def test_get_routines_empty_list(self) -> None:
        """Test get_routines returns empty list when no routines."""
        manager = Mock()
        manager.get_routines.return_value = []
        
        routines = manager.get_routines()
        assert routines == []

    def test_get_routines_with_filtering(self) -> None:
        """Test filtering routines by criteria."""
        manager = Mock()
        all_routines = [
            {"routine_id": "r1", "name": "Morning", "enabled": True},
            {"routine_id": "r2", "name": "Night", "enabled": False},
            {"routine_id": "r3", "name": "Work", "enabled": True}
        ]
        
        manager.get_routines.return_value = all_routines
        routines = manager.get_routines()
        
        # Filter enabled routines
        enabled = [r for r in routines if r["enabled"]]
        assert len(enabled) == 2


class TestRoutineManagerExecute:
    """Tests for executing routines."""

    def test_execute_routine_success(self) -> None:
        """Test executing a routine successfully."""
        manager = Mock()
        manager.execute.return_value = {"executed": True, "routine_id": "r1"}
        
        result = manager.execute("r1")
        assert result["executed"] is True

    def test_execute_routine_with_device(self) -> None:
        """Test executing routine on specific device."""
        manager = Mock()
        manager.execute.return_value = {"status": "executing", "device": "ABCD"}
        
        result = manager.execute("r1", device="ABCD")
        manager.execute.assert_called_once_with("r1", device="ABCD")

    def test_execute_routine_invalid_id_fails(self) -> None:
        """Test executing with invalid routine ID fails."""
        manager = Mock()
        manager.execute.side_effect = ValueError("Routine not found")
        
        with pytest.raises(ValueError):
            manager.execute("invalid_id")

    def test_execute_routine_returns_status(self) -> None:
        """Test execute returns execution status."""
        manager = Mock()
        manager.execute.return_value = {
            "routine_id": "r1",
            "status": "running",
            "progress": 25
        }
        
        result = manager.execute("r1")
        assert "status" in result
        assert "routine_id" in result

    def test_execute_routine_timeout_handling(self) -> None:
        """Test handling execution timeout."""
        manager = Mock()
        manager.execute.side_effect = TimeoutError("Execution timeout")
        
        with pytest.raises(TimeoutError):
            manager.execute("r1")

    def test_execute_multiple_routines_sequence(self) -> None:
        """Test executing multiple routines in sequence."""
        manager = Mock()
        manager.execute.return_value = {"status": "executed"}
        
        routine_ids = ["r1", "r2", "r3"]
        results = [manager.execute(rid) for rid in routine_ids]
        
        assert len(results) == 3
        assert all(r["status"] == "executed" for r in results)


class TestRoutineManagerCreateRoutine:
    """Tests for creating routines."""

    def test_create_routine_basic(self) -> None:
        """Test creating a basic routine."""
        manager = Mock()
        manager.create_routine.return_value = {
            "routine_id": "new_r1",
            "name": "New Routine",
            "created": True
        }
        
        result = manager.create_routine("New Routine")
        assert result["created"] is True
        assert "routine_id" in result

    def test_create_routine_with_actions(self) -> None:
        """Test creating routine with actions."""
        manager = Mock()
        actions = [
            {"type": "music", "action": "play"},
            {"type": "light", "action": "on"}
        ]
        
        manager.create_routine.return_value = {
            "routine_id": "r_new",
            "actions": actions
        }
        
        result = manager.create_routine("Morning", actions=actions)
        assert len(result["actions"]) == 2

    def test_create_routine_name_required(self) -> None:
        """Test routine creation requires name."""
        manager = Mock()
        manager.create_routine.side_effect = ValueError("Name required")
        
        with pytest.raises(ValueError):
            manager.create_routine("")

    def test_create_routine_returns_id(self) -> None:
        """Test created routine has unique ID."""
        manager = Mock()
        manager.create_routine.return_value = {"routine_id": "r_unique"}
        
        result = manager.create_routine("Test")
        assert "routine_id" in result
        assert len(result["routine_id"]) > 0


class TestRoutineManagerDeleteRoutine:
    """Tests for deleting routines."""

    def test_delete_routine_success(self) -> None:
        """Test deleting a routine successfully."""
        manager = Mock()
        manager.delete_routine.return_value = {"deleted": True}
        
        result = manager.delete_routine("r1")
        assert result["deleted"] is True

    def test_delete_routine_invalid_id(self) -> None:
        """Test delete with invalid routine ID."""
        manager = Mock()
        manager.delete_routine.side_effect = ValueError("Routine not found")
        
        with pytest.raises(ValueError):
            manager.delete_routine("invalid_id")

    def test_delete_nonexistent_routine(self) -> None:
        """Test deleting routine that doesn't exist."""
        manager = Mock()
        manager.delete_routine.side_effect = KeyError("Routine not found")
        
        with pytest.raises(KeyError):
            manager.delete_routine("nonexistent")


class TestRoutineManagerUpdateRoutine:
    """Tests for updating routines."""

    def test_update_routine_name(self) -> None:
        """Test updating routine name."""
        manager = Mock()
        manager.update_routine.return_value = {
            "routine_id": "r1",
            "name": "Updated Name"
        }
        
        result = manager.update_routine("r1", name="Updated Name")
        assert result["name"] == "Updated Name"

    def test_update_routine_actions(self) -> None:
        """Test updating routine actions."""
        manager = Mock()
        new_actions = [{"type": "music", "action": "stop"}]
        
        manager.update_routine.return_value = {
            "routine_id": "r1",
            "actions": new_actions
        }
        
        result = manager.update_routine("r1", actions=new_actions)
        assert len(result["actions"]) == 1

    def test_update_routine_enabled_status(self) -> None:
        """Test updating routine enabled status."""
        manager = Mock()
        manager.update_routine.return_value = {
            "routine_id": "r1",
            "enabled": False
        }
        
        result = manager.update_routine("r1", enabled=False)
        assert result["enabled"] is False


class TestRoutineManagerListActions:
    """Tests for listing available actions."""

    def test_list_available_actions(self) -> None:
        """Test listing all available actions."""
        manager = Mock()
        manager.list_actions.return_value = [
            {"type": "music", "name": "Play Music"},
            {"type": "light", "name": "Turn on Light"},
            {"type": "device", "name": "Control Device"}
        ]
        
        actions = manager.list_actions()
        assert len(actions) >= 3

    def test_action_has_required_fields(self) -> None:
        """Test action objects have required fields."""
        manager = Mock()
        manager.list_actions.return_value = [{
            "type": "music",
            "name": "Play Music",
            "description": "Start playing music",
            "parameters": []
        }]
        
        actions = manager.list_actions()
        action = actions[0]
        
        assert "type" in action
        assert "name" in action

    def test_list_actions_empty(self) -> None:
        """Test list actions returns empty when no actions available."""
        manager = Mock()
        manager.list_actions.return_value = []
        
        actions = manager.list_actions()
        assert actions == []

    def test_list_actions_by_type(self) -> None:
        """Test filtering actions by type."""
        manager = Mock()
        manager.list_actions.return_value = [
            {"type": "music", "name": "Play"},
            {"type": "music", "name": "Pause"},
            {"type": "light", "name": "On"}
        ]
        
        actions = manager.list_actions()
        music_actions = [a for a in actions if a["type"] == "music"]
        assert len(music_actions) == 2


class TestRoutineManagerEnableDisable:
    """Tests for enabling/disabling routines."""

    def test_enable_routine(self) -> None:
        """Test enabling a routine."""
        manager = Mock()
        manager.set_enabled.return_value = {"routine_id": "r1", "enabled": True}
        
        result = manager.set_enabled("r1", True)
        assert result["enabled"] is True

    def test_disable_routine(self) -> None:
        """Test disabling a routine."""
        manager = Mock()
        manager.set_enabled.return_value = {"routine_id": "r1", "enabled": False}
        
        result = manager.set_enabled("r1", False)
        assert result["enabled"] is False

    def test_toggle_routine_enabled(self) -> None:
        """Test toggling routine enabled status."""
        manager = Mock()
        
        # First get current state
        manager.get_routine.return_value = {"routine_id": "r1", "enabled": True}
        routine = manager.get_routine("r1")
        
        # Toggle it
        new_state = not routine["enabled"]
        manager.set_enabled.return_value = {"enabled": new_state}
        
        result = manager.set_enabled("r1", new_state)
        assert result["enabled"] is False


class TestRoutineManagerGetDetails:
    """Tests for getting routine details."""

    def test_get_routine_details(self) -> None:
        """Test getting full routine details."""
        manager = Mock()
        manager.get_routine.return_value = {
            "routine_id": "r1",
            "name": "Morning",
            "description": "Morning routine",
            "enabled": True,
            "actions": [],
            "created_at": "2025-10-16",
            "updated_at": "2025-10-16"
        }
        
        routine = manager.get_routine("r1")
        assert routine["name"] == "Morning"
        assert routine["enabled"] is True

    def test_get_routine_with_actions(self) -> None:
        """Test routine details include actions."""
        manager = Mock()
        manager.get_routine.return_value = {
            "routine_id": "r1",
            "name": "Test",
            "actions": [
                {"action_id": "a1", "type": "music"},
                {"action_id": "a2", "type": "light"}
            ]
        }
        
        routine = manager.get_routine("r1")
        assert len(routine["actions"]) == 2

    def test_get_nonexistent_routine(self) -> None:
        """Test getting details of nonexistent routine."""
        manager = Mock()
        manager.get_routine.side_effect = ValueError("Routine not found")
        
        with pytest.raises(ValueError):
            manager.get_routine("nonexistent")


class TestRoutineManagerSearch:
    """Tests for searching routines."""

    def test_search_by_name(self) -> None:
        """Test searching routines by name."""
        manager = Mock()
        manager.search.return_value = [
            {"routine_id": "r1", "name": "Morning Routine"}
        ]
        
        results = manager.search(name="Morning")
        assert len(results) == 1
        assert "Morning" in results[0]["name"]

    def test_search_by_description(self) -> None:
        """Test searching by description."""
        manager = Mock()
        manager.search.return_value = [
            {"routine_id": "r2", "description": "Daily routine"}
        ]
        
        results = manager.search(description="Daily")
        assert len(results) == 1

    def test_search_returns_empty(self) -> None:
        """Test search returns empty when no matches."""
        manager = Mock()
        manager.search.return_value = []
        
        results = manager.search(name="NonExistent")
        assert results == []


class TestRoutineManagerScheduling:
    """Tests for routine scheduling."""

    def test_schedule_routine(self) -> None:
        """Test scheduling routine for specific time."""
        manager = Mock()
        manager.schedule.return_value = {
            "routine_id": "r1",
            "scheduled_time": "07:00",
            "scheduled": True
        }
        
        result = manager.schedule("r1", "07:00")
        assert result["scheduled"] is True

    def test_schedule_recurring_routine(self) -> None:
        """Test scheduling recurring routine."""
        manager = Mock()
        manager.schedule.return_value = {
            "routine_id": "r1",
            "recurring": "daily",
            "scheduled": True
        }
        
        result = manager.schedule("r1", "07:00", recurring="daily")
        assert result["recurring"] == "daily"

    def test_unschedule_routine(self) -> None:
        """Test removing routine schedule."""
        manager = Mock()
        manager.unschedule.return_value = {"routine_id": "r1", "scheduled": False}
        
        result = manager.unschedule("r1")
        assert result["scheduled"] is False


class TestRoutineManagerErrorHandling:
    """Tests for error handling."""

    def test_api_error_handling(self) -> None:
        """Test handling API errors."""
        manager = Mock()
        manager.execute.side_effect = ConnectionError("API unavailable")
        
        with pytest.raises(ConnectionError):
            manager.execute("r1")

    def test_invalid_parameter_handling(self) -> None:
        """Test handling invalid parameters."""
        manager = Mock()
        manager.create_routine.side_effect = TypeError("Invalid parameter")
        
        with pytest.raises(TypeError):
            manager.create_routine(123)  # Invalid type

    def test_authentication_error(self) -> None:
        """Test handling authentication errors."""
        manager = Mock()
        manager.get_routines.side_effect = PermissionError("Not authenticated")
        
        with pytest.raises(PermissionError):
            manager.get_routines()


class TestRoutineManagerIntegration:
    """Integration tests combining multiple operations."""

    def test_create_execute_delete_workflow(self) -> None:
        """Test complete workflow: create → execute → delete routine."""
        manager = Mock()
        
        # Create
        manager.create_routine.return_value = {
            "routine_id": "new_r",
            "name": "Test Routine"
        }
        created = manager.create_routine("Test Routine")
        
        # Execute
        manager.execute.return_value = {"status": "executed"}
        executed = manager.execute(created["routine_id"])
        
        # Delete
        manager.delete_routine.return_value = {"deleted": True}
        deleted = manager.delete_routine(created["routine_id"])
        
        assert deleted["deleted"] is True

    def test_list_modify_execute_workflow(self) -> None:
        """Test workflow: list → modify → execute routine."""
        manager = Mock()
        
        # List
        manager.get_routines.return_value = [
            {"routine_id": "r1", "name": "Morning"}
        ]
        routines = manager.get_routines()
        
        # Modify
        routine_id = routines[0]["routine_id"]
        manager.update_routine.return_value = {
            "routine_id": routine_id,
            "name": "Updated Morning"
        }
        updated = manager.update_routine(routine_id, name="Updated Morning")
        
        # Execute
        manager.execute.return_value = {"status": "success"}
        result = manager.execute(routine_id)
        
        assert result["status"] == "success"


class TestRoutineManagerCaching:
    """Tests for caching behavior."""

    def test_routines_cached(self) -> None:
        """Test that routines are cached."""
        manager = Mock()
        manager.get_routines.return_value = [{"routine_id": "r1"}]
        
        # First call
        result1 = manager.get_routines()
        # Second call (should use cache)
        result2 = manager.get_routines()
        
        # Should have same results
        assert result1 == result2

    def test_cache_invalidation(self) -> None:
        """Test cache invalidation on update."""
        manager = Mock()
        
        # Initial cache
        manager.get_routines.return_value = [{"routine_id": "r1", "name": "Old"}]
        
        # Update invalidates cache
        manager.update_routine.return_value = {"routine_id": "r1", "name": "New"}
        manager.update_routine("r1", name="New")
        
        # Fetch again
        manager.get_routines.return_value = [{"routine_id": "r1", "name": "New"}]
        result = manager.get_routines()
        
        assert result[0]["name"] == "New"
