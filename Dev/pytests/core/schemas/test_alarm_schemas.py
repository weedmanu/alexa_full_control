"""
Alarm Schema Tests - Phase 3.5c.2 (TDD)

Tests for alarm-related DTOs.
Covers: alarm creation, alarm management, alarm notifications.

Test Coverage:
- Alarm DTO with time and metadata
- Create alarm requests
- Alarm response with status
- Alarm recurrence patterns
- Alarm serialization and field aliasing
- Alarm validation and constraints

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/alarm_schemas.py
"""

import pytest
from datetime import datetime, time, timedelta, timezone
from typing import Optional, List
from pydantic import ValidationError


class TestAlarmDTO:
    """Test AlarmDTO for alarm metadata."""

    def test_alarm_with_required_fields(self):
        """Should accept alarm_id, label, and time."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        alarm = AlarmDTO(
            alarm_id="alarm123",
            label="Morning Alarm",
            time="07:00:00"
        )
        
        assert alarm.alarm_id == "alarm123"
        assert alarm.label == "Morning Alarm"
        assert alarm.time == "07:00:00"

    def test_alarm_with_optional_fields(self):
        """Should accept optional fields: enabled, recurring, days_of_week."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        alarm = AlarmDTO(
            alarm_id="alarm123",
            label="Morning Alarm",
            time="07:00:00",
            enabled=True,
            recurring=True,
            days_of_week=["MON", "TUE", "WED", "THU", "FRI"]
        )
        
        assert alarm.enabled is True
        assert alarm.recurring is True
        assert len(alarm.days_of_week) == 5

    def test_alarm_requires_alarm_id(self):
        """Alarm ID is required."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        with pytest.raises(ValidationError):
            AlarmDTO(label="Morning Alarm", time="07:00:00")

    def test_alarm_requires_label(self):
        """Label is required."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        with pytest.raises(ValidationError):
            AlarmDTO(alarm_id="alarm123", time="07:00:00")

    def test_alarm_requires_time(self):
        """Time is required."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        with pytest.raises(ValidationError):
            AlarmDTO(alarm_id="alarm123", label="Morning Alarm")

    def test_alarm_is_immutable(self):
        """AlarmDTO should be frozen (immutable)."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        alarm = AlarmDTO(
            alarm_id="alarm123",
            label="Morning Alarm",
            time="07:00:00"
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            alarm.label = "Evening Alarm"


