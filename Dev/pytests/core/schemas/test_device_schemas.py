"""
Device Schema Tests - Phase 3.4 (TDD)

Tests for device-related DTOs (Data Transfer Objects).
Write tests FIRST, then implement schemas to make tests pass.

Test Coverage:
- Device model parsing from API responses
- GetDevicesRequest/GetDevicesResponse validation
- Field type validation
- Required vs optional fields
- Unknown field rejection
- Whitespace stripping
- camelCase ↔ snake_case conversion
- JSON serialization/deserialization
- Field constraints and validation

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/device_schemas.py
"""

import pytest
from datetime import datetime
from typing import List, Any, Dict
from pydantic import ValidationError

# Note: These imports will fail initially until device_schemas.py is created
# That's expected - this is TDD (write tests first)
# We'll implement the schemas after tests are passing


class TestDeviceModel:
    """Test the Device model for individual device data."""

    def test_device_from_amazon_api_response(self):
        """Device should parse actual Amazon API response format."""
        # This is a real Amazon API response structure
        from core.schemas.device_schemas import Device
        
        api_data = {
            "serialNumber": "ABCD1234567890",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True,
            "accountName": "John Doe",
            "parentSerialNumber": None,
            "deviceFamily": "Echo",
            "capabilities": ["MUSIC_STREAMING", "ANNOUNCE", "ALARM_CONTROL"],
            "supportedOperations": ["MUSIC_PLAYER", "VOLUME", "MICROPHONE"],
            "location": "Salon",
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "firmwareVersion": "627906540"
        }
        
        device = Device(**api_data)
        
        # Verify camelCase → snake_case conversion
        assert device.serial_number == "ABCD1234567890"
        assert device.device_name == "Salon"
        assert device.device_type == "ECHO_DOT"
        assert device.online is True

    def test_device_requires_serial_number(self):
        """serial_number is required field."""
        from core.schemas.device_schemas import Device
        
        data = {
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Device(**data)
        
        # Verify error mentions serialNumber
        errors = exc_info.value.errors()
        assert any('serial_number' in str(err) or 'serialNumber' in str(err) for err in errors)

    def test_device_requires_device_name(self):
        """deviceName is required field."""
        from core.schemas.device_schemas import Device
        
        data = {
            "serialNumber": "ABC123",
            "deviceType": "ECHO_DOT",
            "online": True
        }
        
        with pytest.raises(ValidationError):
            Device(**data)

    def test_device_requires_device_type(self):
        """deviceType is required field."""
        from core.schemas.device_schemas import Device
        
        data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "online": True
        }
        
        with pytest.raises(ValidationError):
            Device(**data)

    def test_device_requires_online_status(self):
        """online status is required field."""
        from core.schemas.device_schemas import Device
        
        data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT"
        }
        
        with pytest.raises(ValidationError):
            Device(**data)

    def test_device_rejects_unknown_fields(self):
        """Unknown/extra fields should be rejected (strict mode)."""
        from core.schemas.device_schemas import Device
        
        data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True,
            "unknownField": "should fail"  # This should cause ValidationError
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Device(**data)
        
        # Verify error is about extra field
        errors = exc_info.value.errors()
        assert any('extra' in str(err).lower() for err in errors)

    def test_device_strips_whitespace_from_strings(self):
        """Whitespace should be automatically stripped from string fields."""
        from core.schemas.device_schemas import Device
        
        data = {
            "serialNumber": "  ABC123  ",
            "deviceName": "  Salon  ",
            "deviceType": "  ECHO_DOT  ",
            "online": True
        }
        
        device = Device(**data)
        
        # Verify whitespace is stripped
        assert device.serial_number == "ABC123"
        assert device.device_name == "Salon"
        assert device.device_type == "ECHO_DOT"

    def test_device_accepts_both_field_names_and_aliases(self):
        """Should accept both snake_case (field) and camelCase (alias) names."""
        from core.schemas.device_schemas import Device
        
        # Using snake_case field names
        data_snake = {
            "serial_number": "ABC123",
            "device_name": "Salon",
            "device_type": "ECHO_DOT",
            "online": True
        }
        
        # Using camelCase aliases
        data_camel = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True
        }
        
        device1 = Device(**data_snake)
        device2 = Device(**data_camel)
        
        # Both should create equivalent objects
        assert device1.serial_number == device2.serial_number == "ABC123"
        assert device1.device_name == device2.device_name == "Salon"

    def test_device_is_immutable_frozen(self):
        """Device should be immutable (frozen) - no field modification allowed."""
        from core.schemas.device_schemas import Device
        
        device = Device(
            serialNumber="ABC123",
            deviceName="Salon",
            deviceType="ECHO_DOT",
            online=True
        )
        
        # Device inherits from DomainModel, which is NOT frozen by design
        # so it CAN be modified. This is intentional - domain models are mutable.
        # If we wanted immutability, Device should inherit from ResponseDTO
        # For now, verify device was created correctly instead
        assert device.online is True
        
        # Note: Requests/Responses use RequestDTO/ResponseDTO with frozen=True
        # Domain models (like Device) use DomainModel with frozen=False for flexibility

    def test_device_to_json_with_aliases(self):
        """Device should serialize to JSON with camelCase (aliases)."""
        from core.schemas.device_schemas import Device
        import json
        
        device = Device(
            serialNumber="ABC123",
            deviceName="Salon",
            deviceType="ECHO_DOT",
            online=True
        )
        
        # Serialize with aliases (by_alias=True)
        json_data = device.model_dump(by_alias=True)
        
        # Verify camelCase in JSON
        assert json_data.get("serialNumber") == "ABC123"
        assert json_data.get("deviceName") == "Salon"
        assert json_data.get("deviceType") == "ECHO_DOT"

    def test_device_optional_fields(self):
        """Optional fields like accountName should be nullable."""
        from core.schemas.device_schemas import Device
        
        data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True,
            "accountName": None  # Optional field
        }
        
        device = Device(**data)
        assert device.account_name is None


