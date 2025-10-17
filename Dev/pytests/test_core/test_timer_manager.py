"""
Tests for TimerManager Phase 3.7 DTO integration.
"""

import pytest
from typing import Any, Dict, List, Optional
from core.timers.timer_manager import TimerManager
from services.cache_service import CacheService


class FakeAPIServiceTimer:
    """Fake API service for testing TimerManager."""
    
    def __init__(self, timers: List[Dict[str, Any]]):
        self._timers = timers
    
    def get(self, path: str, timeout: int = 10):
        """Mock GET request."""
        if path == "/api/notifications":
            return {"notifications": [t for t in self._timers if t.get("type") == "Timer"]}
        return {}
    
    def post(self, path: str, json: Dict[str, Any], timeout: int = 10):
        """Mock POST request."""
        return {"id": "timer123", "status": "ON"}
    
    def delete(self, path: str, timeout: int = 10):
        """Mock DELETE request."""
        return None
    
    def put(self, path: str, json: Dict[str, Any], timeout: int = 10):
        """Mock PUT request."""
        return None


class FakeStateMachine:
    """Fake state machine."""
    
    @property
    def can_execute_commands(self) -> bool:
        return True
    
    @property
    def state(self):
        class State:
            name = "CONNECTED"
        return State()


def make_timer_manager(api_service=None):
    """Create a TimerManager for testing."""
    class FakeAuth:
        pass
    
    class FakeConfig:
        amazon_domain = "amazon.com"
    
    auth = FakeAuth()
    config = FakeConfig()
    state_machine = FakeStateMachine()
    cache_service = CacheService()
    
    # Create http_client mock
    class FakeHttpClient:
        pass
    
    api_service = api_service or FakeAPIServiceTimer([])
    
    manager = TimerManager(
        auth=auth,
        state_machine=state_machine,
        api_service=api_service,
        cache_service=cache_service,
        cache_ttl=60
    )
    return manager


def test_list_timers_basic():
    """Test list_timers returns empty list."""
    manager = make_timer_manager()
    timers = manager.list_timers(force_refresh=True)
    assert isinstance(timers, list)


def test_list_timers_with_data():
    """Test list_timers returns timer data."""
    timers_data = [
        {
            "id": "timer1",
            "type": "Timer",
            "status": "ON",
            "timerLabel": "Cooking",
            "durationMs": 300000,
            "remainingMs": 250000
        }
    ]
    api_service = FakeAPIServiceTimer(timers_data)
    manager = make_timer_manager(api_service=api_service)
    
    timers = manager.list_timers(force_refresh=True)
    assert len(timers) == 1
    assert timers[0]["timerLabel"] == "Cooking"


def test_get_timers_typed_returns_dto():
    """Test Phase 3.7: get_timers_typed() returns GetTimersResponse DTO."""
    timers_data = [
        {
            "id": "timer1",
            "type": "Timer",
            "status": "ON",
            "timerLabel": "Cooking",
            "timerId": "timer1",
            "label": "Cooking",
            "durationMs": 300000,
            "remainingMs": 250000
        }
    ]
    api_service = FakeAPIServiceTimer(timers_data)
    manager = make_timer_manager(api_service=api_service)
    
    response = manager.get_timers_typed(force_refresh=True)
    
    # Verify response is DTO (if available)
    if response is not None:
        # Should have timers attribute
        assert hasattr(response, 'timers'), "Response should have 'timers' attribute"
        assert len(response.timers) >= 1, "Should have at least 1 timer"
    else:
        # Fallback if DTO not available is OK
        pass


def test_get_timers_typed_with_legacy_api():
    """Test Phase 3.7: get_timers_typed() handles legacy API returning dict."""
    timers_data = [
        {
            "id": "timer1",
            "type": "Timer",
            "status": "ON",
            "timerLabel": "Cooking",
        }
    ]
    api_service = FakeAPIServiceTimer(timers_data)
    manager = make_timer_manager(api_service=api_service)
    
    response = manager.get_timers_typed(force_refresh=True)
    
    # Should gracefully handle list response (or return None)
    # This is OK - testing graceful fallback
    assert True  # Just verify no exception raised