class TestCreateAlarmRequest:
    """Test CreateAlarmRequest for alarm creation."""

    def test_create_alarm_request_minimal(self):
        """Should accept device_serial_number, label, and time."""
        from core.schemas.alarm_schemas import CreateAlarmRequest
        
        request = CreateAlarmRequest(
            device_serial_number="SERIALNUMBER123",
            label="Morning Alarm",
            time="07:00:00"
        )
        
        assert request.device_serial_number == "SERIALNUMBER123"
        assert request.label == "Morning Alarm"
        assert request.time == "07:00:00"

    def test_create_alarm_request_with_recurring(self):
        """Should accept recurring and days_of_week."""
        from core.schemas.alarm_schemas import CreateAlarmRequest
        
        request = CreateAlarmRequest(
            device_serial_number="SERIALNUMBER123",
            label="Work Alarm",
            time="08:30:00",
            recurring=True,
            days_of_week=["MON", "TUE", "WED", "THU", "FRI"]
        )
        
        assert request.recurring is True
        assert len(request.days_of_week) == 5

    def test_create_alarm_requires_device_serial(self):
        """Device serial number is required."""
        from core.schemas.alarm_schemas import CreateAlarmRequest
        
        with pytest.raises(ValidationError):
            CreateAlarmRequest(label="Morning Alarm", time="07:00:00")

    def test_create_alarm_requires_label(self):
        """Label is required."""
        from core.schemas.alarm_schemas import CreateAlarmRequest
        
        with pytest.raises(ValidationError):
            CreateAlarmRequest(device_serial_number="SERIALNUMBER123", time="07:00:00")

    def test_create_alarm_requires_time(self):
        """Time is required."""
        from core.schemas.alarm_schemas import CreateAlarmRequest
        
        with pytest.raises(ValidationError):
            CreateAlarmRequest(device_serial_number="SERIALNUMBER123", label="Morning Alarm")

    def test_create_alarm_request_is_frozen(self):
        """CreateAlarmRequest should be frozen."""
        from core.schemas.alarm_schemas import CreateAlarmRequest
        
        request = CreateAlarmRequest(
            device_serial_number="SERIALNUMBER123",
            label="Morning Alarm",
            time="07:00:00"
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            request.label = "Evening Alarm"


class TestAlarmResponse:
    """Test AlarmResponse for alarm operation results."""

    def test_alarm_response_success(self):
        """Should accept success flag."""
        from core.schemas.alarm_schemas import AlarmResponse
        
        response = AlarmResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_alarm_response_with_alarm_id(self):
        """Should accept alarm_id on success."""
        from core.schemas.alarm_schemas import AlarmResponse
        
        response = AlarmResponse(
            success=True,
            alarm_id="alarm123"
        )
        
        assert response.alarm_id == "alarm123"

    def test_alarm_response_with_error(self):
        """Should accept error information."""
        from core.schemas.alarm_schemas import AlarmResponse
        
        response = AlarmResponse(
            success=False,
            error="Failed to create alarm",
            error_code="ALARM_CREATE_FAILED"
        )
        
        assert response.success is False
        assert response.error == "Failed to create alarm"

    def test_alarm_response_requires_success(self):
        """Success field is required."""
        from core.schemas.alarm_schemas import AlarmResponse
        
        with pytest.raises(ValidationError):
            AlarmResponse()

    def test_alarm_response_auto_sets_created_at(self):
        """Created_at should be auto-set to current UTC time."""
        from core.schemas.alarm_schemas import AlarmResponse
        
        before = datetime.now(timezone.utc)
        response = AlarmResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after

    def test_alarm_response_is_frozen(self):
        """AlarmResponse should be frozen."""
        from core.schemas.alarm_schemas import AlarmResponse
        
        response = AlarmResponse(success=True)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            response.success = False


class TestAlarmWorkflow:
    """Test alarm-related workflows."""

    def test_alarm_list_parsing(self):
        """Should parse list of alarms."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        alarms_data = [
            {"alarmId": "alarm1", "label": "Morning", "time": "07:00:00"},
            {"alarmId": "alarm2", "label": "Evening", "time": "22:00:00"}
        ]
        
        alarms = [AlarmDTO(**alarm) for alarm in alarms_data]
        
        assert len(alarms) == 2
        assert alarms[0].alarm_id == "alarm1"
        assert alarms[1].alarm_id == "alarm2"

    def test_alarm_field_aliasing_from_camel_case(self):
        """Should convert camelCase to snake_case."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        alarm_data = {
            "alarmId": "alarm123",
            "label": "My Alarm",
            "time": "07:00:00",
            "daysOfWeek": ["MON", "TUE"]
        }
        
        alarm = AlarmDTO(**alarm_data)
        
        assert alarm.alarm_id == "alarm123"
        assert alarm.days_of_week == ["MON", "TUE"]

    def test_alarm_serialization_to_camel_case(self):
        """Should serialize to camelCase with aliases."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        alarm = AlarmDTO(
            alarm_id="alarm123",
            label="My Alarm",
            time="07:00:00"
        )
        
        data = alarm.model_dump(by_alias=True)
        
        assert data["alarmId"] == "alarm123"
        assert data["time"] == "07:00:00"

    def test_create_and_respond_alarm(self):
        """Should support complete create alarm workflow."""
        from core.schemas.alarm_schemas import (
            CreateAlarmRequest,
            AlarmResponse
        )
        
        request = CreateAlarmRequest(
            device_serial_number="DEVICE123",
            label="Morning Alarm",
            time="07:00:00",
            recurring=True
        )
        
        response = AlarmResponse(
            success=True,
            alarm_id="alarm456"
        )
        
        assert request.device_serial_number == "DEVICE123"
        assert response.alarm_id == "alarm456"
        assert response.success is True

    def test_alarm_dto_with_all_fields(self):
        """AlarmDTO should support all optional fields."""
        from core.schemas.alarm_schemas import AlarmDTO
        
        alarm = AlarmDTO(
            alarm_id="alarm123",
            label="Complete Alarm",
            time="06:30:00",
            enabled=True,
            recurring=True,
            days_of_week=["MON", "WED", "FRI"],
            sound_uri="https://example.com/alarm.mp3"
        )
        
        assert alarm.enabled is True
        assert alarm.sound_uri == "https://example.com/alarm.mp3"
        assert len(alarm.days_of_week) == 3
