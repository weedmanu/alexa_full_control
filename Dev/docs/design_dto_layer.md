# Phase 3.2: DTO Layer Architecture Design

**Project**: Alexa Voice Control CLI  
**Objective**: Design the Pydantic DTO layer for type-safe data contracts  
**Date**: 17 octobre 2025  
**Status**: Phase 3.2 - Design DTO Layer Architecture  
**Based On**: Phase 3.1 API Contracts (docs/api_contracts.md)

---

## 📋 Executive Summary

This document describes the architecture for implementing type-safe Data Transfer Objects (DTOs) using Pydantic v2 across the entire application. The design ensures:

- ✅ **Type Safety**: All API data validated and typed
- ✅ **Immutability**: Request/Response DTOs are frozen (read-only)
- ✅ **Field Naming**: Support both camelCase (API) and snake_case (Python)
- ✅ **Comprehensive Validation**: Custom validators for complex business logic
- ✅ **Error Handling**: Clear error messages with field-level feedback
- ✅ **Documentation**: Auto-generated JSON Schema and examples
- ✅ **IDE Support**: Full auto-completion for all API responses

---

## 🏗️ Directory Structure

```
core/
├── schemas/                    # NEW: All DTOs and validators
│   ├── __init__.py            # Public API exports
│   ├── base.py                # Base classes and common types
│   ├── device_schemas.py      # Device-related DTOs
│   ├── music_schemas.py       # Music/Playback DTOs
│   ├── auth_schemas.py        # Authentication DTOs
│   ├── routine_schemas.py     # Routine/Automation DTOs
│   ├── alarm_schemas.py       # Alarm DTOs
│   ├── timer_schemas.py       # Timer DTOs
│   ├── reminder_schemas.py    # Reminder DTOs
│   ├── dnd_schemas.py         # Do Not Disturb DTOs
│   ├── multiroom_schemas.py   # Multiroom Audio DTOs
│   ├── lists_schemas.py       # Lists/Shopping DTOs
│   ├── notification_schemas.py # Notification DTOs
│   ├── calendar_schemas.py    # Calendar DTOs
│   ├── smart_home_schemas.py  # Smart Home DTOs
│   ├── bluetooth_schemas.py   # Bluetooth DTOs
│   └── validators.py          # Custom validators and utilities
│
Dev/
├── pytests/
│   ├── core/
│   │   ├── schemas/           # NEW: Schema tests
│   │   │   ├── __init__.py
│   │   │   ├── test_device_schemas.py
│   │   │   ├── test_music_schemas.py
│   │   │   ├── test_auth_schemas.py
│   │   │   └── ... (more test files)
│   │   └── ...
│   └── ...
```

---

## 📦 Core Design Concepts

### 1. DTO Types

#### BaseDTOModel

Base class for ALL DTOs with common Pydantic configuration.

```
Pydantic BaseModel
    ↓
    BaseDTOModel (Common config: str_strip_whitespace, extra='forbid', etc)
    ├─ RequestDTO (frozen=True, immutable)
    ├─ ResponseDTO (frozen=True, immutable)
    └─ DomainModel (domain-specific objects: Device, Alarm, etc)
```

#### Request DTOs

- **Pattern**: `{Action}Request` or `{Endpoint}Request`
- **Examples**: `GetDevicesRequest`, `SendSpeakCommandRequest`, `CreateAlarmRequest`
- **Properties**: Frozen, immutable (cannot be modified after creation)
- **Validation**: Input validation before sending to API
- **Structure**: Usually minimal for GET requests, detailed for POST/PUT

#### Response DTOs

- **Pattern**: `{Action}Response` or `{Resource}DTO`
- **Examples**: `GetDevicesResponse`, `DeviceDTO`, `AlarmDTO`
- **Properties**: Frozen, immutable (API data read-only)
- **Validation**: Output validation after receiving from API
- **Structure**: Maps directly from API JSON response

#### Domain Models

- **Pattern**: `{Resource}Model` or just `{Resource}`
- **Examples**: `Device`, `Alarm`, `Reminder`, `Routine`
- **Properties**: Reusable across request/response
- **Location**: Nested inside appropriate schema files

---

## 🔧 Pydantic Configuration

### Base Configuration (All DTOs)

```python
model_config = ConfigDict(
    # 1. Data Transformation
    str_strip_whitespace=True,      # Trim strings automatically
    str_to_lower=False,             # Keep case as-is (usually)

    # 2. Extra Fields
    extra='forbid',                 # Reject unknown fields (strict mode)
    populate_by_name=True,          # Accept both camelCase and snake_case

    # 3. Serialization
    use_enum_values=True,           # Use enum values, not enum names

    # 4. JSON Schema
    json_schema_extra={
        "examples": [],             # Override in each DTO
    }
)
```

