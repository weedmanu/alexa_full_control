"""
Device-Related Data Transfer Objects (DTOs)

Phase 3.4 - Device Schemas Implementation

Models:
- Device: Individual Alexa device with status, capabilities
- GetDevicesRequest: Request to fetch all devices
- GetDevicesResponse: Response containing list of devices

API Endpoints:
- GET /api/devices: Retrieve all registered Alexa devices
- Implements device discovery and status retrieval

Field Mapping (camelCase → snake_case):
- serialNumber → serial_number
- deviceName → device_name
- deviceType → device_type
- deviceFamily → device_family
- accountName → account_name
- parentSerialNumber → parent_serial_number
- supportedOperations → supported_operations
- macAddress → mac_address
- firmwareVersion → firmware_version

Example Amazon API Response:
{
    "devices": [
        {
            "serialNumber": "ABCD1234567890",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": true,
            "accountName": "John Doe",
            "deviceFamily": "Echo",
            "capabilities": ["MUSIC_STREAMING", "ANNOUNCE"],
            "supportedOperations": ["MUSIC_PLAYER", "VOLUME"]
        }
    ]
}
"""

from typing import List, Optional

from pydantic import Field, field_validator

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class Device(DomainModel):
    """
    Individual Alexa device information.

    Represents a single registered Alexa device with its capabilities,
    online status, and device metadata.

    Attributes:
        serial_number: Unique device identifier (Amazon serial number)
        device_name: User-friendly device name (e.g., "Salon")
        device_type: Device type/model (e.g., "ECHO_DOT", "ECHO", "ECHO_SHOW")
        online: Whether device is currently connected and online
        account_name: Associated AWS account name (optional)
        device_family: Device family category (e.g., "Echo", "Fire", "Dash")
        capabilities: List of device capabilities (e.g., "MUSIC_STREAMING")
        supported_operations: Operations device can perform
        location: Physical location name (e.g., "Living Room")
        mac_address: Device MAC address for network identification
        firmware_version: Current firmware version
        parent_serial_number: Serial number of parent device (for paired devices)

    Example:
        >>> device = Device(
        ...     serialNumber="ABC123",
        ...     deviceName="Salon",
        ...     deviceType="ECHO_DOT",
        ...     online=True
        ... )
        >>> device.serial_number
        'ABC123'
        >>> device.device_name
        'Salon'
    """

    # Required fields
    serial_number: str = Field(..., alias="serialNumber", min_length=1)
    device_name: str = Field(..., alias="deviceName", min_length=1)
    device_type: str = Field(..., alias="deviceType", min_length=1)
    online: bool

    # Optional fields
    account_name: Optional[str] = Field(None, alias="accountName")
    device_family: Optional[str] = Field(None, alias="deviceFamily")
    capabilities: Optional[List[str]] = Field(None)
    supported_operations: Optional[List[str]] = Field(None, alias="supportedOperations")
    location: Optional[str] = Field(None)
    mac_address: Optional[str] = Field(None, alias="macAddress")
    firmware_version: Optional[str] = Field(None, alias="firmwareVersion")
    parent_serial_number: Optional[str] = Field(None, alias="parentSerialNumber")

    @field_validator("serial_number", "device_name", "device_type", mode="before")
    @classmethod
    def validate_not_none_string(cls, v):
        """Reject 'None' string values."""
        if v == "None":
            raise ValueError("Field cannot be 'None' string")
        return v


class GetDevicesRequest(RequestDTO):
    """
    Request to retrieve all Alexa devices.

    GET /api/devices typically has empty request body.
    Parameters may be passed as query strings instead.

    Example:
        >>> request = GetDevicesRequest()
        >>> # Send empty body request
    """

    # GET /api/devices typically has no body parameters
    # This is a marker class for type safety
    pass


class GetDevicesResponse(ResponseDTO):
    """
    Response containing list of all registered Alexa devices.

    This is the main response from device listing endpoint.
    Contains all devices registered to the Amazon account.

    Attributes:
        devices: List of Device objects
        created_at: Response generation timestamp (from ResponseDTO base)

    Example:
        >>> response = GetDevicesResponse(devices=[
        ...     Device(serialNumber="ABC123", deviceName="Salon", ...)
        ... ])
        >>> len(response.devices)
        1
        >>> response.devices[0].serial_number
        'ABC123'
    """

    devices: List[Device] = Field(..., description="List of registered devices")

    def get_online_devices(self) -> List[Device]:
        """Get only devices that are currently online."""
        return [d for d in self.devices if d.online]

    def get_device_by_name(self, name: str) -> Optional[Device]:
        """Find device by name (case-insensitive)."""
        name_lower = name.lower()
        for device in self.devices:
            if device.device_name.lower() == name_lower:
                return device
        return None

    def get_device_by_serial(self, serial: str) -> Optional[Device]:
        """Find device by serial number."""
        for device in self.devices:
            if device.serial_number == serial:
                return device
        return None

    def get_devices_by_type(self, device_type: str) -> List[Device]:
        """Get all devices of specific type."""
        return [d for d in self.devices if d.device_type == device_type]

    def get_devices_by_family(self, family: str) -> List[Device]:
        """Get all devices of specific family."""
        return [d for d in self.devices if d.device_family == family]


__all__ = [
    "Device",
    "GetDevicesRequest",
    "GetDevicesResponse",
]
