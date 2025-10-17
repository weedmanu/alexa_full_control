"""Proof-of-concept tests for Device Manager with AlexaAPIService (mandatory)."""
import pytest
from unittest.mock import Mock, MagicMock
from core.device_manager import DeviceManager
from services.alexa_api_service import AlexaAPIService


@pytest.fixture
def auth_mock():
    """Mock AlexaAuth object."""
    auth = Mock()
    auth.amazon_domain = "amazon.fr"
    return auth


@pytest.fixture
def state_machine_mock():
    """Mock AlexaStateMachine."""
    return Mock()


@pytest.fixture
def cache_service_mock():
    """Mock CacheService."""
    cache = Mock()
    cache.get.return_value = None
    cache.set.return_value = None
    return cache


@pytest.fixture
def api_service_mock():
    """Mock AlexaAPIService."""
    api = Mock(spec=AlexaAPIService)
    api.get_devices.return_value = [
        {"serialNumber": "G090LF123", "accountName": "Salon", "online": True},
    ]
    return api


def test_device_manager_requires_api_service(
    auth_mock, state_machine_mock, cache_service_mock
):
    """Verify DeviceManager requires api_service (no longer optional)."""
    with pytest.raises(ValueError, match="api_service ne peut pas être None"):
        device_mgr = DeviceManager(
            auth=auth_mock,
            state_machine=state_machine_mock,
            api_service=None,
            cache_service=cache_service_mock,
        )


def test_device_manager_uses_api_service(
    auth_mock, state_machine_mock, cache_service_mock, api_service_mock
):
    """Verify get_devices uses AlexaAPIService (mandatory)."""
    device_mgr = DeviceManager(
        auth=auth_mock,
        state_machine=state_machine_mock,
        api_service=api_service_mock,
        cache_service=cache_service_mock,
    )
    
    devices = device_mgr.get_devices(force_refresh=True)
    
    # Should call the injected API service
    api_service_mock.get_devices.assert_called()
    assert len(devices) == 1
    assert devices[0]["accountName"] == "Salon"


def test_device_manager_stores_api_service_in_cache(
    auth_mock, state_machine_mock, cache_service_mock, api_service_mock
):
    """Verify devices are cached after retrieval via AlexaAPIService."""
    device_mgr = DeviceManager(
        auth=auth_mock,
        state_machine=state_machine_mock,
        api_service=api_service_mock,
        cache_service=cache_service_mock,
    )
    
    devices = device_mgr.get_devices(force_refresh=True)
    
    # Verify cache was updated
    cache_service_mock.set.assert_called_once()
    call_args = cache_service_mock.set.call_args
    assert call_args[0][0] == "devices"
    assert "devices" in call_args[0][1]

