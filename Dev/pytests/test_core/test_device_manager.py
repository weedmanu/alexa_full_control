import time
from typing import Any, Dict, List

import pytest

from core.device_manager import DeviceManager


class DummyAuth:
    amazon_domain = "amazon.test"


class DummyStateMachine:
    pass


class FakeAPIService:
    def __init__(self, devices: List[Dict[str, Any]]):
        self._devices = devices

    def get_devices(self) -> List[Dict[str, Any]]:
        return self._devices


def make_device_manager(monkeypatch, api_service=None):
    auth = DummyAuth()
    state_machine = DummyStateMachine()

    # Provide a minimal cache_service that stores to an in-memory dict
    class SimpleCache:
        def __init__(self):
            self.store = {}

        def get(self, key, ignore_ttl=False):
            return self.store.get(key)

        def set(self, key, obj, ttl_seconds=None):
            self.store[key] = obj

        def invalidate(self, key):
            if key in self.store:
                del self.store[key]

    cache_service = SimpleCache()

    dm = DeviceManager(auth=auth, state_machine=state_machine, api_service=api_service, cache_service=cache_service)
    return dm


def test_get_devices_uses_api_service(monkeypatch):
    devices = [{"accountName": "Salon", "serialNumber": "S1", "online": True}]
    api = FakeAPIService(devices)
    dm = make_device_manager(monkeypatch, api_service=api)

    res = dm.get_devices(force_refresh=True)
    assert res == devices


def test_get_devices_fallback_legacy(monkeypatch):
    # Create a DeviceManager without api_service and monkeypatch _api_call
    dm = make_device_manager(monkeypatch, api_service=None)

    def fake_api_call(method, path, params=None, timeout=None):
        return {"devices": [{"accountName": "Bureau", "serialNumber": "B1", "online": False}]}

    monkeypatch.setattr(dm, "_api_call", fake_api_call)

    res = dm.get_devices(force_refresh=True)
    assert isinstance(res, list)
    assert res[0]["accountName"] == "Bureau"


def test_get_devices_api_service_exception(monkeypatch):
    class BrokenAPI:
        def get_devices(self):
            raise RuntimeError("boom")

    api = BrokenAPI()
    dm = make_device_manager(monkeypatch, api_service=api)

    res = dm.get_devices(force_refresh=True)
    assert res is None
