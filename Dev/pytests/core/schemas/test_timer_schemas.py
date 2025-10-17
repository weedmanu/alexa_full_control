"""
Timer Schema Tests - Phase 3.5c.3 (TDD)

Tests for timer-related DTOs.
Covers: timer creation, timer management, timer notifications.

Test Coverage:
- Timer DTO with duration and metadata
- Create timer requests
- Timer response with status
- Timer state tracking
- Timer serialization and field aliasing
- Timer validation and constraints

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/timer_schemas.py
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import ValidationError


class TestTimerDTO:
    """Test TimerDTO for timer metadata."""

    def test_timer_with_required_fields(self):
        """Should accept timer_id, label, and duration_ms."""
        from core.schemas.timer_schemas import TimerDTO
        
        timer = TimerDTO(
            timer_id="timer123",
            label="Cooking Timer",
            duration_ms=300000  # 5 minutes
        )
        
        assert timer.timer_id == "timer123"
        assert timer.label == "Cooking Timer"
        assert timer.duration_ms == 300000

    def test_timer_with_optional_fields(self):
        """Should accept optional fields: state, remaining_ms."""
        from core.schemas.timer_schemas import TimerDTO
        
        timer = TimerDTO(
            timer_id="timer123",
            label="Cooking Timer",
            duration_ms=300000,
            state="RUNNING",
            remaining_ms=250000
        )
        
        assert timer.state == "RUNNING"
        assert timer.remaining_ms == 250000

    def test_timer_requires_timer_id(self):
        """Timer ID is required."""
        from core.schemas.timer_schemas import TimerDTO
        
        with pytest.raises(ValidationError):
            TimerDTO(label="Cooking Timer", duration_ms=300000)

    def test_timer_requires_label(self):
        """Label is required."""
        from core.schemas.timer_schemas import TimerDTO
        
        with pytest.raises(ValidationError):
            TimerDTO(timer_id="timer123", duration_ms=300000)

    def test_timer_requires_duration_ms(self):
        """Duration in milliseconds is required."""
        from core.schemas.timer_schemas import TimerDTO
        
        with pytest.raises(ValidationError):
            TimerDTO(timer_id="timer123", label="Cooking Timer")

    def test_timer_duration_must_be_positive(self):
        """Duration must be positive."""
        from core.schemas.timer_schemas import TimerDTO
        
        with pytest.raises(ValidationError):
            TimerDTO(timer_id="timer123", label="Timer", duration_ms=0)

    def test_timer_is_immutable(self):
        """TimerDTO should be frozen (immutable)."""
        from core.schemas.timer_schemas import TimerDTO
        
        timer = TimerDTO(
            timer_id="timer123",
            label="Cooking Timer",
            duration_ms=300000
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            timer.label = "Boiling Timer"


class TestCreateTimerRequest:
    """Test CreateTimerRequest for timer creation."""

    def test_create_timer_request_minimal(self):
        """Should accept device_serial_number, label, and duration_ms."""
        from core.schemas.timer_schemas import CreateTimerRequest
        
        request = CreateTimerRequest(
            device_serial_number="SERIALNUMBER123",
            label="Cooking",
            duration_ms=300000
        )
        
        assert request.device_serial_number == "SERIALNUMBER123"
        assert request.label == "Cooking"
        assert request.duration_ms == 300000

    def test_create_timer_request_with_optional_fields(self):
        """Should accept optional fields."""
        from core.schemas.timer_schemas import CreateTimerRequest
        
        request = CreateTimerRequest(
            device_serial_number="SERIALNUMBER123",
            label="Cooking",
            duration_ms=600000,
            sound_uri="https://example.com/timer.mp3"
        )
        
        assert request.sound_uri == "https://example.com/timer.mp3"

    def test_create_timer_requires_device_serial(self):
        """Device serial number is required."""
        from core.schemas.timer_schemas import CreateTimerRequest
        
        with pytest.raises(ValidationError):
            CreateTimerRequest(label="Cooking", duration_ms=300000)

    def test_create_timer_requires_label(self):
        """Label is required."""
        from core.schemas.timer_schemas import CreateTimerRequest
        
        with pytest.raises(ValidationError):
            CreateTimerRequest(device_serial_number="SERIALNUMBER123", duration_ms=300000)

    def test_create_timer_requires_duration(self):
        """Duration is required."""
        from core.schemas.timer_schemas import CreateTimerRequest
        
        with pytest.raises(ValidationError):
            CreateTimerRequest(device_serial_number="SERIALNUMBER123", label="Cooking")

    def test_create_timer_duration_must_be_positive(self):
        """Duration must be positive."""
        from core.schemas.timer_schemas import CreateTimerRequest
        
        with pytest.raises(ValidationError):
            CreateTimerRequest(
                device_serial_number="SERIALNUMBER123",
                label="Cooking",
                duration_ms=0
            )

    def test_create_timer_request_is_frozen(self):
        """CreateTimerRequest should be frozen."""
        from core.schemas.timer_schemas import CreateTimerRequest
        
        request = CreateTimerRequest(
            device_serial_number="SERIALNUMBER123",
            label="Cooking",
            duration_ms=300000
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            request.label = "Baking"


class TestTimerResponse:
    """Test TimerResponse for timer operation results."""

    def test_timer_response_success(self):
        """Should accept success flag."""
        from core.schemas.timer_schemas import TimerResponse
        
        response = TimerResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_timer_response_with_timer_id(self):
        """Should accept timer_id on success."""
        from core.schemas.timer_schemas import TimerResponse
        
        response = TimerResponse(
            success=True,
            timer_id="timer123"
        )
        
        assert response.timer_id == "timer123"

    def test_timer_response_with_error(self):
        """Should accept error information."""
        from core.schemas.timer_schemas import TimerResponse
        
        response = TimerResponse(
            success=False,
            error="Failed to create timer",
            error_code="TIMER_CREATE_FAILED"
        )
        
        assert response.success is False
        assert response.error == "Failed to create timer"

    def test_timer_response_requires_success(self):
        """Success field is required."""
        from core.schemas.timer_schemas import TimerResponse
        
        with pytest.raises(ValidationError):
            TimerResponse()

    def test_timer_response_auto_sets_created_at(self):
        """Created_at should be auto-set to current UTC time."""
        from core.schemas.timer_schemas import TimerResponse
        
        before = datetime.now(timezone.utc)
        response = TimerResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after

    def test_timer_response_is_frozen(self):
        """TimerResponse should be frozen."""
        from core.schemas.timer_schemas import TimerResponse
        
        response = TimerResponse(success=True)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            response.success = False


class TestTimerWorkflow:
    """Test timer-related workflows."""

    def test_timer_list_parsing(self):
        """Should parse list of timers."""
        from core.schemas.timer_schemas import TimerDTO
        
        timers_data = [
            {"timerId": "timer1", "label": "Cooking", "durationMs": 300000},
            {"timerId": "timer2", "label": "Laundry", "durationMs": 1800000}
        ]
        
        timers = [TimerDTO(**timer) for timer in timers_data]
        
        assert len(timers) == 2
        assert timers[0].timer_id == "timer1"
        assert timers[1].timer_id == "timer2"

    def test_timer_field_aliasing_from_camel_case(self):
        """Should convert camelCase to snake_case."""
        from core.schemas.timer_schemas import TimerDTO
        
        timer_data = {
            "timerId": "timer123",
            "label": "Cooking",
            "durationMs": 300000,
            "remainingMs": 250000
        }
        
        timer = TimerDTO(**timer_data)
        
        assert timer.timer_id == "timer123"
        assert timer.duration_ms == 300000
        assert timer.remaining_ms == 250000

    def test_timer_serialization_to_camel_case(self):
        """Should serialize to camelCase with aliases."""
        from core.schemas.timer_schemas import TimerDTO
        
        timer = TimerDTO(
            timer_id="timer123",
            label="Cooking",
            duration_ms=300000
        )
        
        data = timer.model_dump(by_alias=True)
        
        assert data["timerId"] == "timer123"
        assert data["durationMs"] == 300000

    def test_create_and_respond_timer(self):
        """Should support complete create timer workflow."""
        from core.schemas.timer_schemas import (
            CreateTimerRequest,
            TimerResponse
        )
        
        request = CreateTimerRequest(
            device_serial_number="DEVICE123",
            label="Cooking",
            duration_ms=600000
        )
        
        response = TimerResponse(
            success=True,
            timer_id="timer456"
        )
        
        assert request.device_serial_number == "DEVICE123"
        assert response.timer_id == "timer456"
        assert response.success is True

    def test_timer_running_state(self):
        """Timer should track running state."""
        from core.schemas.timer_schemas import TimerDTO
        
        running_timer = TimerDTO(
            timer_id="timer1",
            label="Cooking",
            duration_ms=300000,
            state="RUNNING",
            remaining_ms=150000
        )
        
        paused_timer = TimerDTO(
            timer_id="timer2",
            label="Baking",
            duration_ms=600000,
            state="PAUSED",
            remaining_ms=300000
        )
        
        assert running_timer.state == "RUNNING"
        assert paused_timer.state == "PAUSED"
        assert running_timer.remaining_ms < running_timer.duration_ms
