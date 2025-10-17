"""Communication Schema DTOs - Phase 3.6

DTOs for Alexa communication operations:
- speak/announce commands
- device messaging
- general communication responses

Test Location: Dev/pytests/core/schemas/test_communication_schemas.py
"""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import Field

from core.schemas.base import RequestDTO, ResponseDTO, DomainModel


class SpeakCommandRequest(RequestDTO):
    """Request DTO for speak command."""
    
    device_serial: str = Field(
        ...,
        alias="deviceSerialNumber",
        description="Device serial number"
    )
    text_to_speak: str = Field(
        ...,
        alias="textToSpeak",
        description="Text to speak"
    )


class AnnounceCommandRequest(RequestDTO):
    """Request DTO for announce command."""
    
    device_serial: str = Field(
        ...,
        alias="deviceSerialNumber",
        description="Device serial number"
    )
    message: str = Field(
        ...,
        description="Message to announce"
    )
    title: Optional[str] = Field(
        None,
        description="Optional title/header"
    )


class CommunicationResponse(ResponseDTO):
    """Response DTO for communication commands."""
    
    success: bool = Field(
        default=True,
        description="Whether command succeeded"
    )
    status: str = Field(
        default="executed",
        description="Command status"
    )
    request_id: Optional[str] = Field(
        None,
        alias="requestId",
        description="Request tracking ID"
    )
    device_serial: Optional[str] = Field(
        None,
        alias="deviceSerialNumber",
        description="Device that executed command"
    )
    error_message: Optional[str] = Field(
        None,
        alias="errorMessage",
        description="Error message if failed"
    )


class BroadcastResponse(ResponseDTO):
    """Response DTO for broadcast commands."""
    
    success: bool = Field(
        default=True,
        description="Whether broadcast succeeded"
    )
    devices_targeted: int = Field(
        default=0,
        alias="devicesTargeted",
        description="Number of devices targeted"
    )
    devices_executed: int = Field(
        default=0,
        alias="devicesExecuted",
        description="Number of devices executed"
    )


class ConversationResponse(ResponseDTO):
    """Response DTO for conversation/voice commands."""
    
    transcript: Optional[str] = Field(
        None,
        description="What was heard"
    )
    intent: Optional[str] = Field(
        None,
        description="Recognized intent"
    )
    confidence: Optional[float] = Field(
        None,
        description="Recognition confidence 0-1"
    )
    response_text: Optional[str] = Field(
        None,
        alias="responseText",
        description="Alexa's response text"
    )
