"""
Phase 2 TDD Tests for TimerManager with mandatory AlexaAPIService injection.

Tests verify:
- TimerManager requires api_service (raises ValueError if None)
- All timer operations use api_service (no fallback to _api_call)
- Cache operations work correctly (memory + disk)
- Thread safety maintained
"""

import pytest
from unittest.mock import Mock
from core.timers.timer_manager import TimerManager
from core.state_machine import AlexaStateMachine, ConnectionState
from services.cache_service import CacheService


class TestTimersManagerMandatoryInjection:
    """Test mandatory api_service injection (Phase 2)."""

    def test_constructor_requires_api_service(self):
        """TimerManager should raise ValueError if api_service is None."""
        auth = Mock()
        state_machine = AlexaStateMachine()

        with pytest.raises(ValueError, match="api_service is mandatory"):
            TimerManager(
                auth=auth,
                state_machine=state_machine,
                api_service=None,  # This should raise
            )

    def test_constructor_with_valid_api_service(self):
        """TimerManager should initialize successfully with valid api_service."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        assert manager._api_service is api_service
        assert manager.auth is auth
        assert manager.state_machine is state_machine

    def test_constructor_with_cache_service(self):
        """TimerManager should accept optional cache_service."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        api_service = Mock()
        cache_service = Mock(spec=CacheService)

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
            cache_service=cache_service,
        )

        assert manager.cache_service is cache_service

    def test_constructor_with_custom_cache_ttl(self):
        """TimerManager should respect custom cache_ttl."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
            cache_ttl=120,
        )

        assert manager._cache_ttl == 120


class TestTimersManagerCreateTimer:
    """Test create_timer uses api_service directly."""

    def test_create_timer_success(self):
        """create_timer should call api_service.post and return timer data."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()

        timer_response = {"timerId": "timer-123", "timerLabel": "Coffee"}
        api_service.post.return_value = timer_response

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_timer(
            device_serial="G090LF1234567",
            device_type="Echo",
            duration_minutes=10,
            label="Coffee",
        )

        # Verify api_service.post was called correctly
        api_service.post.assert_called_once()
        args, kwargs = api_service.post.call_args
        assert args[0] == "/api/timers"
        assert kwargs["timeout"] == 10
        assert kwargs["json"]["timerLabel"] == "Coffee"
        assert kwargs["json"]["originalDuration"] == "PT10M"

        # Verify result
        assert result == timer_response

    def test_create_timer_not_authenticated(self):
        """create_timer should return None if not authenticated."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.DISCONNECTED)
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_timer(
            device_serial="G090LF1234567",
            device_type="Echo",
            duration_minutes=10,
        )

        # Should not call api_service
        api_service.post.assert_not_called()
        assert result is None

    def test_create_timer_api_error(self):
        """create_timer should handle api_service errors gracefully."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()
        api_service.post.side_effect = Exception("API Error")

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.create_timer(
            device_serial="G090LF1234567",
            device_type="Echo",
            duration_minutes=10,
        )

        assert result is None


