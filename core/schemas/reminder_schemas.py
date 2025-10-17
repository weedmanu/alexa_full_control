"""
Reminder Schemas - Phase 3.5c.4

Data Transfer Objects (DTOs) for reminder-related API operations.

Classes:
- ReminderDTO: Reminder metadata and configuration
- CreateReminderRequest: Request to create a reminder
- ReminderResponse: Response from reminder operations

API Endpoints Covered:
- GET /api/reminders: List all reminders
- POST /api/reminders: Create a new reminder
- PUT /api/reminders/{reminderId}: Update reminder
- DELETE /api/reminders/{reminderId}: Delete reminder
"""

from typing import Optional
from datetime import datetime
from pydantic import Field, ConfigDict

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class ReminderDTO(DomainModel):
    """
    Data model for a reminder.
    
    Immutable domain model for reminder metadata and configuration.
    
    Attributes:
        reminder_id: Unique identifier for the reminder
        label: Human-readable reminder label/name
        trigger_time: Time when the reminder should trigger
        enabled: Whether the reminder is active (default: True)
        description: Optional description of what the reminder is for
    
    Example:
        >>> reminder = ReminderDTO(
        ...     reminder_id="reminder123",
        ...     label="Doctor Appointment",
        ...     trigger_time=datetime.now(timezone.utc),
        ...     enabled=True,
        ...     description="Annual checkup"
        ... )
    """
    
    reminder_id: str = Field(..., alias="reminderId")
    label: str
    trigger_time: datetime = Field(..., alias="triggerTime")
    enabled: bool = True
    description: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class CreateReminderRequest(RequestDTO):
    """
    Request to create a new reminder.
    
    Immutable request DTO for reminder creation.
    
    Attributes:
        device_serial_number: Serial number of the target device
        label: Reminder label/name
        trigger_time: Time when the reminder should trigger
        description: Optional description
    
    Example:
        >>> request = CreateReminderRequest(
        ...     device_serial_number="SERIALNUMBER123",
        ...     label="Doctor Appointment",
        ...     trigger_time=datetime.now(timezone.utc)
        ... )
    """
    
    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    label: str
    trigger_time: datetime = Field(..., alias="triggerTime")
    description: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class ReminderResponse(ResponseDTO):
    """
    Response from reminder operation.
    
    Immutable response DTO with automatic timestamp.
    
    Attributes:
        success: Whether the operation succeeded
        reminder_id: ID of the created/modified reminder (on success)
        error: Optional error description
        error_code: Optional error code identifier
        created_at: Timestamp of response creation (auto-set)
    
    Example:
        >>> response = ReminderResponse(
        ...     success=True,
        ...     reminder_id="reminder456"
        ... )
    """
    
    success: bool
    reminder_id: Optional[str] = Field(None, alias="reminderId")
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )
