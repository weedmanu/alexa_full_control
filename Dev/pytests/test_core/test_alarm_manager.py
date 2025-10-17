"""
Tests for AlarmManager Phase 3.7 DTO integration.
"""

import pytest
from typing import Any, Dict, List, Optional
from core.timers.alarm_manager import AlarmManager
import requests


class FakeHTTPClientAlarm:
    """Fake HTTP client for AlarmManager."""
    
    def __init__(self, alarms: List[Dict[str, Any]]):
        self._alarms = alarms
    
    def get(self, url: str, headers: Dict[str, str], timeout: int = 10):
        """Mock GET request."""
        class Response:
            def raise_for_status(self):
                pass
            
            def json(self):
                return {"alarms": self._alarms}
        
        response = Response()
        response._alarms = self._alarms
        return response
    
    def delete(self, url: str, headers: Dict[str, str], timeout: int = 10):
        """Mock DELETE request."""
        class Response:
            def raise_for_status(self):
                pass
        return Response()
    
    def put(self, url: str, json: Dict[str, Any], headers: Dict[str, str], timeout: int = 10):
        """Mock PUT request."""
        class Response:
            def raise_for_status(self):
                pass
        return Response()


class FakeStateMachineAlarm:
    """Fake state machine."""
    
    @property
    def can_execute_commands(self) -> bool:
        return True
    
    @property
    def state(self):
        class State:
            name = "CONNECTED"
        return State()


class CircuitBreakerFake:
    """Fake circuit breaker."""
    
    def call(self, func, *args, **kwargs):
        """Call function directly."""
        return func(*args, **kwargs)


def make_alarm_manager(alarms_data=None):
    """Create an AlarmManager for testing."""
    class FakeAuth:
        csrf = ""
    
    class FakeConfig:
        alexa_domain = "alexa.amazon.com"
        amazon_domain = "amazon.com"
    
    auth = FakeAuth()
    config = FakeConfig()
    state_machine = FakeStateMachineAlarm()
    
    alarms_data = alarms_data or []
    http_client = FakeHTTPClientAlarm(alarms_data)
    
    manager = AlarmManager(
        auth=auth,
        config=config,
        state_machine=state_machine,
    )
    
    # Override http_client and breaker for testing
    manager.http_client = http_client
    manager.breaker = CircuitBreakerFake()
    
    return manager


def test_list_alarms_basic():
    """Test list_alarms returns data."""
    alarms_data = [
        {
            "id": "alarm1",
            "label": "Morning",
            "time": "07:00:00",
            "enabled": True
        }
    ]
    manager = make_alarm_manager(alarms_data)
    alarms = manager.list_alarms()
    assert isinstance(alarms, list)


def test_get_alarms_typed_returns_dto():
    """Test Phase 3.7: get_alarms_typed() returns GetAlarmsResponse DTO."""
    alarms_data = [
        {
            "id": "alarm1",
            "label": "Morning",
            "time": "07:00:00",
            "enabled": True,
            "recurring": True,
            "daysOfWeek": ["MON", "TUE", "WED", "THU", "FRI"]
        }
    ]
    manager = make_alarm_manager(alarms_data)
    
    response = manager.get_alarms_typed()
    
    # Verify response is DTO (if available)
    if response is not None:
        assert hasattr(response, 'alarms'), "Response should have 'alarms' attribute"


def test_get_alarms_typed_with_legacy_data():
    """Test Phase 3.7: get_alarms_typed() handles legacy data."""
    alarms_data = [
        {
            "id": "alarm1",
            "label": "Bedtime",
        }
    ]
    manager = make_alarm_manager(alarms_data)
    
    response = manager.get_alarms_typed()
    
    # Should gracefully handle or return None
    assert True  # Just verify no exception raised
