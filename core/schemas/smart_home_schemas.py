"""
Smart Home Schemas - Phase 3.5c.10

Data Transfer Objects (DTOs) for smart home operations.

Classes:
- SmartHomeDeviceDTO: Smart home device metadata
- SmartHomeRequest: Request for smart home operations
- SmartHomeResponse: Response from smart home operations

API Endpoints Covered:
- GET /api/smart-home/devices: List devices
- POST /api/smart-home/devices/{deviceId}/command: Send command
"""

from typing import Optional
from pydantic import Field, ConfigDict

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class SmartHomeDeviceDTO(DomainModel):
    """Data model for a smart home device."""
    
    device_id: str = Field(..., alias="deviceId")
    name: str
    state: Optional[str] = None
    device_type: Optional[str] = Field(None, alias="deviceType")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class SmartHomeRequest(RequestDTO):
    """Request for smart home operations."""
    
    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    action: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )


class SmartHomeResponse(ResponseDTO):
    """Response from smart home operation."""
    
    success: bool
    state: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")
    
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True
    )
