"""Communication Schemas Tests - Phase 3.6 (TDD)

Tests for communication-related DTOs.
Write tests FIRST, then implement schemas.

Test Coverage:
- SpeakCommandRequest with camelCase aliasing
- AnnounceCommandRequest validation
- CommunicationResponse immutability
- BroadcastResponse device counting
- ConversationResponse transcript parsing
- Field aliasing (deviceSerialNumber ↔ device_serial)
- Immutability enforcement
- Auto-timestamping
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from core.schemas.communication_schemas import (
    SpeakCommandRequest,
    AnnounceCommandRequest,
    CommunicationResponse,
    BroadcastResponse,
    ConversationResponse
)


class TestSpeakCommandRequest:
    """Test SpeakCommandRequest DTO."""

    def test_speak_request_from_api_format(self):
        """Should parse Amazon API format with camelCase."""
        api_data = {
            "deviceSerialNumber": "DEVICE001",
            "textToSpeak": "Hello Alexa"
        }
        
        request = SpeakCommandRequest(**api_data)
        
        assert request.device_serial == "DEVICE001"
        assert request.text_to_speak == "Hello Alexa"

    def test_speak_request_from_python_format(self):
        """Should accept python snake_case format."""
        request = SpeakCommandRequest(
            device_serial="DEVICE001",
            text_to_speak="Hello Alexa"
        )
        
        assert request.device_serial == "DEVICE001"
        assert request.text_to_speak == "Hello Alexa"

    def test_speak_request_requires_device_serial(self):
        """device_serial is required."""
        with pytest.raises(ValidationError) as exc_info:
            SpeakCommandRequest(text_to_speak="Hello")
        
        # Error message shows the alias name in Pydantic v2
        assert "deviceSerialNumber" in str(exc_info.value) or "device_serial" in str(exc_info.value)

    def test_speak_request_requires_text(self):
        """text_to_speak is required."""
        with pytest.raises(ValidationError) as exc_info:
            SpeakCommandRequest(device_serial="DEVICE001")
        
        # Error message shows the alias name in Pydantic v2
        assert "textToSpeak" in str(exc_info.value) or "text_to_speak" in str(exc_info.value)

    def test_speak_request_immutable(self):
        """SpeakCommandRequest should be immutable."""
        request = SpeakCommandRequest(
            device_serial="DEVICE001",
            text_to_speak="Hello"
        )
        
        with pytest.raises(Exception):
            request.device_serial = "DEVICE002"

    def test_speak_request_whitespace_stripped(self):
        """Whitespace should be stripped from fields."""
        request = SpeakCommandRequest(
            device_serial="  DEVICE001  ",
            text_to_speak="  Hello  "
        )
        
        assert request.device_serial == "DEVICE001"
        assert request.text_to_speak == "Hello"

    def test_speak_request_extra_fields_forbidden(self):
        """Unknown fields should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpeakCommandRequest(
                device_serial="DEVICE001",
                text_to_speak="Hello",
                unknown_field="value"
            )
        
        assert "extra_forbidden" in str(exc_info.value) or "unknown_field" in str(exc_info.value)


class TestAnnounceCommandRequest:
    """Test AnnounceCommandRequest DTO."""

    def test_announce_request_minimal(self):
        """Announce requires device and message."""
        request = AnnounceCommandRequest(
            device_serial="DEVICE001",
            message="Important update"
        )
        
        assert request.device_serial == "DEVICE001"
        assert request.message == "Important update"
        assert request.title is None

    def test_announce_request_with_title(self):
        """Announce can include optional title."""
        request = AnnounceCommandRequest(
            device_serial="DEVICE001",
            message="Important update",
            title="System Alert"
        )
        
        assert request.title == "System Alert"

    def test_announce_request_camelcase(self):
        """Should accept camelCase deviceSerialNumber."""
        request = AnnounceCommandRequest(
            deviceSerialNumber="DEVICE001",
            message="Test"
        )
        
        assert request.device_serial == "DEVICE001"

    def test_announce_request_requires_message(self):
        """message is required."""
        with pytest.raises(ValidationError):
            AnnounceCommandRequest(device_serial="DEVICE001")


