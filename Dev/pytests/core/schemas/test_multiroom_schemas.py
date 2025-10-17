"""
Multiroom Schema Tests - Phase 3.5c.6 (TDD)

Tests for multiroom audio DTOs.
Covers: room groups, multiroom coordination, audio synchronization.

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/multiroom_schemas.py
"""

import pytest
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import ValidationError


class TestMultiRoomGroupDTO:
    """Test MultiRoomGroupDTO for room groups."""

    def test_multiroom_group_required_fields(self):
        """Should accept group_id and name."""
        from core.schemas.multiroom_schemas import MultiRoomGroupDTO
        
        group = MultiRoomGroupDTO(
            group_id="group123",
            name="Living Room"
        )
        
        assert group.group_id == "group123"
        assert group.name == "Living Room"

    def test_multiroom_group_with_devices(self):
        """Should accept device_serials list."""
        from core.schemas.multiroom_schemas import MultiRoomGroupDTO
        
        group = MultiRoomGroupDTO(
            group_id="group123",
            name="Living Room",
            device_serials=["DEVICE1", "DEVICE2", "DEVICE3"]
        )
        
        assert len(group.device_serials) == 3

    def test_multiroom_group_requires_group_id(self):
        """Group ID is required."""
        from core.schemas.multiroom_schemas import MultiRoomGroupDTO
        
        with pytest.raises(ValidationError):
            MultiRoomGroupDTO(name="Living Room")

    def test_multiroom_group_requires_name(self):
        """Name is required."""
        from core.schemas.multiroom_schemas import MultiRoomGroupDTO
        
        with pytest.raises(ValidationError):
            MultiRoomGroupDTO(group_id="group123")

    def test_multiroom_group_is_immutable(self):
        """MultiRoomGroupDTO should be frozen."""
        from core.schemas.multiroom_schemas import MultiRoomGroupDTO
        
        group = MultiRoomGroupDTO(group_id="group123", name="Living Room")
        
        with pytest.raises(Exception):
            group.name = "Bedroom"


class TestCreateMultiRoomRequest:
    """Test CreateMultiRoomRequest for group creation."""

    def test_create_multiroom_request(self):
        """Should accept device_serials list."""
        from core.schemas.multiroom_schemas import CreateMultiRoomRequest
        
        request = CreateMultiRoomRequest(
            device_serials=["DEVICE1", "DEVICE2"]
        )
        
        assert len(request.device_serials) == 2

    def test_create_multiroom_requires_devices(self):
        """Device serials are required."""
        from core.schemas.multiroom_schemas import CreateMultiRoomRequest
        
        with pytest.raises(ValidationError):
            CreateMultiRoomRequest()

    def test_create_multiroom_request_is_frozen(self):
        """CreateMultiRoomRequest should be frozen."""
        from core.schemas.multiroom_schemas import CreateMultiRoomRequest
        
        request = CreateMultiRoomRequest(device_serials=["DEVICE1", "DEVICE2"])
        
        with pytest.raises(Exception):
            request.device_serials = ["DEVICE3"]


class TestMultiRoomResponse:
    """Test MultiRoomResponse for multiroom operations."""

    def test_multiroom_response_success(self):
        """Should accept success flag."""
        from core.schemas.multiroom_schemas import MultiRoomResponse
        
        response = MultiRoomResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_multiroom_response_with_group_id(self):
        """Should accept group_id on success."""
        from core.schemas.multiroom_schemas import MultiRoomResponse
        
        response = MultiRoomResponse(success=True, group_id="group456")
        
        assert response.group_id == "group456"

    def test_multiroom_response_with_error(self):
        """Should accept error information."""
        from core.schemas.multiroom_schemas import MultiRoomResponse
        
        response = MultiRoomResponse(
            success=False,
            error="Failed to create group",
            error_code="MULTIROOM_CREATE_FAILED"
        )
        
        assert response.success is False

    def test_multiroom_response_requires_success(self):
        """Success field is required."""
        from core.schemas.multiroom_schemas import MultiRoomResponse
        
        with pytest.raises(ValidationError):
            MultiRoomResponse()

    def test_multiroom_response_auto_sets_created_at(self):
        """Created_at should be auto-set."""
        from core.schemas.multiroom_schemas import MultiRoomResponse
        
        before = datetime.now(timezone.utc)
        response = MultiRoomResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after


class TestMultiRoomWorkflow:
    """Test multiroom workflows."""

    def test_create_multiroom_workflow(self):
        """Should support complete multiroom workflow."""
        from core.schemas.multiroom_schemas import (
            CreateMultiRoomRequest,
            MultiRoomResponse
        )
        
        request = CreateMultiRoomRequest(
            device_serials=["DEVICE1", "DEVICE2", "DEVICE3"]
        )
        
        response = MultiRoomResponse(success=True, group_id="group123")
        
        assert len(request.device_serials) == 3
        assert response.group_id == "group123"

    def test_multiroom_group_field_aliasing(self):
        """Should support camelCase field aliasing."""
        from core.schemas.multiroom_schemas import MultiRoomGroupDTO
        
        group_data = {
            "groupId": "group123",
            "name": "Living Room",
            "deviceSerials": ["DEVICE1", "DEVICE2"]
        }
        
        group = MultiRoomGroupDTO(**group_data)
        
        assert group.group_id == "group123"
        assert len(group.device_serials) == 2
