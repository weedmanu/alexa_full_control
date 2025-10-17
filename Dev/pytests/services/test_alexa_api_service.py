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
