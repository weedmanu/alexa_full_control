"""
Routine Schemas - Phase 3.5c.1

Data Transfer Objects (DTOs) for routine-related API operations.

Classes:
- RoutineDTO: Routine metadata and configuration
- ExecuteRoutineRequest: Request to execute a routine
- RoutineResponse: Response from routine operations

API Endpoints Covered:
- GET /api/routines: List all routines
- POST /api/routines/{routineId}/execute: Execute a routine
- PUT /api/routines/{routineId}: Update routine
- DELETE /api/routines/{routineId}: Delete routine
"""

from typing import Optional

from pydantic import ConfigDict, Field

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class RoutineDTO(DomainModel):
    """
    Data model for a routine (automation workflow).

    Immutable domain model for routine metadata and configuration.

    Attributes:
        routine_id: Unique identifier for the routine
        name: Human-readable routine name
        enabled: Whether the routine is active
        description: Optional description of what the routine does
        serialized: Optional serialized format identifier
        automation_type: Optional type of automation (e.g., TIME_OF_DAY, VOICE_COMMAND)

    Example:
        >>> routine = RoutineDTO(
        ...     routine_id="routine123",
        ...     name="Morning Routine",
        ...     enabled=True,
        ...     description="Start the day",
        ...     automation_type="TIME_OF_DAY"
        ... )
    """

    routine_id: str = Field(..., alias="routineId")
    name: str
    enabled: bool
    description: Optional[str] = None
    serialized: Optional[str] = None
    automation_type: Optional[str] = Field(None, alias="automationType")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class ExecuteRoutineRequest(RequestDTO):
    """
    Request to execute a routine on a device.

    Immutable request DTO for routine execution.

    Attributes:
        device_serial_number: Serial number of the target device
        routine_id: ID of the routine to execute

    Example:
        >>> request = ExecuteRoutineRequest(
        ...     device_serial_number="SERIALNUMBER123",
        ...     routine_id="routine123"
        ... )
    """

    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    routine_id: str = Field(..., alias="routineId")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class RoutineResponse(ResponseDTO):
    """
    Response from routine operation.

    Immutable response DTO with automatic timestamp.

    Attributes:
        success: Whether the operation succeeded
        message: Optional success message
        error: Optional error description
        error_code: Optional error code identifier
        created_at: Timestamp of response creation (auto-set)

    Example:
        >>> response = RoutineResponse(
        ...     success=True,
        ...     message="Routine executed successfully"
        ... )
    """

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)