class TestCommunicationResponse:
    """Test CommunicationResponse DTO."""

    def test_communication_response_defaults(self):
        """Response should have sensible defaults."""
        response = CommunicationResponse()
        
        assert response.success is True
        assert response.status == "executed"
        assert response.created_at is not None

    def test_communication_response_with_request_id(self):
        """Should accept requestId (camelCase)."""
        response = CommunicationResponse(
            requestId="req-12345",
            deviceSerialNumber="DEVICE001"
        )
        
        assert response.request_id == "req-12345"
        assert response.device_serial == "DEVICE001"

    def test_communication_response_with_error(self):
        """Response can indicate failure with error message."""
        response = CommunicationResponse(
            success=False,
            status="failed",
            errorMessage="Device offline"
        )
        
        assert response.success is False
        assert response.error_message == "Device offline"

    def test_communication_response_immutable(self):
        """Response should be immutable."""
        response = CommunicationResponse(success=True)
        
        with pytest.raises(Exception):
            response.success = False

    def test_communication_response_auto_timestamps(self):
        """Response should auto-set created_at."""
        before = datetime.now(timezone.utc)
        response = CommunicationResponse()
        after = datetime.now(timezone.utc)
        
        assert before <= response.created_at <= after

    def test_communication_response_forbids_extra_fields(self):
        """Unknown fields should be rejected."""
        with pytest.raises(ValidationError):
            CommunicationResponse(
                success=True,
                unknown_field="value"
            )


class TestBroadcastResponse:
    """Test BroadcastResponse DTO."""

    def test_broadcast_response_defaults(self):
        """Broadcast response defaults."""
        response = BroadcastResponse()
        
        assert response.success is True
        assert response.devices_targeted == 0
        assert response.devices_executed == 0

    def test_broadcast_response_with_counts(self):
        """Should accept device counts."""
        response = BroadcastResponse(
            success=True,
            devicesTargeted=5,
            devicesExecuted=4
        )
        
        assert response.devices_targeted == 5
        assert response.devices_executed == 4

    def test_broadcast_response_camelcase(self):
        """Field names should support camelCase."""
        response = BroadcastResponse(
            devicesTargeted=10,
            devicesExecuted=8
        )
        
        assert response.devices_targeted == 10
        assert response.devices_executed == 8

    def test_broadcast_response_immutable(self):
        """Broadcast response immutable."""
        response = BroadcastResponse(devicesTargeted=5)
        
        with pytest.raises(Exception):
            response.devices_targeted = 10


class TestConversationResponse:
    """Test ConversationResponse DTO."""

    def test_conversation_response_empty(self):
        """All fields optional."""
        response = ConversationResponse()
        
        assert response.transcript is None
        assert response.intent is None
        assert response.confidence is None

    def test_conversation_response_with_transcript(self):
        """Should capture what was heard."""
        response = ConversationResponse(
            transcript="What time is it",
            intent="get_time",
            confidence=0.95,
            responseText="It is 3:45 PM"
        )
        
        assert response.transcript == "What time is it"
        assert response.intent == "get_time"
        assert response.confidence == 0.95
        assert response.response_text == "It is 3:45 PM"

    def test_conversation_response_confidence_range(self):
        """Confidence should be 0-1 but no validation enforced yet."""
        # Note: Could add validators in future
        response = ConversationResponse(confidence=0.5)
        assert response.confidence == 0.5

    def test_conversation_response_camelcase_response_text(self):
        """Should accept responseText (camelCase)."""
        response = ConversationResponse(responseText="Hello there")
        
        assert response.response_text == "Hello there"

    def test_conversation_response_immutable(self):
        """Response immutable."""
        response = ConversationResponse(transcript="test")
        
        with pytest.raises(Exception):
            response.transcript = "modified"

    def test_conversation_response_forbids_extra_fields(self):
        """Unknown fields rejected."""
        with pytest.raises(ValidationError):
            ConversationResponse(
                transcript="test",
                unknown_field="value"
            )
