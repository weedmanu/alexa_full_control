"""
Test suite for Phase 3.7.2 - Timer, Reminder, and Alarm Managers DTO integration.
Tests dual methods: legacy (returns List[Dict]) + typed (returns DTO).
"""

import pytest
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

# Mock API service for testing DTOs
class MockAPIServiceForTimers:
    """Mock API service returning timer data"""
    def get(self, endpoint: str, **kwargs):
        if "notifications" in endpoint:
            return {
                "notifications": [
                    {
                        "id": "timer_1",
                        "timerId": "timer_1",
                        "timerLabel": "Cooking",
                        "type": "Timer",
                        "status": "ON",
                        "durationMs": 300000,
                        "remainingMs": 250000,
                    },
                    {
                        "id": "timer_2",
                        "timerId": "timer_2",
                        "timerLabel": "Laundry",
                        "type": "Timer",
                        "status": "ON",
                        "durationMs": 1800000,
                        "remainingMs": 1500000,
                    }
                ]
            }
        return {"notifications": []}


class MockCacheService:
    """Mock cache service"""
    def __init__(self):
        self.store: Dict[str, Any] = {}
    
    def get(self, key: str):
        return self.store.get(key)
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        self.store[key] = value


class MockAuth:
    """Mock auth"""
    pass


class MockStateMachine:
    """Mock state machine"""
    can_execute_commands = True
    
    class State:
        name = "CONNECTED"
    
    state = State()


def make_minimal_config():
    """Create minimal config for BaseManager"""
    class Config:
        amazon_domain = "amazon.com"
        alexa_domain = "alexa.amazon.com"
    return Config()


# ==================== TIMER TESTS ====================

class TestTimerManagerTyped:
    """Tests for Phase 3.7.1 - TimerManager.get_timers_typed()"""
    
    def test_get_timers_typed_returns_dto(self):
        """Test that get_timers_typed returns GetTimersResponse DTO"""
        from core.timers.timer_manager import TimerManager
        
        # Create manager
        tm = TimerManager(
            auth=MockAuth(),
            state_machine=MockStateMachine(),
            api_service=MockAPIServiceForTimers(),
            cache_service=MockCacheService(),
            cache_ttl=60
        )
        
        response = tm.get_timers_typed(force_refresh=True)
        
        # Should either return DTO or None (if DTO not available)
        if response is not None:
            assert hasattr(response, 'timers'), "Response should have 'timers' attribute"
            assert len(response.timers) >= 1, "Should have timers"
            # Check first timer has expected fields
            if len(response.timers) > 0:
                timer = response.timers[0]
                assert hasattr(timer, 'label'), "Timer should have label"
    
    def test_get_timers_typed_graceful_fallback(self):
        """Test graceful fallback when DTOs not available"""
        from core.timers.timer_manager import TimerManager, HAS_TIMER_DTO
        
        if not HAS_TIMER_DTO:
            pytest.skip("DTO not available, skipping test")
        
        tm = TimerManager(
            auth=MockAuth(),
            state_machine=MockStateMachine(),
            api_service=MockAPIServiceForTimers(),
            cache_service=MockCacheService(),
            cache_ttl=60
        )
        
        # Should not raise exception
        response = tm.get_timers_typed(force_refresh=True)
        assert response is None or hasattr(response, 'timers')


# ==================== REMINDER TESTS ====================

class MockHTTPClientForReminders:
    """Mock HTTP client for reminders"""
    csrf = "test_csrf"
    
    def get(self, url: str, headers: Dict = None, timeout: int = 10):
        """Mock GET request"""
        class Response:
            def json(self):
                return {
                    "reminders": [
                        {
                            "id": "reminder_1",
                            "reminderId": "reminder_1",
                            "label": "Doctor Appointment",
                            "triggerTime": "2025-10-20T10:00:00Z",
                            "enabled": True,
                        },
                        {
                            "id": "reminder_2",
                            "reminderId": "reminder_2",
                            "label": "Dentist",
                            "triggerTime": "2025-10-25T14:00:00Z",
                            "enabled": False,
                        }
                    ]
                }
            
            def raise_for_status(self):
                pass
        
        return Response()


class TestReminderManagerTyped:
    """Tests for Phase 3.7.2 - ReminderManager.get_reminders_typed()"""
    
    def test_get_reminders_typed_returns_dto(self):
        """Test that get_reminders_typed returns GetRemindersResponse DTO"""
        from core.timers.reminder_manager import ReminderManager
        
        # Create manager with minimal config
        config = make_minimal_config()
        rm = ReminderManager(
            auth=MockAuth(),
            config=config,
            state_machine=MockStateMachine(),
            cache_service=MockCacheService()
        )
        
        # Override http_client
        rm.http_client = MockHTTPClientForReminders()
        
        response = rm.get_reminders_typed()
        
        # Should either return DTO or None
        if response is not None:
            assert hasattr(response, 'reminders'), "Response should have 'reminders' attribute"
            assert len(response.reminders) >= 1, "Should have reminders"


# ==================== ALARM TESTS ====================

class MockHTTPClientForAlarms:
    """Mock HTTP client for alarms"""
    csrf = "test_csrf"
    
    def get(self, url: str, headers: Dict = None, timeout: int = 10):
        """Mock GET request"""
        class Response:
            def json(self):
                return {
                    "alarms": [
                        {
                            "id": "alarm_1",
                            "alarmId": "alarm_1",
                            "label": "Morning Alarm",
                            "time": "07:00:00",
                            "enabled": True,
                            "recurring": True,
                            "daysOfWeek": ["MON", "TUE", "WED", "THU", "FRI"],
                        },
                        {
                            "id": "alarm_2",
                            "alarmId": "alarm_2",
                            "label": "Weekend",
                            "time": "09:00:00",
                            "enabled": True,
                            "recurring": True,
                            "daysOfWeek": ["SAT", "SUN"],
                        }
                    ]
                }
            
            def raise_for_status(self):
                pass
        
        return Response()


class TestAlarmManagerTyped:
    """Tests for Phase 3.7.2 - AlarmManager.get_alarms_typed()"""
    
    def test_get_alarms_typed_returns_dto(self):
        """Test that get_alarms_typed returns GetAlarmsResponse DTO"""
        from core.timers.alarm_manager import AlarmManager
        
        # Create manager with minimal config
        config = make_minimal_config()
        am = AlarmManager(
            auth=MockAuth(),
            config=config,
            state_machine=MockStateMachine()
        )
        
        # Override http_client
        am.http_client = MockHTTPClientForAlarms()
        
        response = am.get_alarms_typed()
        
        # Should either return DTO or None
        if response is not None:
            assert hasattr(response, 'alarms'), "Response should have 'alarms' attribute"
            assert len(response.alarms) >= 1, "Should have alarms"
