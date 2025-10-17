"""
Do Not Disturb (DND) Schema Tests - Phase 3.5c.5 (TDD)

Tests for DND (Do Not Disturb) mode DTOs.
Covers: DND status, DND configuration, sleep timer management.

Test Coverage:
- DND status DTO
- Set DND request
- DND response
- Sleep timer integration
- Serialization and field aliasing

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/dnd_schemas.py
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import ValidationError


class TestDNDStatusDTO:
    """Test DNDStatusDTO for current DND state."""

    def test_dnd_status_enabled(self):
        """Should accept enabled flag."""
        from core.schemas.dnd_schemas import DNDStatusDTO
        
        status = DNDStatusDTO(enabled=True)
        
        assert status.enabled is True

    def test_dnd_status_with_duration(self):
        """Should accept duration_ms for timed DND."""
        from core.schemas.dnd_schemas import DNDStatusDTO
        
        status = DNDStatusDTO(
            enabled=True,
            duration_ms=3600000  # 1 hour
        )
        
        assert status.enabled is True
        assert status.duration_ms == 3600000

    def test_dnd_status_requires_enabled(self):
        """Enabled flag is required."""
        from core.schemas.dnd_schemas import DNDStatusDTO
        
        with pytest.raises(ValidationError):
            DNDStatusDTO()

    def test_dnd_status_is_immutable(self):
        """DNDStatusDTO should be frozen (immutable)."""
        from core.schemas.dnd_schemas import DNDStatusDTO
        
        status = DNDStatusDTO(enabled=True)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            status.enabled = False

    def test_dnd_status_with_end_time(self):
        """Should accept optional end_time."""
        from core.schemas.dnd_schemas import DNDStatusDTO
        
        end_time = datetime.now(timezone.utc) + timedelta(hours=2)
        status = DNDStatusDTO(
            enabled=True,
            end_time=end_time
        )
        
        assert status.end_time is not None


class TestSetDNDRequest:
    """Test SetDNDRequest for DND configuration."""

    def test_set_dnd_request_minimal(self):
        """Should accept device_serial_number and enabled."""
        from core.schemas.dnd_schemas import SetDNDRequest
        
        request = SetDNDRequest(
            device_serial_number="SERIALNUMBER123",
            enabled=True
        )
        
        assert request.device_serial_number == "SERIALNUMBER123"
        assert request.enabled is True

    def test_set_dnd_request_with_duration(self):
        """Should accept optional duration."""
        from core.schemas.dnd_schemas import SetDNDRequest
        
        request = SetDNDRequest(
            device_serial_number="SERIALNUMBER123",
            enabled=True,
            duration_ms=3600000
        )
        
        assert request.duration_ms == 3600000

    def test_set_dnd_request_requires_device_serial(self):
        """Device serial number is required."""
        from core.schemas.dnd_schemas import SetDNDRequest
        
        with pytest.raises(ValidationError):
            SetDNDRequest(enabled=True)

    def test_set_dnd_request_requires_enabled(self):
        """Enabled flag is required."""
        from core.schemas.dnd_schemas import SetDNDRequest
        
        with pytest.raises(ValidationError):
            SetDNDRequest(device_serial_number="SERIALNUMBER123")

    def test_set_dnd_request_is_frozen(self):
        """SetDNDRequest should be frozen."""
        from core.schemas.dnd_schemas import SetDNDRequest
        
        request = SetDNDRequest(
            device_serial_number="SERIALNUMBER123",
            enabled=True
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            request.enabled = False


class TestDNDResponse:
    """Test DNDResponse for DND operation results."""

    def test_dnd_response_success(self):
        """Should accept success flag."""
        from core.schemas.dnd_schemas import DNDResponse
        
        response = DNDResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_dnd_response_with_status(self):
        """Should accept optional status."""
        from core.schemas.dnd_schemas import DNDResponse
        
        response = DNDResponse(
            success=True,
            dnd_enabled=True
        )
        
        assert response.dnd_enabled is True

    def test_dnd_response_with_error(self):
        """Should accept error information."""
        from core.schemas.dnd_schemas import DNDResponse
        
        response = DNDResponse(
            success=False,
            error="Failed to set DND",
            error_code="DND_SET_FAILED"
        )
        
        assert response.success is False
        assert response.error == "Failed to set DND"

    def test_dnd_response_requires_success(self):
        """Success field is required."""
        from core.schemas.dnd_schemas import DNDResponse
        
        with pytest.raises(ValidationError):
            DNDResponse()

    def test_dnd_response_auto_sets_created_at(self):
        """Created_at should be auto-set to current UTC time."""
        from core.schemas.dnd_schemas import DNDResponse
        
        before = datetime.now(timezone.utc)
        response = DNDResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after

    def test_dnd_response_is_frozen(self):
        """DNDResponse should be frozen."""
        from core.schemas.dnd_schemas import DNDResponse
        
        response = DNDResponse(success=True)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            response.success = False


class TestDNDWorkflow:
    """Test DND-related workflows."""

    def test_enable_dnd_workflow(self):
        """Should support enable DND workflow."""
        from core.schemas.dnd_schemas import (
            SetDNDRequest,
            DNDResponse
        )
        
        request = SetDNDRequest(
            device_serial_number="DEVICE123",
            enabled=True
        )
        
        response = DNDResponse(success=True, dnd_enabled=True)
        
        assert request.device_serial_number == "DEVICE123"
        assert response.dnd_enabled is True

    def test_disable_dnd_workflow(self):
        """Should support disable DND workflow."""
        from core.schemas.dnd_schemas import (
            SetDNDRequest,
            DNDResponse
        )
        
        request = SetDNDRequest(
            device_serial_number="DEVICE123",
            enabled=False
        )
        
        response = DNDResponse(success=True, dnd_enabled=False)
        
        assert request.enabled is False
        assert response.dnd_enabled is False

    def test_timed_dnd_workflow(self):
        """Should support timed DND (sleep timer)."""
        from core.schemas.dnd_schemas import SetDNDRequest
        
        request = SetDNDRequest(
            device_serial_number="DEVICE123",
            enabled=True,
            duration_ms=1800000  # 30 minutes
        )
        
        assert request.enabled is True
        assert request.duration_ms == 1800000

    def test_dnd_status_field_aliasing(self):
        """Should support camelCase field aliasing."""
        from core.schemas.dnd_schemas import DNDStatusDTO
        
        status_data = {
            "enabled": True,
            "durationMs": 3600000,
            "endTime": datetime.now(timezone.utc)
        }
        
        status = DNDStatusDTO(**status_data)
        
        assert status.enabled is True
        assert status.duration_ms == 3600000
