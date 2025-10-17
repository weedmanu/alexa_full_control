"""
Alarm Schemas - Phase 3.5c.2

Data Transfer Objects (DTOs) for alarm-related API operations.

Classes:
- AlarmDTO: Alarm metadata and configuration
- CreateAlarmRequest: Request to create an alarm
- AlarmResponse: Response from alarm operations

API Endpoints Covered:
- GET /api/alarms: List all alarms
- POST /api/alarms: Create a new alarm
- PUT /api/alarms/{alarmId}: Update alarm
- DELETE /api/alarms/{alarmId}: Delete alarm
"""

from typing import Optional, List
from pydantic import Field, ConfigDict

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class AlarmDTO(DomainModel):
    """
    Data model for an alarm.
    
    Immutable domain model for alarm metadata and configuration.
    
    Attributes:
        alarm_id: Unique identifier for the alarm
        label: Human-readable alarm label/name
        time: Time for the alarm (HH:MM:SS format)
        enabled: Whether the alarm is active (default: True)
        recurring: Whether the alarm is recurring (default: False)
        days_of_week: List of days for recurring alarms (MON, TUE, etc.)
        sound_uri: Optional custom alarm sound URI
    
    Example:
        >>> alarm = AlarmDTO(
        ...     alarm_id="alarm123",
        ...     label="Morning Alarm",
        ...     time="07:00:00",
        ...     enabled=True,
        ...     recurring=True,
        ...     days_of_week=["MON", "TUE", "WED", "THU", "FRI"]
        ... )
    """
    
    alarm_id: str = Field(..., alias="alarmId")
    label: str
    time: str
    enabled: bool = True
    recurring: bool = False
    days_of_week: List[str] = Field(default_factory=list, alias="daysOfWeek")
    sound_uri: Optional[str] = Field(None, alias="soundUri")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class CreateAlarmRequest(RequestDTO):
    """
    Request to create a new alarm.
    
    Immutable request DTO for alarm creation.
    
    Attributes:
        device_serial_number: Serial number of the target device
        label: Alarm label/name
        time: Time for the alarm (HH:MM:SS format)
        recurring: Whether the alarm should be recurring (default: False)
        days_of_week: Days for recurring alarms
        sound_uri: Optional custom alarm sound
    
    Example:
        >>> request = CreateAlarmRequest(
        ...     device_serial_number="SERIALNUMBER123",
        ...     label="Morning Alarm",
        ...     time="07:00:00",
        ...     recurring=True,
        ...     days_of_week=["MON", "TUE", "WED"]
        ... )
    """
    
    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    label: str
    time: str
    recurring: bool = False
    days_of_week: List[str] = Field(default_factory=list, alias="daysOfWeek")
    sound_uri: Optional[str] = Field(None, alias="soundUri")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class AlarmResponse(ResponseDTO):
    """
    Response from alarm operation.
    
    Immutable response DTO with automatic timestamp.
    
    Attributes:
        success: Whether the operation succeeded
        alarm_id: ID of the created/modified alarm (on success)
        error: Optional error description
        error_code: Optional error code identifier
        created_at: Timestamp of response creation (auto-set)
    
    Example:
        >>> response = AlarmResponse(
        ...     success=True,
        ...     alarm_id="alarm456"
        ... )
    """
    
    success: bool
    alarm_id: Optional[str] = Field(None, alias="alarmId")
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class GetAlarmsResponse(ResponseDTO):
    """
    Response containing list of all alarms.
    
    Response DTO for GET /api/alarms endpoint.
    
    Attributes:
        alarms: List of AlarmDTO objects
    
    Example:
        >>> response = GetAlarmsResponse(
        ...     alarms=[
        ...         AlarmDTO(alarm_id="a1", label="Morning", time="07:00:00", enabled=True)
        ...     ]
        ... )
    """
    
    alarms: list[AlarmDTO] = Field(default_factory=list)
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )

