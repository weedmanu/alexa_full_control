"""
Lists Schema Tests - Phase 3.5c.8 (TDD)

Tests for shopping list DTOs.
Covers: list management, list items, list operations.

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/list_schemas.py
"""

import pytest
from datetime import datetime, timezone
from typing import Optional, List as ListType
from pydantic import ValidationError


class TestListDTO:
    """Test ListDTO for list metadata."""

    def test_list_required_fields(self):
        """Should accept list_id and name."""
        from core.schemas.list_schemas import ListDTO
        
        lst = ListDTO(list_id="list123", name="Shopping")
        
        assert lst.list_id == "list123"
        assert lst.name == "Shopping"

    def test_list_with_items(self):
        """Should accept items list."""
        from core.schemas.list_schemas import ListDTO
        
        lst = ListDTO(
            list_id="list123",
            name="Shopping",
            items=["milk", "eggs", "bread"]
        )
        
        assert len(lst.items) == 3

    def test_list_requires_id(self):
        """ID is required."""
        from core.schemas.list_schemas import ListDTO
        
        with pytest.raises(ValidationError):
            ListDTO(name="Shopping")

    def test_list_requires_name(self):
        """Name is required."""
        from core.schemas.list_schemas import ListDTO
        
        with pytest.raises(ValidationError):
            ListDTO(list_id="list123")

    def test_list_is_immutable(self):
        """ListDTO should be frozen."""
        from core.schemas.list_schemas import ListDTO
        
        lst = ListDTO(list_id="list123", name="Shopping")
        
        with pytest.raises(Exception):
            lst.name = "Groceries"


class TestCreateListRequest:
    """Test CreateListRequest."""

    def test_create_list_request(self):
        """Should accept device_serial_number and name."""
        from core.schemas.list_schemas import CreateListRequest
        
        request = CreateListRequest(
            device_serial_number="DEVICE123",
            name="Shopping"
        )
        
        assert request.device_serial_number == "DEVICE123"
        assert request.name == "Shopping"

    def test_create_list_requires_device(self):
        """Device is required."""
        from core.schemas.list_schemas import CreateListRequest
        
        with pytest.raises(ValidationError):
            CreateListRequest(name="Shopping")

    def test_create_list_requires_name(self):
        """Name is required."""
        from core.schemas.list_schemas import CreateListRequest
        
        with pytest.raises(ValidationError):
            CreateListRequest(device_serial_number="DEVICE123")


class TestListResponse:
    """Test ListResponse."""

    def test_list_response_success(self):
        """Should accept success flag."""
        from core.schemas.list_schemas import ListResponse
        
        response = ListResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_list_response_with_list_id(self):
        """Should accept list_id on success."""
        from core.schemas.list_schemas import ListResponse
        
        response = ListResponse(success=True, list_id="list456")
        
        assert response.list_id == "list456"

    def test_list_response_with_error(self):
        """Should accept error information."""
        from core.schemas.list_schemas import ListResponse
        
        response = ListResponse(
            success=False,
            error="Failed to create"
        )
        
        assert response.success is False

    def test_list_response_requires_success(self):
        """Success field is required."""
        from core.schemas.list_schemas import ListResponse
        
        with pytest.raises(ValidationError):
            ListResponse()

    def test_list_response_auto_sets_created_at(self):
        """Created_at should be auto-set."""
        from core.schemas.list_schemas import ListResponse
        
        before = datetime.now(timezone.utc)
        response = ListResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after


class TestListWorkflow:
    """Test list workflows."""

    def test_create_list_workflow(self):
        """Should support complete create list workflow."""
        from core.schemas.list_schemas import (
            CreateListRequest,
            ListResponse
        )
        
        request = CreateListRequest(
            device_serial_number="DEVICE123",
            name="Shopping"
        )
        
        response = ListResponse(success=True, list_id="list456")
        
        assert request.device_serial_number == "DEVICE123"
        assert response.list_id == "list456"

    def test_list_field_aliasing(self):
        """Should support camelCase field aliasing."""
        from core.schemas.list_schemas import ListDTO
        
        list_data = {
            "listId": "list123",
            "name": "Shopping",
            "items": ["milk", "eggs"]
        }
        
        lst = ListDTO(**list_data)
        
        assert lst.list_id == "list123"
        assert len(lst.items) == 2