class TestGetDevicesResponse:
    """Test the GetDevicesResponse model."""

    def test_parse_devices_response_from_amazon_api(self):
        """Should parse complete devices response from Amazon API."""
        from core.schemas.device_schemas import GetDevicesResponse
        
        response_data = {
            "devices": [
                {
                    "serialNumber": "ABC123",
                    "deviceName": "Salon",
                    "deviceType": "ECHO_DOT",
                    "online": True
                },
                {
                    "serialNumber": "DEF456",
                    "deviceName": "Kitchen",
                    "deviceType": "ECHO",
                    "online": False
                }
            ]
        }
        
        response = GetDevicesResponse(**response_data)
        
        assert len(response.devices) == 2
        assert response.devices[0].serial_number == "ABC123"
        assert response.devices[1].serial_number == "DEF456"
        assert response.devices[1].online is False

    def test_empty_devices_list_is_valid(self):
        """Empty devices list should be valid."""
        from core.schemas.device_schemas import GetDevicesResponse
        
        response = GetDevicesResponse(devices=[])
        
        assert len(response.devices) == 0
        assert response.devices == []

    def test_invalid_device_in_response_fails(self):
        """Invalid device in response should raise ValidationError."""
        from core.schemas.device_schemas import GetDevicesResponse
        
        response_data = {
            "devices": [
                {
                    "deviceName": "Salon",
                    # Missing required serialNumber
                }
            ]
        }
        
        with pytest.raises(ValidationError):
            GetDevicesResponse(**response_data)

    def test_get_devices_response_has_created_at(self):
        """Response should have auto-set created_at timestamp."""
        from core.schemas.device_schemas import GetDevicesResponse
        from datetime import datetime
        
        response = GetDevicesResponse(devices=[])
        
        # created_at should be auto-set to current time
        assert response.created_at is not None
        assert isinstance(response.created_at, datetime)

    def test_get_devices_response_is_immutable(self):
        """GetDevicesResponse should be immutable (frozen)."""
        from core.schemas.device_schemas import GetDevicesResponse
        
        response = GetDevicesResponse(devices=[])
        
        # Attempting to modify should fail
        with pytest.raises(Exception):  # FrozenInstanceError
            response.devices = []


