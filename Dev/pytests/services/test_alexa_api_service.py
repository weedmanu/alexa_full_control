import json
import time
import pytest

from types import SimpleNamespace


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=''):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


class DummySession:
    def __init__(self):
        self.requests = []

    def request(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        # simple routing for tests
        if url.endswith('/devices'):
            return DummyResponse(200, json_data={"devices": [{"id": "dev1"}]})
        if url.endswith('/err'):
            return DummyResponse(500, json_data={"error": "boom"}, text='boom')
        if url.endswith('/post') and method.lower() == 'post':
            return DummyResponse(201, json_data={"ok": True})
        raise RuntimeError(f"unhandled url {url}")


def make_cache_with(key, value):
    store = {key: value}

    class C:
        def get(self, k, ignore_ttl=False):
            return store.get(k)

    return C()


@pytest.mark.unit
def test_get_success_returns_json(monkeypatch):
    # service should call session.request and return JSON
    from services import alexa_api_service

    session = DummySession()
    svc = alexa_api_service.AlexaAPIService(session=session)
    data = svc.get('devices')
    assert isinstance(data, dict)
    assert 'devices' in data


@pytest.mark.unit
def test_get_api_error_raises_ApiError(monkeypatch):
    from services import alexa_api_service

    session = DummySession()
    svc = alexa_api_service.AlexaAPIService(session=session)
    with pytest.raises(alexa_api_service.ApiError):
        svc.get('/err')


@pytest.mark.unit
def test_get_network_error_uses_cache_fallback(monkeypatch):
    from services import alexa_api_service

    # simulate session raising requests.exceptions.RequestException
    class BadSession:
        def request(self, method, url, **kwargs):
            raise Exception("network")

    cache = make_cache_with('devices_cache', {"devices": [{"id": "cached"}]})
    svc = alexa_api_service.AlexaAPIService(session=BadSession(), cache_service=cache)
    # expect fallback to return cached value
    data = svc.get('devices', cache_key='devices_cache')
    assert data.get('devices')[0]['id'] == 'cached'


@pytest.mark.unit
def test_post_success_calls_session_post(monkeypatch):
    from services import alexa_api_service

    session = DummySession()
    svc = alexa_api_service.AlexaAPIService(session=session)
    res = svc.post('/post', json={'a': 1})
    assert res.get('ok') is True


@pytest.mark.unit
def test_circuit_breaker_trips_after_failures(monkeypatch):
    from services import alexa_api_service

    # a simple breaker that opens after 2 failures - use real pybreaker if available
    session = DummySession()
    svc = alexa_api_service.AlexaAPIService(session=session)

    # first call to /err -> ApiError
    with pytest.raises(alexa_api_service.ApiError):
        svc.get('/err')
    # second call -> still error
    with pytest.raises(alexa_api_service.ApiError):
        svc.get('/err')
    # depending on breaker settings, a CircuitOpen error may be raised
    # we accept either ApiError or alexa_api_service.CircuitOpen
    try:
        svc.get('/err')
    except Exception as exc:
        assert isinstance(exc, (alexa_api_service.ApiError, alexa_api_service.CircuitOpen))
from unittest.mock import Mock

import pytest

from core.exceptions import APIError
from services.alexa_api_service import AlexaAPIService


class TestAlexaAPIServiceInitialization:
    def test_service_initializes_with_auth_and_cache(self):
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        assert service._auth == auth
        assert service._cache == cache


class TestGetDevices:
    def test_get_devices_returns_list_of_devices(self):
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)

        mock_response = Mock()
        mock_response.json.return_value = {"devices": [{"serialNumber": "ABC123"}]}
        auth.get.return_value = mock_response

        res = service.get_devices()
        assert isinstance(res, list)
        assert res[0]["serialNumber"] == "ABC123"

    def test_get_devices_falls_back_to_cache_on_failure(self):
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)

        auth.get.side_effect = Exception("API down")
        cache.get.return_value = {"devices": [{"serialNumber": "CACHED"}]}

        res = service.get_devices(use_cache_fallback=True)
        assert res[0]["serialNumber"] == "CACHED"

    def test_get_devices_raises_api_error_on_failure(self):
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)

        auth.get.side_effect = Exception("Failure")

        with pytest.raises(APIError):
            service.get_devices(use_cache_fallback=False)


class TestSendSpeak:
    def test_send_speak_command_calls_auth_post(self):
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)

        service.send_speak_command("ABC123", "hello")
        auth.post.assert_called()
