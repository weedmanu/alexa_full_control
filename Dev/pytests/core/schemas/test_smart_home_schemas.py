"""
Smart Home Schema Tests - Phase 3.5c.10 (TDD)

Tests for smart home device DTOs.
Covers: smart home device management.

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/smart_home_schemas.py
"""

import pytest
from datetime import datetime, timezone
from typing import Optional
from pydantic import ValidationError


class TestSmartHomeDeviceDTO:
    """Test SmartHomeDeviceDTO."""

    def test_device_required_fields(self):
        """Should accept device_id and name."""
        from core.schemas.smart_home_schemas import SmartHomeDeviceDTO
        
        device = SmartHomeDeviceDTO(
            device_id="device123",
            name="Smart Light"
        )
        
        assert device.device_id == "device123"
        assert device.name == "Smart Light"

    def test_device_with_state(self):
        """Should accept optional state."""
        from core.schemas.smart_home_schemas import SmartHomeDeviceDTO
        
        device = SmartHomeDeviceDTO(
            device_id="device123",
            name="Smart Light",
            state="ON"
        )
        
        assert device.state == "ON"

    def test_device_requires_id(self):
        """ID is required."""
        from core.schemas.smart_home_schemas import SmartHomeDeviceDTO
        
        with pytest.raises(ValidationError):
            SmartHomeDeviceDTO(name="Smart Light")

    def test_device_is_immutable(self):
        """SmartHomeDeviceDTO should be frozen."""
        from core.schemas.smart_home_schemas import SmartHomeDeviceDTO
        
        device = SmartHomeDeviceDTO(device_id="device123", name="Smart Light")
        
        with pytest.raises(Exception):
            device.name = "Smart Switch"


class TestSmartHomeRequest:
    """Test SmartHomeRequest."""

    def test_smart_home_request(self):
        """Should accept device_serial_number and action."""
        from core.schemas.smart_home_schemas import SmartHomeRequest
        
        request = SmartHomeRequest(
            device_serial_number="DEVICE123",
            action="ON"
        )
        
        assert request.device_serial_number == "DEVICE123"
        assert request.action == "ON"

    def test_request_requires_device(self):
        """Device is required."""
        from core.schemas.smart_home_schemas import SmartHomeRequest
        
        with pytest.raises(ValidationError):
            SmartHomeRequest(action="ON")


class TestSmartHomeResponse:
    """Test SmartHomeResponse."""

    def test_response_success(self):
        """Should accept success flag."""
        from core.schemas.smart_home_schemas import SmartHomeResponse
        
        response = SmartHomeResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_response_with_state(self):
        """Should accept optional state."""
        from core.schemas.smart_home_schemas import SmartHomeResponse
        
        response = SmartHomeResponse(success=True, state="ON")
        
        assert response.state == "ON"

    def test_response_requires_success(self):
        """Success field is required."""
        from core.schemas.smart_home_schemas import SmartHomeResponse
        
        with pytest.raises(ValidationError):
            SmartHomeResponse()


class TestSmartHomeWorkflow:
    """Test smart home workflows."""

    def test_smart_home_workflow(self):
        """Should support complete smart home workflow."""
        from core.schemas.smart_home_schemas import (
            SmartHomeRequest,
            SmartHomeResponse
        )
        
        request = SmartHomeRequest(
            device_serial_number="DEVICE123",
            action="ON"
        )
        
        response = SmartHomeResponse(success=True, state="ON")
        
        assert request.action == "ON"
        assert response.state == "ON"

    def test_device_field_aliasing(self):
        """Should support camelCase field aliasing."""
        from core.schemas.smart_home_schemas import SmartHomeDeviceDTO
        
        device_data = {
            "deviceId": "device123",
            "name": "Smart Light"
        }
        
        device = SmartHomeDeviceDTO(**device_data)
        
        assert device.device_id == "device123"
