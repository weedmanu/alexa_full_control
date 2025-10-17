"""
Calendar Schemas - Phase 3.5c.9

Data Transfer Objects (DTOs) for calendar operations.

Classes:
- CalendarEventDTO: Calendar event metadata
- EventRequest: Request for calendar operations
- CalendarResponse: Response from calendar operations

API Endpoints Covered:
- GET /api/calendar/events: List events
- POST /api/calendar/events: Create event
- PUT /api/calendar/events/{eventId}: Update event
- DELETE /api/calendar/events/{eventId}: Delete event
"""

from typing import Optional
from datetime import datetime
from pydantic import Field, ConfigDict

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class CalendarEventDTO(DomainModel):
    """Data model for a calendar event."""
    
    event_id: str = Field(..., alias="eventId")
    title: str
    start_time: datetime = Field(..., alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    description: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class EventRequest(RequestDTO):
    """Request for calendar operations."""
    
    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    title: str
    start_time: datetime = Field(..., alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class CalendarResponse(ResponseDTO):
    """Response from calendar operation."""
    
    success: bool
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )
