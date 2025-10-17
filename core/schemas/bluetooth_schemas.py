"""
Bluetooth Schemas - Phase 3.5c.11

Data Transfer Objects (DTOs) for Bluetooth device operations.

Classes:
- BluetoothDeviceDTO: Bluetooth device metadata
- BluetoothRequest: Request for Bluetooth operations
- BluetoothResponse: Response from Bluetooth operations

API Endpoints Covered:
- GET /api/bluetooth/devices: List paired devices
- POST /api/bluetooth/devices/{address}/connect: Connect device
- POST /api/bluetooth/devices/{address}/disconnect: Disconnect device
"""

from typing import Optional

from pydantic import ConfigDict, Field

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class BluetoothDeviceDTO(DomainModel):
    """Data model for a Bluetooth device."""

    device_address: str = Field(..., alias="deviceAddress")
    name: str
    paired: bool = False
    rssi: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class BluetoothRequest(RequestDTO):
    """Request for Bluetooth operations."""

    device_address: str = Field(..., alias="deviceAddress")
    action: str

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class BluetoothResponse(ResponseDTO):
    """Response from Bluetooth operation."""

    success: bool
    paired: Optional[bool] = None
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)
