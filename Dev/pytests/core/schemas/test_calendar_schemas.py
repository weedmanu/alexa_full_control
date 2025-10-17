"""
Calendar Schema Tests - Phase 3.5c.9 (TDD)

Tests for calendar event DTOs.
Covers: event management, calendar operations.

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/calendar_schemas.py
"""

import pytest
from datetime import datetime, timezone
from typing import Optional
from pydantic import ValidationError


class TestCalendarEventDTO:
    """Test CalendarEventDTO."""

    def test_event_required_fields(self):
        """Should accept event_id, title, start_time."""
        from core.schemas.calendar_schemas import CalendarEventDTO
        
        now = datetime.now(timezone.utc)
        event = CalendarEventDTO(
            event_id="event123",
            title="Meeting",
            start_time=now
        )
        
        assert event.event_id == "event123"
        assert event.title == "Meeting"

    def test_event_with_end_time(self):
        """Should accept optional end_time."""
        from core.schemas.calendar_schemas import CalendarEventDTO
        
        now = datetime.now(timezone.utc)
        event = CalendarEventDTO(
            event_id="event123",
            title="Meeting",
            start_time=now,
            end_time=now
        )
        
        assert event.end_time is not None

    def test_event_requires_id(self):
        """ID is required."""
        from core.schemas.calendar_schemas import CalendarEventDTO
        
        with pytest.raises(ValidationError):
            CalendarEventDTO(title="Meeting", start_time=datetime.now(timezone.utc))

    def test_event_is_immutable(self):
        """CalendarEventDTO should be frozen."""
        from core.schemas.calendar_schemas import CalendarEventDTO
        
        now = datetime.now(timezone.utc)
        event = CalendarEventDTO(event_id="event123", title="Meeting", start_time=now)
        
        with pytest.raises(Exception):
            event.title = "Presentation"


class TestEventRequest:
    """Test EventRequest."""

    def test_event_request(self):
        """Should accept device_serial_number."""
        from core.schemas.calendar_schemas import EventRequest
        
        now = datetime.now(timezone.utc)
        request = EventRequest(
            device_serial_number="DEVICE123",
            title="Meeting",
            start_time=now
        )
        
        assert request.device_serial_number == "DEVICE123"

    def test_event_request_requires_device(self):
        """Device is required."""
        from core.schemas.calendar_schemas import EventRequest
        
        with pytest.raises(ValidationError):
            EventRequest(title="Meeting", start_time=datetime.now(timezone.utc))


class TestCalendarResponse:
    """Test CalendarResponse."""

    def test_calendar_response_success(self):
        """Should accept success flag."""
        from core.schemas.calendar_schemas import CalendarResponse
        
        response = CalendarResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_calendar_response_with_error(self):
        """Should accept error information."""
        from core.schemas.calendar_schemas import CalendarResponse
        
        response = CalendarResponse(success=False, error="Failed")
        
        assert response.success is False

    def test_calendar_response_requires_success(self):
        """Success field is required."""
        from core.schemas.calendar_schemas import CalendarResponse
        
        with pytest.raises(ValidationError):
            CalendarResponse()


class TestCalendarWorkflow:
    """Test calendar workflows."""

    def test_calendar_event_workflow(self):
        """Should support complete event workflow."""
        from core.schemas.calendar_schemas import (
            EventRequest,
            CalendarResponse
        )
        
        now = datetime.now(timezone.utc)
        request = EventRequest(
            device_serial_number="DEVICE123",
            title="Meeting",
            start_time=now
        )
        
        response = CalendarResponse(success=True)
        
        assert request.device_serial_number == "DEVICE123"
        assert response.success is True

    def test_event_field_aliasing(self):
        """Should support camelCase field aliasing."""
        from core.schemas.calendar_schemas import CalendarEventDTO
        
        now = datetime.now(timezone.utc)
        event_data = {
            "eventId": "event123",
            "title": "Meeting",
            "startTime": now
        }
        
        event = CalendarEventDTO(**event_data)
        
        assert event.event_id == "event123"
