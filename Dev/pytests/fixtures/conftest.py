"""Shared pytest fixtures and mocks for all tests."""

import pytest
from unittest.mock import MagicMock, Mock
from typing import Dict, Any, Optional
import threading


# ==============================================================================
# AUTH FIXTURES
# ==============================================================================

@pytest.fixture
def mock_auth():
    """Mock Alexa authentication object."""
    auth = MagicMock()
    auth.get_csrf_token = MagicMock(return_value="mock_csrf_token_12345")
    auth.get_headers = MagicMock(return_value={
        "User-Agent": "AmazonAlexa/2.0",
        "Authorization": "Bearer mock_token"
    })
    auth.is_authenticated = MagicMock(return_value=True)
    auth.refresh_token = MagicMock(return_value=True)
    return auth


# ==============================================================================
# HTTP CLIENT FIXTURES
# ==============================================================================

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for API calls."""
    client = MagicMock()
    
    # Default success responses
    client.get = MagicMock(return_value={"status": "ok", "data": []})
    client.post = MagicMock(return_value={"status": "ok"})
    client.put = MagicMock(return_value={"status": "ok"})
    client.delete = MagicMock(return_value={"status": "ok"})
    
    # Headers always present
    client.headers = {
        "User-Agent": "AmazonAlexa/2.0",
        "X-Csrf-Token": "mock_csrf_token_12345"
    }
    
    # Session management
    client.session = MagicMock()
    client.session.headers = client.headers
    
    return client


# ==============================================================================
# CONFIG FIXTURES
# ==============================================================================

@pytest.fixture
def mock_config():
    """Mock application configuration."""
    config = MagicMock()
    config.debug = True
    config.cache_ttl = 300
    config.timeout = 30
    config.max_retries = 3
    config.circuit_breaker = {
        "failure_threshold": 3,
        "timeout": 30,
        "recovery_timeout": 60
    }
    return config


# ==============================================================================
# STATE MACHINE FIXTURES
# ==============================================================================

@pytest.fixture
def mock_state_machine():
    """Mock Alexa state machine."""
    machine = MagicMock()
    machine.get_state = MagicMock(return_value={
        "devices": [],
        "routines": [],
        "alarms": [],
        "timers": [],
        "reminders": [],
        "notifications": []
    })
    machine.update_state = MagicMock(return_value=True)
    machine.lock = threading.RLock()
    return machine


# ==============================================================================
# CACHE SERVICE FIXTURES
# ==============================================================================

@pytest.fixture
def mock_cache_service() -> MagicMock:
    """Mock cache service."""
    cache: MagicMock = MagicMock()
    cache_dict: Dict[str, Any] = {}
    
    def get_side_effect(key: str, default: Any = None) -> Any:
        return cache_dict.get(key, default)
    
    def set_side_effect(key: str, value: Any) -> bool:
        cache_dict[key] = value
        return True
    
    def clear_side_effect() -> bool:
        cache_dict.clear()
        return True
    
    cache.get = MagicMock(side_effect=get_side_effect)
    cache.set = MagicMock(side_effect=set_side_effect)
    cache.clear = MagicMock(side_effect=clear_side_effect)
    cache.get_lock = MagicMock(return_value=threading.RLock())
    
    return cache


# ==============================================================================
# CIRCUIT BREAKER FIXTURES
# ==============================================================================

@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker."""
    breaker = MagicMock()
    breaker.call = MagicMock(return_value={"status": "ok"})
    breaker.is_open = MagicMock(return_value=False)
    breaker.reset = MagicMock(return_value=True)
    breaker.failure_count = 0
    breaker.state = "closed"
    return breaker


# ==============================================================================
# MANAGER FIXTURES (BASE STRUCTURES)
# ==============================================================================

@pytest.fixture
def manager_init_params(mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock, mock_cache_service: MagicMock) -> Dict[str, Any]:
    """Common parameters for manager initialization."""
    return {
        "auth": mock_auth,
        "config": mock_config,
        "state_machine": mock_state_machine,
        "cache_service": mock_cache_service
    }


# ==============================================================================
# TEST DATA FIXTURES
# ==============================================================================

@pytest.fixture
def sample_devices() -> list[dict[str, Any]]:
    """Sample device data."""
    return [
        {
            "serialNumber": "DEVICE-1-ABC123",
            "deviceName": "Living Room Echo",
            "deviceType": "ALEXA_GUARD_DISPLAY_ECHO_SHOW_5",
            "online": True
        },
        {
            "serialNumber": "DEVICE-2-DEF456",
            "deviceName": "Kitchen Echo",
            "deviceType": "ALEXA_GUARD_ECHO_DOT_3RD",
            "online": True
        }
    ]


@pytest.fixture
def sample_alarms() -> list[dict[str, Any]]:
    """Sample alarm data."""
    return [
        {
            "id": "alarm-1",
            "label": "Morning Alarm",
            "time": "08:00",
            "recurring": True,
            "daysOfWeek": ["MON", "TUE", "WED", "THU", "FRI"]
        },
        {
            "id": "alarm-2",
            "label": "Meeting Reminder",
            "time": "14:30",
            "recurring": False
        }
    ]


@pytest.fixture
def sample_routines() -> list[dict[str, Any]]:
    """Sample routine data."""
    return [
        {
            "id": "routine-1",
            "name": "Good Morning",
            "triggers": [{"type": "TimeOfDay", "time": "07:00"}],
            "actions": [
                {"type": "ExecuteDeviceAction", "deviceId": "device-1"},
                {"type": "PlayMusicAction", "musicProvider": "AMAZON_MUSIC"}
            ]
        },
        {
            "id": "routine-2",
            "name": "Goodnight",
            "triggers": [{"type": "VoiceCommand", "phrase": "goodnight"}],
            "actions": [{"type": "ExecuteDeviceAction", "deviceId": "device-1"}]
        }
    ]


# ==============================================================================
# UTILITY FIXTURES
# ==============================================================================

@pytest.fixture
def reset_circuit_breaker_registry():
    """Reset circuit breaker registry between tests."""
    from core.breaker_registry import CircuitBreakerRegistry
    yield
    CircuitBreakerRegistry.reset()


@pytest.fixture
def cleanup_cache():
    """Cleanup cache between tests."""
    yield
    # Any cleanup needed


# ==============================================================================
# MARKERS FOR TEST ORGANIZATION
# ==============================================================================

def pytest_configure(config: Any) -> None:  # type: ignore
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests for isolated components")
    config.addinivalue_line("markers", "integration: Integration tests across modules")
    config.addinivalue_line("markers", "security: Security-specific tests")
    config.addinivalue_line("markers", "slow: Tests that take >1s")
    config.addinivalue_line("markers", "cli: CLI command tests")
