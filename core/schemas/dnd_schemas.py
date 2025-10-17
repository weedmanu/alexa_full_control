"""
Do Not Disturb (DND) Schemas - Phase 3.5c.5

Data Transfer Objects (DTOs) for DND-related API operations.

Classes:
- DNDStatusDTO: Current DND state
- SetDNDRequest: Request to set DND mode
- DNDResponse: Response from DND operations

API Endpoints Covered:
- GET /api/dnd: Get current DND status
- POST /api/dnd: Set DND mode
- DELETE /api/dnd: Clear DND mode
"""

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class DNDStatusDTO(DomainModel):
    """Data model for DND status."""

    enabled: bool
    duration_ms: Optional[int] = Field(None, alias="durationMs")
    end_time: Optional[datetime] = Field(None, alias="endTime")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class SetDNDRequest(RequestDTO):
    """Request to set DND mode."""

    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    enabled: bool
    duration_ms: Optional[int] = Field(None, alias="durationMs")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class DNDResponse(ResponseDTO):
    """Response from DND operation."""

    success: bool
    dnd_enabled: Optional[bool] = Field(None, alias="dndEnabled")
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)