### Field Naming Strategy

Use `Field(..., alias='camelCaseName')` to map API camelCase to Python snake_case:

```python
from pydantic import Field

class Device(ResponseDTO):
    serial_number: str = Field(..., alias='serialNumber')
    device_name: str = Field(..., alias='deviceName')
    device_type: str = Field(..., alias='deviceType')
    online: bool
```

This allows:

- API JSON uses `"serialNumber": "ABC123"` (camelCase)
- Python code uses `device.serial_number` (snake_case)
- Both formats accepted during parsing (thanks to `populate_by_name=True`)

---

## 🎯 Naming Conventions

### Request DTOs

| Pattern             | Example                                     | Used For                |
| ------------------- | ------------------------------------------- | ----------------------- |
| `{Action}Request`   | `CreateAlarmRequest`, `DeleteTimerRequest`  | Specific action/command |
| `{Endpoint}Request` | `GetDevicesRequest`, `UpdateRoutineRequest` | Endpoint-based naming   |

### Response DTOs & Models

| Pattern            | Example                                     | Used For                     |
| ------------------ | ------------------------------------------- | ---------------------------- |
| `{Resource}DTO`    | `DeviceDTO`, `AlarmDTO`                     | Single resource response     |
| `{Action}Response` | `GetDevicesResponse`, `CreateAlarmResponse` | Full endpoint response       |
| `{Resource}`       | `Device`, `Alarm`                           | Domain model (nested/shared) |
| `List{Resource}`   | `ListDevices`, `ListAlarms`                 | List container               |

### Error DTOs

| Pattern                 | Example                | Used For              |
| ----------------------- | ---------------------- | --------------------- |
| `APIErrorDTO`           | Error response wrapper | Standard error format |
| `ValidationErrorDetail` | Field-level validation | Detailed error info   |

---

## 🔗 Inheritance Hierarchy

```
Pydantic BaseModel
│
└─ BaseDTOModel (ConfigDict configured)
   │
   ├─ RequestDTO (frozen=True)
   │  ├─ CreateDeviceRequest
   │  ├─ SendCommandRequest
   │  └─ ...
   │
   ├─ ResponseDTO (frozen=True, created_at field)
   │  ├─ GetDevicesResponse
   │  ├─ DeviceDTO
   │  └─ ...
   │
   └─ DomainModel (unfrozen, reusable)
      ├─ Device (used in requests/responses)
      ├─ Alarm (used in requests/responses)
      └─ ...

Also:
├─ APIErrorDTO (error responses)
├─ APISuccessResponse[T] (generic success wrapper)
└─ ValidationErrorDetail (field-level errors)
```

---

## 📝 Field Validation Strategy

### 1. Type Validation

```python
serial_number: str              # Must be string
online: bool                    # Must be boolean
duration: int                   # Must be integer
remaining_time: float           # Must be float
created_at: datetime            # Must be datetime
```

### 2. Constraints

```python
from pydantic import Field

label: str = Field(..., min_length=1, max_length=255)
duration: int = Field(..., ge=1, le=86400)  # 1 sec to 24 hours
percentage: float = Field(..., ge=0.0, le=100.0)
email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

### 3. Custom Validation

```python
from pydantic import field_validator

class AlarmDTO(ResponseDTO):
    alarm_time: str

    @field_validator('alarm_time')
    @classmethod
    def validate_alarm_time(cls, v):
        """Validate time format HH:MM:SS"""
        if not re.match(r'^\d{2}:\d{2}:\d{2}$', v):
            raise ValueError('Invalid time format, expected HH:MM:SS')
        return v
```

### 4. Optional vs Required

```python
required_field: str              # Required (no default)
optional_field: Optional[str]    # Optional (can be None)
field_with_default: str = "default"  # Has default value
nullable_field: str | None       # Can be null
```

---

## 🛡️ Error Handling & Validation

### 1. Standard Error Response

```python
class APIErrorDTO(BaseDTOModel):
    """Standard API error response"""
    success: bool = False
    error: str                           # Main error message
    error_code: Optional[str] = None     # Error code (AUTH_ERROR, NOT_FOUND, etc)
    details: Optional[dict] = None       # Additional details
    field_errors: Optional[dict] = None  # Field-level errors
```

### 2. Validation Error Detail

```python
class ValidationErrorDetail(BaseDTOModel):
    """Field-level validation error"""
    field: str                   # Field name that failed validation
    message: str                 # Error message
    value: Optional[Any] = None  # The invalid value
    code: str                    # Error code (required, type_error, etc)
