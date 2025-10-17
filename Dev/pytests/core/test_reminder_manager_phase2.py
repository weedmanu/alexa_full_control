"""
Phase 2 Tests: ReminderManager - Mandatory AlexaAPIService Injection
Tests that ReminderManager correctly injects and uses AlexaAPIService
without fallbacks to _api_call.
"""

from unittest.mock import Mock
import pytest

from core.reminders.reminder_manager import ReminderManager
from core.state_machine import AlexaStateMachine
from services.cache_service import CacheService


class TestReminderManagerMandatoryInjection:
    """Test that api_service injection is mandatory."""

    def test_constructor_raises_without_api_service(self):
        """Constructor should raise ValueError if api_service is None."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = AlexaStateMachine()

        with pytest.raises(ValueError, match="api_service is mandatory"):
            ReminderManager(
                auth=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )

    def test_constructor_requires_explicit_api_service(self):
        """Constructor should require explicitly passed api_service."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = AlexaStateMachine()

        with pytest.raises(ValueError):
            ReminderManager(auth=auth, config=config, state_machine=state_machine)

    def test_constructor_succeeds_with_api_service(self):
        """Constructor should succeed when api_service is provided."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        assert manager._api_service is api_service

    def test_api_service_not_optional(self):
        """api_service should not be optional in Phase 2."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        assert manager._api_service is not None
        assert manager._api_service is api_service


class TestReminderManagerCreateReminder:
    """Test create_reminder() uses api_service directly."""

    def test_create_reminder_calls_api_service(self):
        """create_reminder() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.return_value = {"id": "reminder_123", "label": "Test"}

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_reminder("device123", "My reminder", "2025-10-18T10:00:00")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[0][0] == "/api/notifications"
        assert call_args[1]["payload"]["label"] == "My reminder"
        assert result is not None

    def test_create_reminder_handles_exception(self):
        """create_reminder() should return None on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.side_effect = Exception("API Error")

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_reminder("device123", "My reminder", "2025-10-18T10:00:00")
        assert result is None

    def test_create_reminder_respects_state_machine(self):
        """create_reminder() should return None if commands not allowed."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_reminder("device123", "My reminder", "2025-10-18T10:00:00")
        assert result is None
        api_service.post.assert_not_called()


class TestReminderManagerCreateRecurringReminder:
    """Test create_recurring_reminder() uses api_service directly."""

    def test_create_recurring_reminder_calls_api_service(self):
        """create_recurring_reminder() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.return_value = {"id": "reminder_456"}

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_recurring_reminder("device123", "Daily reminder", "daily", "09:00")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[0][0] == "/api/notifications"
        assert call_args[1]["payload"]["recurrence"] == "DAILY"
        assert result is not None

    def test_create_recurring_reminder_handles_exception(self):
        """create_recurring_reminder() should return None on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.side_effect = Exception("API Error")

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_recurring_reminder("device123", "Daily reminder", "daily", "09:00")
        assert result is None


class TestReminderManagerGetReminders:
    """Test get_reminders() uses api_service directly."""

    def test_get_reminders_calls_api_service(self):
        """get_reminders() should call api_service.get directly for cache refresh."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        cache_service = Mock(spec=CacheService)
        cache_service.get.return_value = None
        api_service = Mock()
        api_service.get.return_value = {
            "notifications": [
                {"id": "1", "type": "Reminder", "label": "Reminder 1"},
                {"id": "2", "type": "Reminder", "label": "Reminder 2"},
            ]
        }

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            cache_service=cache_service,
            api_service=api_service,
        )

        result = manager.get_reminders()

        api_service.get.assert_called()
        assert len(result) == 2
        assert result[0]["label"] == "Reminder 1"

    def test_get_reminders_respects_state_machine(self):
        """get_reminders() should return empty list if commands not allowed."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_reminders()
        assert result == []
        api_service.get.assert_not_called()


class TestReminderManagerDeleteReminder:
    """Test delete_reminder() uses api_service directly."""

    def test_delete_reminder_calls_api_service(self):
        """delete_reminder() should call api_service.delete directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.delete_reminder("reminder_123")

        api_service.delete.assert_called_once_with("/api/notifications/reminder_123")
        assert result is True

    def test_delete_reminder_handles_exception(self):
        """delete_reminder() should return False on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.delete.side_effect = Exception("API Error")

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.delete_reminder("reminder_123")
        assert result is False

    def test_delete_reminder_respects_state_machine(self):
        """delete_reminder() should return False if commands not allowed."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.delete_reminder("reminder_123")
        assert result is False
        api_service.delete.assert_not_called()


class TestReminderManagerCompleteReminder:
    """Test complete_reminder() uses api_service directly."""

    def test_complete_reminder_calls_api_service(self):
        """complete_reminder() should call api_service.put directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.complete_reminder("reminder_123")

        api_service.put.assert_called_once()
        call_args = api_service.put.call_args
        assert call_args[0][0] == "/api/notifications/reminder_123"
        assert call_args[1]["payload"]["status"] == "COMPLETED"
        assert result is True

    def test_complete_reminder_handles_exception(self):
        """complete_reminder() should return False on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.side_effect = Exception("API Error")

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.complete_reminder("reminder_123")
        assert result is False

    def test_complete_reminder_respects_state_machine(self):
        """complete_reminder() should return False if commands not allowed."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.complete_reminder("reminder_123")
        assert result is False
        api_service.put.assert_not_called()


class TestReminderManagerNoFallbacks:
    """Verify no fallback patterns exist to _api_call."""

    def test_no_api_call_usage(self):
        """Verify that operations use api_service, not _api_call."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.return_value = {"id": "reminder_123"}

        manager = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_reminder("device123", "Test", "2025-10-18T10:00:00")
        assert result is not None
        api_service.post.assert_called_once()
