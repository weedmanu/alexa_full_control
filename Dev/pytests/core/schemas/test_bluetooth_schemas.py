"""
Bluetooth Schema Tests - Phase 3.5c.11 (TDD)

Tests for Bluetooth device DTOs.
Covers: Bluetooth device management.

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/bluetooth_schemas.py
"""

import pytest
from datetime import datetime, timezone
from typing import Optional
from pydantic import ValidationError


class TestBluetoothDeviceDTO:
    """Test BluetoothDeviceDTO."""

    def test_device_required_fields(self):
        """Should accept device_address and name."""
        from core.schemas.bluetooth_schemas import BluetoothDeviceDTO
        
        device = BluetoothDeviceDTO(
            device_address="00:1A:7D:DA:71:13",
            name="JBL Speaker"
        )
        
        assert device.device_address == "00:1A:7D:DA:71:13"
        assert device.name == "JBL Speaker"

    def test_device_with_paired(self):
        """Should accept optional paired flag."""
        from core.schemas.bluetooth_schemas import BluetoothDeviceDTO
        
        device = BluetoothDeviceDTO(
            device_address="00:1A:7D:DA:71:13",
            name="JBL Speaker",
            paired=True
        )
        
        assert device.paired is True

    def test_device_requires_address(self):
        """Address is required."""
        from core.schemas.bluetooth_schemas import BluetoothDeviceDTO
        
        with pytest.raises(ValidationError):
            BluetoothDeviceDTO(name="JBL Speaker")

    def test_device_requires_name(self):
        """Name is required."""
        from core.schemas.bluetooth_schemas import BluetoothDeviceDTO
        
        with pytest.raises(ValidationError):
            BluetoothDeviceDTO(device_address="00:1A:7D:DA:71:13")

    def test_device_is_immutable(self):
        """BluetoothDeviceDTO should be frozen."""
        from core.schemas.bluetooth_schemas import BluetoothDeviceDTO
        
        device = BluetoothDeviceDTO(device_address="00:1A:7D:DA:71:13", name="JBL Speaker")
        
        with pytest.raises(Exception):
            device.name = "Sony Speaker"


class TestBluetoothRequest:
    """Test BluetoothRequest."""

    def test_bluetooth_request(self):
        """Should accept device_address and action."""
        from core.schemas.bluetooth_schemas import BluetoothRequest
        
        request = BluetoothRequest(
            device_address="00:1A:7D:DA:71:13",
            action="CONNECT"
        )
        
        assert request.device_address == "00:1A:7D:DA:71:13"
        assert request.action == "CONNECT"

    def test_request_requires_address(self):
        """Address is required."""
        from core.schemas.bluetooth_schemas import BluetoothRequest
        
        with pytest.raises(ValidationError):
            BluetoothRequest(action="CONNECT")

    def test_request_requires_action(self):
        """Action is required."""
        from core.schemas.bluetooth_schemas import BluetoothRequest
        
        with pytest.raises(ValidationError):
            BluetoothRequest(device_address="00:1A:7D:DA:71:13")


class TestBluetoothResponse:
    """Test BluetoothResponse."""

    def test_response_success(self):
        """Should accept success flag."""
        from core.schemas.bluetooth_schemas import BluetoothResponse
        
        response = BluetoothResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_response_with_paired(self):
        """Should accept optional paired flag."""
        from core.schemas.bluetooth_schemas import BluetoothResponse
        
        response = BluetoothResponse(success=True, paired=True)
        
        assert response.paired is True

    def test_response_requires_success(self):
        """Success field is required."""
        from core.schemas.bluetooth_schemas import BluetoothResponse
        
        with pytest.raises(ValidationError):
            BluetoothResponse()

    def test_response_auto_sets_created_at(self):
        """Created_at should be auto-set."""
        from core.schemas.bluetooth_schemas import BluetoothResponse
        
        before = datetime.now(timezone.utc)
        response = BluetoothResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after


class TestBluetoothWorkflow:
    """Test Bluetooth workflows."""

    def test_bluetooth_connect_workflow(self):
        """Should support complete Bluetooth connect workflow."""
        from core.schemas.bluetooth_schemas import (
            BluetoothRequest,
            BluetoothResponse
        )
        
        request = BluetoothRequest(
            device_address="00:1A:7D:DA:71:13",
            action="CONNECT"
        )
        
        response = BluetoothResponse(success=True, paired=True)
        
        assert request.action == "CONNECT"
        assert response.paired is True

    def test_bluetooth_disconnect_workflow(self):
        """Should support Bluetooth disconnect."""
        from core.schemas.bluetooth_schemas import BluetoothRequest
        
        request = BluetoothRequest(
            device_address="00:1A:7D:DA:71:13",
            action="DISCONNECT"
        )
        
        assert request.action == "DISCONNECT"

    def test_device_field_aliasing(self):
        """Should support camelCase field aliasing."""
        from core.schemas.bluetooth_schemas import BluetoothDeviceDTO
        
        device_data = {
            "deviceAddress": "00:1A:7D:DA:71:13",
            "name": "JBL Speaker"
        }
        
        device = BluetoothDeviceDTO(**device_data)
        
        assert device.device_address == "00:1A:7D:DA:71:13"

    def test_bluetooth_device_list(self):
        """Should parse list of Bluetooth devices."""
        from core.schemas.bluetooth_schemas import BluetoothDeviceDTO
        
        devices_data = [
            {"deviceAddress": "00:1A:7D:DA:71:13", "name": "JBL Speaker"},
            {"deviceAddress": "00:1B:7E:DB:72:14", "name": "Sony Headphones"}
        ]
        
        devices = [BluetoothDeviceDTO(**d) for d in devices_data]
        
        assert len(devices) == 2
        assert devices[0].name == "JBL Speaker"
        assert devices[1].name == "Sony Headphones"
