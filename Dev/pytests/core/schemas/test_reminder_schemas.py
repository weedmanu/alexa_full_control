"""
Reminder Schema Tests - Phase 3.5c.4 (TDD)

Tests for reminder-related DTOs.
Covers: reminder creation, reminder management, reminder notifications.

Test Coverage:
- Reminder DTO with time and metadata
- Create reminder requests
- Reminder response with status
- Reminder state tracking
- Reminder serialization and field aliasing
- Reminder validation and constraints

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/reminder_schemas.py
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import ValidationError


class TestReminderDTO:
    """Test ReminderDTO for reminder metadata."""

    def test_reminder_with_required_fields(self):
        """Should accept reminder_id, label, and trigger_time."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        reminder = ReminderDTO(
            reminder_id="reminder123",
            label="Doctor Appointment",
            trigger_time=datetime.now(timezone.utc) + timedelta(hours=2)
        )
        
        assert reminder.reminder_id == "reminder123"
        assert reminder.label == "Doctor Appointment"
        assert reminder.trigger_time is not None

    def test_reminder_with_optional_fields(self):
        """Should accept optional fields: enabled, description."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        reminder = ReminderDTO(
            reminder_id="reminder123",
            label="Doctor Appointment",
            trigger_time=future,
            enabled=True,
            description="Annual checkup"
        )
        
        assert reminder.enabled is True
        assert reminder.description == "Annual checkup"

    def test_reminder_requires_reminder_id(self):
        """Reminder ID is required."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        with pytest.raises(ValidationError):
            ReminderDTO(
                label="Doctor Appointment",
                trigger_time=datetime.now(timezone.utc)
            )

    def test_reminder_requires_label(self):
        """Label is required."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        with pytest.raises(ValidationError):
            ReminderDTO(
                reminder_id="reminder123",
                trigger_time=datetime.now(timezone.utc)
            )

    def test_reminder_requires_trigger_time(self):
        """Trigger time is required."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        with pytest.raises(ValidationError):
            ReminderDTO(
                reminder_id="reminder123",
                label="Doctor Appointment"
            )

    def test_reminder_is_immutable(self):
        """ReminderDTO should be frozen (immutable)."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        reminder = ReminderDTO(
            reminder_id="reminder123",
            label="Doctor Appointment",
            trigger_time=datetime.now(timezone.utc)
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            reminder.label = "Dentist Appointment"


class TestCreateReminderRequest:
    """Test CreateReminderRequest for reminder creation."""

    def test_create_reminder_request_minimal(self):
        """Should accept device_serial_number, label, and trigger_time."""
        from core.schemas.reminder_schemas import CreateReminderRequest
        
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        request = CreateReminderRequest(
            device_serial_number="SERIALNUMBER123",
            label="Doctor Appointment",
            trigger_time=future
        )
        
        assert request.device_serial_number == "SERIALNUMBER123"
        assert request.label == "Doctor Appointment"

    def test_create_reminder_request_with_description(self):
        """Should accept optional description."""
        from core.schemas.reminder_schemas import CreateReminderRequest
        
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        request = CreateReminderRequest(
            device_serial_number="SERIALNUMBER123",
            label="Doctor Appointment",
            trigger_time=future,
            description="Annual checkup at clinic"
        )
        
        assert request.description == "Annual checkup at clinic"

    def test_create_reminder_requires_device_serial(self):
        """Device serial number is required."""
        from core.schemas.reminder_schemas import CreateReminderRequest
        
        with pytest.raises(ValidationError):
            CreateReminderRequest(
                label="Doctor Appointment",
                trigger_time=datetime.now(timezone.utc)
            )

    def test_create_reminder_requires_label(self):
        """Label is required."""
        from core.schemas.reminder_schemas import CreateReminderRequest
        
        with pytest.raises(ValidationError):
            CreateReminderRequest(
                device_serial_number="SERIALNUMBER123",
                trigger_time=datetime.now(timezone.utc)
            )

    def test_create_reminder_requires_trigger_time(self):
        """Trigger time is required."""
        from core.schemas.reminder_schemas import CreateReminderRequest
        
        with pytest.raises(ValidationError):
            CreateReminderRequest(
                device_serial_number="SERIALNUMBER123",
                label="Doctor Appointment"
            )

    def test_create_reminder_request_is_frozen(self):
        """CreateReminderRequest should be frozen."""
        from core.schemas.reminder_schemas import CreateReminderRequest
        
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        request = CreateReminderRequest(
            device_serial_number="SERIALNUMBER123",
            label="Doctor Appointment",
            trigger_time=future
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            request.label = "Meeting"


class TestReminderResponse:
    """Test ReminderResponse for reminder operation results."""

    def test_reminder_response_success(self):
        """Should accept success flag."""
        from core.schemas.reminder_schemas import ReminderResponse
        
        response = ReminderResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_reminder_response_with_reminder_id(self):
        """Should accept reminder_id on success."""
        from core.schemas.reminder_schemas import ReminderResponse
        
        response = ReminderResponse(
            success=True,
            reminder_id="reminder456"
        )
        
        assert response.reminder_id == "reminder456"

    def test_reminder_response_with_error(self):
        """Should accept error information."""
        from core.schemas.reminder_schemas import ReminderResponse
        
        response = ReminderResponse(
            success=False,
            error="Failed to create reminder",
            error_code="REMINDER_CREATE_FAILED"
        )
        
        assert response.success is False
        assert response.error == "Failed to create reminder"

    def test_reminder_response_requires_success(self):
        """Success field is required."""
        from core.schemas.reminder_schemas import ReminderResponse
        
        with pytest.raises(ValidationError):
            ReminderResponse()

    def test_reminder_response_auto_sets_created_at(self):
        """Created_at should be auto-set to current UTC time."""
        from core.schemas.reminder_schemas import ReminderResponse
        
        before = datetime.now(timezone.utc)
        response = ReminderResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after

    def test_reminder_response_is_frozen(self):
        """ReminderResponse should be frozen."""
        from core.schemas.reminder_schemas import ReminderResponse
        
        response = ReminderResponse(success=True)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            response.success = False


class TestReminderWorkflow:
    """Test reminder-related workflows."""

    def test_reminder_list_parsing(self):
        """Should parse list of reminders."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        now = datetime.now(timezone.utc)
        reminders_data = [
            {
                "reminderId": "reminder1",
                "label": "Doctor",
                "triggerTime": now + timedelta(hours=2)
            },
            {
                "reminderId": "reminder2",
                "label": "Meeting",
                "triggerTime": now + timedelta(days=1)
            }
        ]
        
        reminders = [ReminderDTO(**reminder) for reminder in reminders_data]
        
        assert len(reminders) == 2
        assert reminders[0].reminder_id == "reminder1"
        assert reminders[1].reminder_id == "reminder2"

    def test_reminder_field_aliasing_from_camel_case(self):
        """Should convert camelCase to snake_case."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        reminder_data = {
            "reminderId": "reminder123",
            "label": "My Reminder",
            "triggerTime": future
        }
        
        reminder = ReminderDTO(**reminder_data)
        
        assert reminder.reminder_id == "reminder123"
        assert reminder.trigger_time is not None

    def test_reminder_serialization_to_camel_case(self):
        """Should serialize to camelCase with aliases."""
        from core.schemas.reminder_schemas import ReminderDTO
        
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        reminder = ReminderDTO(
            reminder_id="reminder123",
            label="My Reminder",
            trigger_time=future
        )
        
        data = reminder.model_dump(by_alias=True)
        
        assert data["reminderId"] == "reminder123"
        assert "triggerTime" in data

    def test_create_and_respond_reminder(self):
        """Should support complete create reminder workflow."""
        from core.schemas.reminder_schemas import (
            CreateReminderRequest,
            ReminderResponse
        )
        
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        request = CreateReminderRequest(
            device_serial_number="DEVICE123",
            label="Doctor Appointment",
            trigger_time=future
        )
        
        response = ReminderResponse(
            success=True,
            reminder_id="reminder456"
        )
        
        assert request.device_serial_number == "DEVICE123"
        assert response.reminder_id == "reminder456"
        assert response.success is True
