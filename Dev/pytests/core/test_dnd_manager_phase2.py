"""
Phase 2 Tests: DNDManager - Mandatory AlexaAPIService Injection
Tests that DNDManager correctly injects and uses AlexaAPIService
without fallbacks to _api_call.
"""

from unittest.mock import Mock
import pytest

from core.dnd_manager import DNDManager
from core.state_machine import AlexaStateMachine


class TestDNDManagerMandatoryInjection:
    """Test that api_service injection is mandatory."""

    def test_constructor_raises_without_api_service(self):
        """Constructor should raise ValueError if api_service is None."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = AlexaStateMachine()

        with pytest.raises(ValueError, match="api_service is mandatory"):
            DNDManager(
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
            DNDManager(auth=auth, config=config, state_machine=state_machine)

    def test_constructor_succeeds_with_api_service(self):
        """Constructor should succeed when api_service is provided."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = DNDManager(
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

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        assert manager._api_service is not None
        assert manager._api_service is api_service


class TestDNDManagerGetDNDStatus:
    """Test get_dnd_status() uses api_service directly."""

    def test_get_dnd_status_calls_api_service(self):
        """get_dnd_status() should call api_service.get directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {
            "doNotDisturbDeviceStatusList": [
                {"deviceSerialNumber": "device123", "enabled": True},
                {"deviceSerialNumber": "device456", "enabled": False},
            ]
        }

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_dnd_status("device123")

        api_service.get.assert_called_once_with("/api/dnd/status")
        assert result is not None
        assert result["deviceSerialNumber"] == "device123"
        assert result["enabled"] is True

    def test_get_dnd_status_handles_exception(self):
        """get_dnd_status() should return None on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.side_effect = Exception("API Error")

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_dnd_status("device123")
        assert result is None

    def test_get_dnd_status_respects_state_machine(self):
        """get_dnd_status() should return None if commands not allowed."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_dnd_status("device123")
        assert result is None
        api_service.get.assert_not_called()


class TestDNDManagerEnableDND:
    """Test enable_dnd() uses api_service directly."""

    def test_enable_dnd_calls_api_service(self):
        """enable_dnd() should call api_service.put directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.return_value = {"status": "ok"}

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.enable_dnd("device123", "ALEXA_DEVICE")

        api_service.put.assert_called_once()
        call_args = api_service.put.call_args
        assert call_args[0][0] == "/api/dnd/status"
        assert call_args[1]["payload"]["enabled"] is True
        assert result is True

    def test_enable_dnd_handles_exception(self):
        """enable_dnd() should return False on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.side_effect = Exception("API Error")

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.enable_dnd("device123", "ALEXA_DEVICE")
        assert result is False


class TestDNDManagerDisableDND:
    """Test disable_dnd() uses api_service directly."""

    def test_disable_dnd_calls_api_service(self):
        """disable_dnd() should call api_service.put directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.return_value = {"status": "ok"}

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.disable_dnd("device123", "ALEXA_DEVICE")

        api_service.put.assert_called_once()
        call_args = api_service.put.call_args
        assert call_args[0][0] == "/api/dnd/status"
        assert call_args[1]["payload"]["enabled"] is False
        assert result is True

    def test_disable_dnd_handles_exception(self):
        """disable_dnd() should return False on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.side_effect = Exception("API Error")

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.disable_dnd("device123", "ALEXA_DEVICE")
        assert result is False


class TestDNDManagerSetDNDSchedule:
    """Test set_dnd_schedule() uses api_service directly."""

    def test_set_dnd_schedule_calls_api_service(self):
        """set_dnd_schedule() should call api_service.put directly."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.return_value = {"status": "ok"}

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_dnd_schedule("device123", "ALEXA_DEVICE", 22, 0, 8, 0)

        api_service.put.assert_called_once()
        call_args = api_service.put.call_args
        assert call_args[0][0] == "/api/dnd/device-status-list"
        payload = call_args[1]["payload"]
        assert payload["deviceSerialNumber"] == "device123"
        assert payload["timeWindows"][0]["startTime"] == "22:00"
        assert payload["timeWindows"][0]["endTime"] == "08:00"
        assert result is True

    def test_set_dnd_schedule_handles_exception(self):
        """set_dnd_schedule() should return False on exception."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.side_effect = Exception("API Error")

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_dnd_schedule("device123", "ALEXA_DEVICE", 22, 0, 8, 0)
        assert result is False

    def test_set_dnd_schedule_respects_state_machine(self):
        """set_dnd_schedule() should return False if commands not allowed."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_dnd_schedule("device123", "ALEXA_DEVICE", 22, 0, 8, 0)
        assert result is False
        api_service.put.assert_not_called()


class TestDNDManagerNoFallbacks:
    """Verify no fallback patterns exist to _api_call."""

    def test_no_api_call_usage(self):
        """Verify that operations use api_service, not _api_call."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {
            "doNotDisturbDeviceStatusList": [
                {"deviceSerialNumber": "device123", "enabled": True}
            ]
        }

        manager = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_dnd_status("device123")
        assert result is not None
        api_service.get.assert_called_once()
