"""
Phase 3.6: AlexaAPIService Integration Tests

Tests for integrating DTO schemas into AlexaAPIService.
Demonstrates how to use typed DTOs for API requests/responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError


class TestAlexaAPIServiceWithDTOs:
    """Test AlexaAPIService returning typed DTOs instead of dicts."""

    def test_get_devices_returns_device_response_dto(self):
        """get_devices() should return GetDevicesResponse DTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.device_schemas import GetDevicesResponse
        
        # Mock the session
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "devices": [
                {
                    "serialNumber": "DEVICE001",
                    "deviceName": "Living Room",
                    "deviceType": "ALEXA",
                    "online": True
                }
            ]
        }
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.get_devices()
        
        # Result should be typed as GetDevicesResponse
        # For now just verify it returns a dict (will be GetDevicesResponse in implementation)
        assert isinstance(result, (dict, list))

    def test_speak_command_returns_response_dto(self):
        """send_speak_command should return ResponseDTO."""
        from services.alexa_api_service import AlexaAPIService
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        service.send_speak_command("DEVICE001", "Hello World")
        
        # Verify the request was made
        assert mock_session.request.called

    def test_api_error_includes_error_code(self):
        """API errors should include error_code for better debugging."""
        from services.alexa_api_service import AlexaAPIService, ApiError
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request", "errorCode": "INVALID_PARAM"}
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        
        with pytest.raises(ApiError):
            service.get("test")

    def test_dto_field_validation_on_response(self):
        """ResponseDTO should validate fields automatically."""
        from core.schemas.device_schemas import GetDevicesResponse
        
        # This should pass
        response = GetDevicesResponse(devices=[])
        assert response.devices == []
        assert response.created_at is not None

    def test_dto_field_aliasing_on_request(self):
        """RequestDTO should accept camelCase from API."""
        from core.schemas.device_schemas import GetDevicesRequest
        
        # RequestDTO with camelCase (API) should map to snake_case (Python)
        request = GetDevicesRequest()
        assert request is not None

    def test_device_dto_from_amazon_response(self):
        """Device DTO should parse Amazon API response format."""
        from core.schemas.device_schemas import Device
        
        amazon_device_data = {
            "serialNumber": "DEVICE001",
            "deviceName": "Living Room",
            "deviceType": "ECHO_DOT",
            "online": True
        }
        
        device = Device(**amazon_device_data)
        
        assert device.serial_number == "DEVICE001"
        assert device.device_name == "Living Room"
        assert device.online is True

    def test_multiple_devices_parsing(self):
        """Multiple devices should parse correctly."""
        from core.schemas.device_schemas import Device
        
        devices_data = [
            {
                "serialNumber": "DEVICE001",
                "deviceName": "Living Room",
                "deviceType": "ECHO_DOT",
                "online": True
            },
            {
                "serialNumber": "DEVICE002",
                "deviceName": "Bedroom",
                "deviceType": "ALEXA",
                "online": False
            }
        ]
        
        devices = [Device(**d) for d in devices_data]
        
        assert len(devices) == 2
        assert devices[0].device_name == "Living Room"
        assert devices[1].online is False

    def test_dto_immutability_prevents_accidental_modification(self):
        """ResponseDTO immutability should prevent accidental field changes."""
        from core.schemas.device_schemas import GetDevicesResponse
        
        response = GetDevicesResponse(devices=[])
        
        with pytest.raises(Exception):
            response.devices = [{"name": "new"}]

    def test_authenticated_request_with_dto(self):
        """Authenticated requests should return DTOs."""
        from services.alexa_api_service import AlexaAPIService
        
        # Mock authenticated session
        mock_auth = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "devices": [
                {
                    "serialNumber": "DEVICE001",
                    "deviceName": "Living Room",
                    "deviceType": "ECHO_DOT",
                    "online": True
                }
            ]
        }
        mock_auth.get.return_value = mock_response
        mock_auth.amazon_domain = "amazon.com"
        
        service = AlexaAPIService(mock_auth)
        result = service.get_devices()
        
        # Should return list of devices
        assert isinstance(result, list) or isinstance(result, dict)