```

### 3. Integration in Services

```python
from pydantic import ValidationError
from core.exceptions import APIError

def get_devices(self) -> GetDevicesResponse:
    response = self.api_session.get('/api/devices')
    data = response.json()

    try:
        # Parse and validate response
        return GetDevicesResponse(**data)
    except ValidationError as e:
        # Convert Pydantic validation errors to domain errors
        raise APIError(
            f"Invalid devices response: {e}",
            details=e.errors()  # Include validation details
        )
```

---

## 🔄 Serialization & Deserialization

### Parsing from API (camelCase → snake_case)

```python
# API returns:
api_response = {
    "serialNumber": "ABC123",
    "deviceName": "Salon",
    "online": True
}

# Pydantic converts to Python:
device = Device(**api_response)
# device.serial_number == "ABC123"
# device.device_name == "Salon"
```

### Serializing to JSON (snake_case → camelCase)

```python
device = Device(
    serial_number="ABC123",
    device_name="Salon",
    online=True
)

# Method 1: model_dump(by_alias=True) for API
api_json = device.model_dump(by_alias=True)
# {"serialNumber": "ABC123", "deviceName": "Salon", "online": True}

# Method 2: model_dump_json for JSON strings
json_string = device.model_dump_json(by_alias=True)

# Method 3: model_dump for Python dict
python_dict = device.model_dump()
```

---

## 📚 Documentation & Examples

### Each DTO includes:

```python
class DeviceDTO(ResponseDTO):
    """
    Single Alexa device information.

    Represents a device registered with the user's Amazon account.
    Maps from API response: GET /api/devices-v2/device

    Attributes:
        serial_number: Unique device identifier (e.g., "ABCD1234567890")
        device_name: User-friendly device name (e.g., "Salon")
        device_type: Device model (e.g., "ECHO_DOT", "ECHO", "SHOW")
        online: Whether device is currently online and reachable
        capabilities: List of features this device supports

    Example:
        >>> response = api_service.get_devices()
        >>> for device in response.devices:
        ...     if device.online:
        ...         print(f"{device.device_name}: {device.device_type}")
        Salon: ECHO_DOT
        Kitchen: ECHO
    """

    serial_number: str = Field(..., description="Unique device ID")
    device_name: str = Field(..., description="User-friendly name")
    device_type: str = Field(..., description="Device model type")
    online: bool = Field(..., description="Online status")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "serial_number": "ABCD1234567890",
                    "device_name": "Salon",
                    "device_type": "ECHO_DOT",
                    "online": True,
                }
            ]
        }
    )
```

---

## 🎯 Schema Organization by Domain

### 1. Device Schemas (`device_schemas.py`)

- Device, GetDevicesResponse, GetDevicesRequest

### 2. Music Schemas (`music_schemas.py`)

- TrackDTO, PlaylistDTO, MusicStatusResponse, PlayMusicRequest, PlayMusicResponse

### 3. Routine Schemas (`routine_schemas.py`)

- RoutineDTO, GetRoutinesResponse, CreateRoutineRequest, UpdateRoutineRequest, DeleteRoutineRequest

### 4. Alarm Schemas (`alarm_schemas.py`)

- AlarmDTO, GetAlarmsResponse, CreateAlarmRequest, UpdateAlarmRequest, DeleteAlarmRequest

### 5. Timer Schemas (`timer_schemas.py`)

- TimerDTO, GetTimersResponse, CreateTimerRequest, PauseTimerRequest

### 6. Reminder Schemas (`reminder_schemas.py`)

- ReminderDTO, GetRemindersResponse, CreateReminderRequest, DeleteReminderRequest

### 7. DND Schemas (`dnd_schemas.py`)

- DNDStatusDTO, GetDNDStatusResponse, SetDNDRequest, SetDNDScheduleRequest

### 8. Multiroom Schemas (`multiroom_schemas.py`)

- GroupDTO, GetGroupsResponse, CreateGroupRequest

### 9. Lists Schemas (`lists_schemas.py`)

- ListDTO, ListItemDTO, GetListsResponse, CreateListRequest, AddListItemRequest

### 10. Notification Schemas (`notification_schemas.py`)

- NotificationDTO, GetNotificationsResponse, SendNotificationRequest

### 11. Calendar Schemas (`calendar_schemas.py`)

- EventDTO, GetEventsResponse

### 12. Smart Home Schemas (`smart_home_schemas.py`)

- SmartHomeDeviceDTO, GetSmartHomeDevicesResponse, ControlDeviceRequest

### 13. Bluetooth Schemas (`bluetooth_schemas.py`)

- BluetoothDeviceDTO, GetBluetoothDevicesResponse, PairDeviceRequest

### 14. Auth Schemas (`auth_schemas.py`)

- SessionDTO, LoginRequest, LoginResponse, TokenDTO

---

## ✅ Common Features Across All DTOs

### 1. **String Whitespace Stripping**

```python
# Input: {"label": "  Wake up  "}
# Parsed: label = "Wake up"  # Automatically trimmed
```

### 2. **Extra Field Rejection**

```python
# Input: {"deviceName": "Salon", "unknownField": "value"}
# Result: ValidationError - extra field not allowed
```

### 3. **Field Aliasing (camelCase ↔ snake_case)**

```python
serial_number: str = Field(..., alias='serialNumber')
# Accepts both in input: serialNumber (from API) or serial_number (from Python)
# Outputs with alias when serializing: by_alias=True
```

### 4. **Immutability (Frozen)**

```python
device = Device(...)
device.online = False  # ❌ FrozenInstanceError: cannot assign to field 'online'
```

### 5. **Type Hints & IDE Auto-completion**

```python
device: DeviceDTO = get_device()
device.serial_number  # ✅ IDE knows this is str
device.online         # ✅ IDE knows this is bool
device.unknown_field  # ❌ IDE shows error: no such attribute
```

### 6. **JSON Schema Generation**

```python
schema = Device.model_json_schema()
# Generates full OpenAPI/JSON Schema for documentation
```

---

## 🚀 Integration Points

### 1. AlexaAPIService → DTOs

```python
class AlexaAPIService:
    def get_devices(self) -> GetDevicesResponse:
        # Before: returns Dict[str, Any]
        # After: returns GetDevicesResponse (typed, validated)
        response = self._session.get('/api/devices')
        return GetDevicesResponse(**response.json())