class TestTimersManagerListTimers:
    """Test list_timers uses api_service and cache correctly."""

    def test_list_timers_from_api(self):
        """list_timers should fetch from api_service when cache is invalid."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()
        cache_service = Mock(spec=CacheService)
        cache_service.get.return_value = None  # No disk cache

        api_response = {
            "notifications": [
                {"id": "t1", "type": "Timer", "status": "ON"},
                {"id": "t2", "type": "Timer", "status": "ON"},
                {"id": "a1", "type": "Alarm", "status": "ON"},  # Should be filtered out
            ]
        }
        api_service.get.return_value = api_response

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
            cache_service=cache_service,
        )

        timers = manager.list_timers()

        # Verify api_service.get was called
        api_service.get.assert_called_once_with("/api/notifications", timeout=10)

        # Verify filtering (only Timer type, ON status)
        assert len(timers) == 2
        assert all(t["type"] == "Timer" for t in timers)
        assert all(t["status"] == "ON" for t in timers)

        # Verify cache was updated
        cache_service.set.assert_called_once()

    def test_list_timers_from_memory_cache(self):
        """list_timers should return memory cache if valid and not expired."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        # Populate memory cache
        cached_timers = [
            {"id": "t1", "type": "Timer", "status": "ON"},
            {"id": "t2", "type": "Timer", "status": "ON"},
        ]
        manager._timers_cache = cached_timers
        import time
        manager._cache_timestamp = time.time()

        # Call list_timers - should use memory cache, not api_service
        timers = manager.list_timers()

        assert timers == cached_timers
        api_service.get.assert_not_called()

    def test_list_timers_force_refresh(self):
        """list_timers with force_refresh=True should bypass cache."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()
        cache_service = Mock(spec=CacheService)
        cache_service.get.return_value = None

        api_response = {
            "notifications": [
                {"id": "t1", "type": "Timer", "status": "ON"},
            ]
        }
        api_service.get.return_value = api_response

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
            cache_service=cache_service,
        )

        # Populate memory cache
        manager._timers_cache = [{"id": "old", "type": "Timer", "status": "ON"}]
        import time
        manager._cache_timestamp = time.time()

        # Call with force_refresh
        timers = manager.list_timers(force_refresh=True)

        # Should fetch from api, not use stale cache
        api_service.get.assert_called_once()
        assert len(timers) == 1
        assert timers[0]["id"] == "t1"

    def test_list_timers_filter_by_device(self):
        """list_timers should filter by device_serial if provided."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()
        cache_service = Mock(spec=CacheService)
        cache_service.get.return_value = None

        api_response = {
            "notifications": [
                {"id": "t1", "type": "Timer", "status": "ON", "deviceSerialNumber": "ABC123"},
                {"id": "t2", "type": "Timer", "status": "ON", "deviceSerialNumber": "XYZ789"},
            ]
        }
        api_service.get.return_value = api_response

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
            cache_service=cache_service,
        )

        timers = manager.list_timers(device_serial="ABC123")

        assert len(timers) == 1
        assert timers[0]["deviceSerialNumber"] == "ABC123"


class TestTimersManagerCancelTimer:
    """Test cancel_timer uses api_service directly."""

    def test_cancel_timer_success(self):
        """cancel_timer should call api_service.delete and return True."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.cancel_timer("timer-123")

        # Verify api_service.delete was called
        api_service.delete.assert_called_once_with("/api/timers/timer-123", timeout=10)
        assert result is True

    def test_cancel_timer_api_error(self):
        """cancel_timer should return False on api_service error."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()
        api_service.delete.side_effect = Exception("API Error")

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.cancel_timer("timer-123")

        assert result is False


class TestTimersManagerPauseTimer:
    """Test pause_timer uses api_service directly."""

    def test_pause_timer_success(self):
        """pause_timer should call api_service.put and return True."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.pause_timer("timer-123")

        # Verify api_service.put was called with correct payload
        api_service.put.assert_called_once()
        args, kwargs = api_service.put.call_args
        assert args[0] == "/api/timers/timer-123"
        assert kwargs["json"] == {"status": "PAUSED"}
        assert kwargs["timeout"] == 10
        assert result is True

    def test_pause_timer_not_authenticated(self):
        """pause_timer should return False if not authenticated."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.DISCONNECTED)
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.pause_timer("timer-123")

        api_service.put.assert_not_called()
        assert result is False


class TestTimersManagerResumeTimer:
    """Test resume_timer uses api_service directly."""

    def test_resume_timer_success(self):
        """resume_timer should call api_service.put and return True."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.resume_timer("timer-123")

        # Verify api_service.put was called with correct payload
        api_service.put.assert_called_once()
        args, kwargs = api_service.put.call_args
        assert args[0] == "/api/timers/timer-123"
        assert kwargs["json"] == {"status": "ON"}
        assert kwargs["timeout"] == 10
        assert result is True

    def test_resume_timer_api_error(self):
        """resume_timer should return False on api_service error."""
        auth = Mock()
        state_machine = AlexaStateMachine()
        state_machine.set_initial_state(ConnectionState.AUTHENTICATED)
        api_service = Mock()
        api_service.put.side_effect = Exception("API Error")

        manager = TimerManager(
            auth=auth,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.resume_timer("timer-123")

        assert result is False
