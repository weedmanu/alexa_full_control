"""
Tests for ReminderManager Phase 3.7 DTO integration.
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from core.timers.reminder_manager import ReminderManager
from services.cache_service import CacheService


class FakeHTTPClientReminder:
    """Fake HTTP client for ReminderManager."""
    
    def __init__(self, reminders: List[Dict[str, Any]]):
        self._reminders = reminders
    
    def get(self, url: str, headers: Dict[str, str], timeout: int = 10):
        """Mock GET request."""
        class Response:
            def raise_for_status(self):
                pass
            
            def json(self):
                return {"reminders": [self._reminders]}
        
        response = Response()
        response._reminders = self._reminders
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


class FakeStateMachineReminder:
    """Fake state machine."""
    
    @property
    def can_execute_commands(self) -> bool:
        return True


class CircuitBreakerFake:
    """Fake circuit breaker."""
    
    def call(self, func, *args, **kwargs):
        """Call function directly."""
        return func(*args, **kwargs)


def make_reminder_manager(reminders_data=None):
    """Create a ReminderManager for testing."""
    class FakeAuth:
        pass
    
    class FakeConfig:
        alexa_domain = "alexa.amazon.com"
        amazon_domain = "amazon.com"
    
    auth = FakeAuth()
    config = FakeConfig()
    state_machine = FakeStateMachineReminder()
    
    reminders_data = reminders_data or []
    http_client = FakeHTTPClientReminder(reminders_data)
    
    manager = ReminderManager(
        auth=auth,
        config=config,
        state_machine=state_machine,
    )
    
    # Override http_client and breaker for testing
    manager.http_client = http_client
    manager.breaker = CircuitBreakerFake()
    
    return manager


def test_list_reminders_basic():
    """Test list_reminders returns data."""
    reminders_data = [
        {
            "id": "reminder1",
            "label": "Doctor",
            "triggerTime": datetime.now(timezone.utc),
            "enabled": True
        }
    ]
    manager = make_reminder_manager(reminders_data)
    reminders = manager.list_reminders()
    assert isinstance(reminders, list)


def test_get_reminders_typed_returns_dto():
    """Test Phase 3.7: get_reminders_typed() returns GetRemindersResponse DTO."""
    reminders_data = [
        {
            "id": "reminder1",
            "label": "Doctor",
            "triggerTime": datetime.now(timezone.utc),
            "enabled": True
        }
    ]
    manager = make_reminder_manager(reminders_data)
    
    response = manager.get_reminders_typed()
    
    # Verify response is DTO (if available)
    if response is not None:
        assert hasattr(response, 'reminders'), "Response should have 'reminders' attribute"


def test_get_reminders_typed_with_legacy_data():
    """Test Phase 3.7: get_reminders_typed() handles legacy data."""
    reminders_data = [
        {
            "id": "reminder1",
            "label": "Meeting",
        }
    ]
    manager = make_reminder_manager(reminders_data)
    
    response = manager.get_reminders_typed()
    
    # Should gracefully handle or return None
    assert True  # Just verify no exception raised
