"""
Timer Schemas - Phase 3.5c.3

Data Transfer Objects (DTOs) for timer-related API operations.

Classes:
- TimerDTO: Timer metadata and state
- CreateTimerRequest: Request to create a timer
- TimerResponse: Response from timer operations

API Endpoints Covered:
- GET /api/timers: List all active timers
- POST /api/timers: Create a new timer
- PUT /api/timers/{timerId}: Update timer
- DELETE /api/timers/{timerId}: Delete timer
"""

from typing import Optional

from pydantic import ConfigDict, Field, field_validator

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class TimerDTO(DomainModel):
    """
    Data model for a timer.

    Immutable domain model for timer metadata and state.

    Attributes:
        timer_id: Unique identifier for the timer
        label: Human-readable timer label/name
        duration_ms: Duration in milliseconds
        state: Current state (RUNNING, PAUSED, DONE)
        remaining_ms: Optional remaining time in milliseconds
        sound_uri: Optional custom timer sound URI

    Example:
        >>> timer = TimerDTO(
        ...     timer_id="timer123",
        ...     label="Cooking",
        ...     duration_ms=300000,
        ...     state="RUNNING",
        ...     remaining_ms=250000
        ... )
    """

    timer_id: str = Field(..., alias="timerId")
    label: str
    duration_ms: int = Field(..., alias="durationMs", gt=0)
    state: Optional[str] = None
    remaining_ms: Optional[int] = Field(None, alias="remainingMs")
    sound_uri: Optional[str] = Field(None, alias="soundUri")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)

    @field_validator("duration_ms")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Ensure duration is positive."""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v


class CreateTimerRequest(RequestDTO):
    """
    Request to create a new timer.

    Immutable request DTO for timer creation.

    Attributes:
        device_serial_number: Serial number of the target device
        label: Timer label/name
        duration_ms: Duration in milliseconds
        sound_uri: Optional custom timer sound

    Example:
        >>> request = CreateTimerRequest(
        ...     device_serial_number="SERIALNUMBER123",
        ...     label="Cooking",
        ...     duration_ms=300000
        ... )
    """

    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    label: str
    duration_ms: int = Field(..., alias="durationMs", gt=0)
    sound_uri: Optional[str] = Field(None, alias="soundUri")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)

    @field_validator("duration_ms")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Ensure duration is positive."""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v


class TimerResponse(ResponseDTO):
    """
    Response from timer operation.

    Immutable response DTO with automatic timestamp.

    Attributes:
        success: Whether the operation succeeded
        timer_id: ID of the created/modified timer (on success)
        error: Optional error description
        error_code: Optional error code identifier
        created_at: Timestamp of response creation (auto-set)

    Example:
        >>> response = TimerResponse(
        ...     success=True,
        ...     timer_id="timer456"
        ... )
    """

    success: bool
    timer_id: Optional[str] = Field(None, alias="timerId")
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class GetTimersResponse(ResponseDTO):
    """
    Response containing list of all timers.

    Response DTO for GET /api/timers endpoint.

    Attributes:
        timers: List of TimerDTO objects

    Example:
        >>> response = GetTimersResponse(
        ...     timers=[
        ...         TimerDTO(timer_id="timer1", label="Cooking", duration_ms=300000, state="RUNNING")
        ...     ]
        ... )
    """

    timers: list[TimerDTO] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)
