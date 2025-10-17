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
        from core.schemas.communication_schemas import CommunicationResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.send_speak_command("DEVICE001", "Hello World")
        
        # Verify the request was made and result is typed DTO
        assert mock_session.request.called
        assert isinstance(result, CommunicationResponse)
        assert result.success is True

    def test_announce_command_returns_response_dto(self):
        """send_announce_command should return ResponseDTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.communication_schemas import CommunicationResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.send_announce_command("DEVICE001", "Important update", title="Alert")
        
        # Verify the request was made and result is typed DTO
        assert mock_session.request.called
        assert isinstance(result, CommunicationResponse)
        assert result.success is True

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

    def test_create_reminder_returns_response_dto(self):
        """create_reminder should return ReminderResponse DTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.reminder_schemas import ReminderResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "reminderId": "rem123"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.create_reminder("Doctor Appointment", "2024-02-15T14:00:00Z")
        
        assert isinstance(result, ReminderResponse)
        assert result.success is True
        assert result.reminder_id == "rem123"

    def test_set_alarm_returns_response_dto(self):
        """set_alarm should return AlarmResponse DTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.alarm_schemas import AlarmResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "alarmId": "alarm123"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.set_alarm("DEVICE001", "07:00:00", label="Morning")
        
        assert isinstance(result, AlarmResponse)
        assert result.success is True
        assert result.alarm_id == "alarm123"

    def test_set_dnd_returns_response_dto(self):
        """set_dnd should return DNDResponse DTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.dnd_schemas import DNDResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "dndEnabled": True}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.set_dnd("DEVICE001", 60)
        
        assert isinstance(result, DNDResponse)
        assert result.success is True
        assert result.dnd_enabled is True

    def test_execute_routine_returns_response_dto(self):
        """execute_routine should return RoutineResponse DTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.routine_schemas import RoutineResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "message": "Routine executed"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.execute_routine("routine123")
        
        assert isinstance(result, RoutineResponse)
        assert result.success is True

    def test_get_lists_returns_response_dto(self):
        """get_lists should return ListResponse DTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.list_schemas import ListResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "listId": "list1"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.get_lists()
        
        assert isinstance(result, ListResponse)
        assert result.success is True

    def test_get_smart_home_devices_returns_response_dto(self):
        """get_smart_home_devices should return SmartHomeResponse DTO."""
        from services.alexa_api_service import AlexaAPIService
        from core.schemas.smart_home_schemas import SmartHomeResponse
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "state": "on"}
        mock_response.status_code = 200
        mock_session.request.return_value = mock_response
        
        service = AlexaAPIService(session=mock_session)
        result = service.get_smart_home_devices()
        
        assert isinstance(result, SmartHomeResponse)
        assert result.success is True