```

### 2. Managers → DTOs

```python
class DeviceManager:
    def get_devices(self) -> List[Device]:
        # Before: returns List[Dict[str, Any]]
        # After: returns List[Device] (typed, IDE support)
        response = self._api_service.get_devices()
        return response.devices
```

### 3. CLI Commands → DTOs

```python
@command
def list_devices(context: CommandContext):
    devices: List[Device] = context.device_manager.get_devices()
    # IDE provides auto-completion for Device attributes
    for device in devices:
        print(f"{device.device_name}: {device.online}")
```

---

## 📊 Migration Pattern

### Phase 3.2 → 3.3 → 3.4 → ... → 3.7

**Phase 3.3**: Create base.py with BaseDTOModel, RequestDTO, ResponseDTO  
**Phase 3.4-5**: Create domain-specific schemas (device, music, etc) with TDD  
**Phase 3.6**: Update AlexaAPIService to return DTOs  
**Phase 3.7**: Update managers to use typed DTOs

---

## 🔍 Quality Metrics

### Code Quality Goals

| Metric           | Target | Verification                             |
| ---------------- | ------ | ---------------------------------------- |
| Type Coverage    | 100%   | mypy --strict on schemas/                |
| Test Coverage    | 95%+   | pytest --cov on test\_\*\_schemas.py     |
| Documentation    | 100%   | Each DTO has docstring + examples        |
| Immutability     | 100%   | frozen=True on all Request/Response DTOs |
| Field Validation | 100%   | Every field has type + constraints       |

---

## 📋 Design Checklist

- ✅ Base classes defined (BaseDTOModel, RequestDTO, ResponseDTO)
- ✅ Directory structure planned (core/schemas/)
- ✅ Naming conventions established
- ✅ Inheritance hierarchy documented
- ✅ Field validation strategy defined
- ✅ Error handling approach defined
- ✅ Serialization/deserialization strategy defined
- ✅ Integration points identified
- ✅ 14 schema files identified (one per domain)
- ✅ Quality metrics established

---

## 🎯 Next Steps

1. ✅ **Phase 3.1 COMPLETE**: API contracts documented (api_contracts.md)
2. ✅ **Phase 3.2 COMPLETE**: DTO layer architecture designed (this file)
3. ⏭️ **Phase 3.3**: Implement base DTO classes (core/schemas/base.py)
4. ⏭️ **Phase 3.4-5**: Implement domain schemas with TDD
5. ⏭️ **Phase 3.6**: Integrate into AlexaAPIService
6. ⏭️ **Phase 3.7**: Update managers to use typed DTOs

---

**Document Version**: 1.0  
**Last Updated**: 17 octobre 2025  
**Phase**: 3.2 Complete ✅
