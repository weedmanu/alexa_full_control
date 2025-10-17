"""
Routine Schema Tests - Phase 3.5c.1 (TDD)

Tests for routine-related DTOs.
Covers: routine execution, routine management, automation workflows.

Test Coverage:
- Routine DTO with metadata and triggers
- Execute routine requests
- Routine response with status
- Routine activation/deactivation
- Routine serialization and field aliasing
- Routine validation and constraints

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/routine_schemas.py
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from pydantic import ValidationError


class TestRoutineDTO:
    """Test RoutineDTO for routine metadata."""

    def test_routine_with_required_fields(self):
        """Should accept routine_id, name, and enabled."""
        from core.schemas.routine_schemas import RoutineDTO
        
        routine = RoutineDTO(
            routine_id="routine123",
            name="Morning Routine",
            enabled=True
        )
        
        assert routine.routine_id == "routine123"
        assert routine.name == "Morning Routine"
        assert routine.enabled is True

    def test_routine_with_optional_fields(self):
        """Should accept optional fields: description, serialized, automation_type."""
        from core.schemas.routine_schemas import RoutineDTO
        
        routine = RoutineDTO(
            routine_id="routine123",
            name="Morning Routine",
            enabled=True,
            description="Start the day",
            serialized="MORNING_ROUTINE",
            automation_type="TIME_OF_DAY"
        )
        
        assert routine.description == "Start the day"
        assert routine.serialized == "MORNING_ROUTINE"
        assert routine.automation_type == "TIME_OF_DAY"

    def test_routine_requires_routine_id(self):
        """Routine ID is required."""
        from core.schemas.routine_schemas import RoutineDTO
        
        with pytest.raises(ValidationError):
            RoutineDTO(name="Morning Routine", enabled=True)

    def test_routine_requires_name(self):
        """Name is required."""
        from core.schemas.routine_schemas import RoutineDTO
        
        with pytest.raises(ValidationError):
            RoutineDTO(routine_id="routine123", enabled=True)

    def test_routine_requires_enabled(self):
        """Enabled flag is required."""
        from core.schemas.routine_schemas import RoutineDTO
        
        with pytest.raises(ValidationError):
            RoutineDTO(routine_id="routine123", name="Morning Routine")

    def test_routine_is_immutable(self):
        """RoutineDTO should be frozen (immutable)."""
        from core.schemas.routine_schemas import RoutineDTO
        
        routine = RoutineDTO(
            routine_id="routine123",
            name="Morning Routine",
            enabled=True
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            routine.name = "Evening Routine"


class TestExecuteRoutineRequest:
    """Test ExecuteRoutineRequest for routine execution."""

    def test_execute_routine_request(self):
        """Should accept device_serial_number and routine_id."""
        from core.schemas.routine_schemas import ExecuteRoutineRequest
        
        request = ExecuteRoutineRequest(
            device_serial_number="SERIALNUMBER123",
            routine_id="routine123"
        )
        
        assert request.device_serial_number == "SERIALNUMBER123"
        assert request.routine_id == "routine123"

    def test_execute_routine_requires_device_serial(self):
        """Device serial number is required."""
        from core.schemas.routine_schemas import ExecuteRoutineRequest
        
        with pytest.raises(ValidationError):
            ExecuteRoutineRequest(routine_id="routine123")

    def test_execute_routine_requires_routine_id(self):
        """Routine ID is required."""
        from core.schemas.routine_schemas import ExecuteRoutineRequest
        
        with pytest.raises(ValidationError):
            ExecuteRoutineRequest(device_serial_number="SERIALNUMBER123")

    def test_execute_routine_request_is_frozen(self):
        """ExecuteRoutineRequest should be frozen."""
        from core.schemas.routine_schemas import ExecuteRoutineRequest
        
        request = ExecuteRoutineRequest(
            device_serial_number="SERIALNUMBER123",
            routine_id="routine123"
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            request.routine_id = "routine456"


class TestRoutineResponse:
    """Test RoutineResponse for routine execution results."""

    def test_routine_response_success(self):
        """Should accept success flag and optional message."""
        from core.schemas.routine_schemas import RoutineResponse
        
        response = RoutineResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None
        assert isinstance(response.created_at, datetime)

    def test_routine_response_with_message(self):
        """Should accept optional message."""
        from core.schemas.routine_schemas import RoutineResponse
        
        response = RoutineResponse(
            success=True,
            message="Routine executed successfully"
        )
        
        assert response.message == "Routine executed successfully"

    def test_routine_response_with_error(self):
        """Should accept error information."""
        from core.schemas.routine_schemas import RoutineResponse
        
        response = RoutineResponse(
            success=False,
            error="Routine not found",
            error_code="ROUTINE_NOT_FOUND"
        )
        
        assert response.success is False
        assert response.error == "Routine not found"
        assert response.error_code == "ROUTINE_NOT_FOUND"

    def test_routine_response_requires_success(self):
        """Success field is required."""
        from core.schemas.routine_schemas import RoutineResponse
        
        with pytest.raises(ValidationError):
            RoutineResponse()

    def test_routine_response_auto_sets_created_at(self):
        """Created_at should be auto-set to current UTC time."""
        from core.schemas.routine_schemas import RoutineResponse
        
        before = datetime.now(timezone.utc)
        response = RoutineResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after

    def test_routine_response_is_frozen(self):
        """RoutineResponse should be frozen."""
        from core.schemas.routine_schemas import RoutineResponse
        
        response = RoutineResponse(success=True)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            response.success = False


class TestRoutineWorkflow:
    """Test routine execution workflows."""

    def test_routine_list_parsing(self):
        """Should parse list of routines."""
        from core.schemas.routine_schemas import RoutineDTO
        
        routines_data = [
            {
                "routineId": "routine1",
                "name": "Morning Routine",
                "enabled": True
            },
            {
                "routineId": "routine2",
                "name": "Evening Routine",
                "enabled": False
            }
        ]
        
        routines = [RoutineDTO(**routine) for routine in routines_data]
        
        assert len(routines) == 2
        assert routines[0].routine_id == "routine1"
        assert routines[1].routine_id == "routine2"

    def test_routine_field_aliasing_from_camel_case(self):
        """Should convert camelCase to snake_case."""
        from core.schemas.routine_schemas import RoutineDTO
        
        routine_data = {
            "routineId": "routine123",
            "name": "My Routine",
            "enabled": True,
            "automationType": "TIME_OF_DAY"
        }
        
        routine = RoutineDTO(**routine_data)
        
        assert routine.routine_id == "routine123"
        assert routine.automation_type == "TIME_OF_DAY"

    def test_routine_serialization_to_camel_case(self):
        """Should serialize to camelCase with aliases."""
        from core.schemas.routine_schemas import RoutineDTO
        
        routine = RoutineDTO(
            routine_id="routine123",
            name="My Routine",
            enabled=True
        )
        
        data = routine.model_dump(by_alias=True)
        
        assert data["routineId"] == "routine123"
        assert data["name"] == "My Routine"
        assert data["enabled"] is True

    def test_routine_response_with_executed_routine(self):
        """Should support complete workflow."""
        from core.schemas.routine_schemas import (
            ExecuteRoutineRequest,
            RoutineResponse
        )
        
        request = ExecuteRoutineRequest(
            device_serial_number="DEVICE123",
            routine_id="routine123"
        )
        
        response = RoutineResponse(
            success=True,
            message="Routine executed"
        )
        
        assert request.device_serial_number == "DEVICE123"
        assert response.success is True