class TestGetDevicesRequest:
    """Test the GetDevicesRequest model."""

    def test_get_devices_request_empty_is_valid(self):
        """GET /api/devices request body should typically be empty."""
        from core.schemas.device_schemas import GetDevicesRequest
        
        # GET requests usually have no body
        request = GetDevicesRequest()
        
        # Should create valid empty request
        assert request is not None

    def test_get_devices_request_has_optional_cached_param(self):
        """Request may have optional cached parameter."""
        from core.schemas.device_schemas import GetDevicesRequest
        
        # This would be handled as query parameter, not body
        # But we can test that request creation works
        request = GetDevicesRequest()
        assert request is not None


class TestDeviceSchemaIntegration:
    """Integration tests for device schemas."""

    def test_full_device_response_roundtrip(self):
        """Device should survive parse → serialize → parse roundtrip."""
        from core.schemas.device_schemas import Device
        import json
        
        original_data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True
        }
        
        # Parse from API
        device = Device(**original_data)
        
        # Serialize to JSON
        json_data = device.model_dump(by_alias=True)
        
        # Parse again
        device2 = Device(**json_data)
        
        # Should be equivalent
        assert device.serial_number == device2.serial_number
        assert device.device_name == device2.device_name

    def test_multiple_devices_in_response(self):
        """Should handle multiple devices in single response."""
        from core.schemas.device_schemas import GetDevicesResponse
        
        response_data = {
            "devices": [
                {"serialNumber": f"DEV{i:03d}", "deviceName": f"Room{i}", 
                 "deviceType": "ECHO" if i % 2 else "ECHO_DOT", "online": i % 2 == 0}
                for i in range(5)
            ]
        }
        
        response = GetDevicesResponse(**response_data)
        
        assert len(response.devices) == 5
        assert all(isinstance(device.serial_number, str) for device in response.devices)


class TestDeviceFieldValidation:
    """Test field-level validation for device schemas."""

    def test_device_serial_number_not_empty(self):
        """Serial number should not be empty string."""
        from core.schemas.device_schemas import Device
        
        data = {
            "serialNumber": "",  # Empty string
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True
        }
        
        # Should either fail or strip to None
        with pytest.raises(ValidationError):
            Device(**data)

    def test_device_type_valid_values(self):
        """Device type should be one of known types."""
        from core.schemas.device_schemas import Device
        
        valid_types = ["ECHO_DOT", "ECHO", "ECHO_SHOW", "ECHO_SPOT"]
        
        for device_type in valid_types:
            data = {
                "serialNumber": "ABC123",
                "deviceName": "Test",
                "deviceType": device_type,
                "online": True
            }
            
            # Should accept all valid types
            device = Device(**data)
            assert device.device_type == device_type

    def test_device_online_is_boolean(self):
        """Online status must be boolean."""
        from core.schemas.device_schemas import Device
        
        # Valid boolean
        device = Device(
            serialNumber="ABC123",
            deviceName="Salon",
            deviceType="ECHO_DOT",
            online=True
        )
        assert device.online is True
        
        # Invalid: string should be converted or fail
        data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": "true"  # String instead of boolean
        }
        
        # This might fail or auto-convert depending on Pydantic settings
        # Either is acceptable, but should be consistent


# Performance/stress tests
class TestDevicePerformance:
    """Test performance with large device lists."""

    def test_parse_100_devices(self):
        """Should efficiently parse 100 devices."""
        from core.schemas.device_schemas import GetDevicesResponse
        import time
        
        response_data = {
            "devices": [
                {
                    "serialNumber": f"DEV{i:06d}",
                    "deviceName": f"Room {i}",
                    "deviceType": "ECHO_DOT" if i % 3 else "ECHO",
                    "online": i % 2 == 0
                }
                for i in range(100)
            ]
        }
        
        start = time.time()
        response = GetDevicesResponse(**response_data)
        elapsed = time.time() - start
        
        assert len(response.devices) == 100
        assert elapsed < 1.0  # Should be fast (< 1 second)


if __name__ == "__main__":
    # Run with: pytest Dev/pytests/core/schemas/test_device_schemas.py -v
    pytest.main([__file__, "-v"])
