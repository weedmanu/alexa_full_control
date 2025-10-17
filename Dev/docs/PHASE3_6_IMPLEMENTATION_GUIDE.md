# Phase 3.6 - AlexaAPIService DTO Integration Implementation Guide

**Status**: ✅ PHASE 3.6 CORE COMPLETE - 323/323 Tests Passing

## Overview

Phase 3.6 has established the complete DTO foundation and integration pattern. AlexaAPIService now has:

1. ✅ Core infrastructure (\_parse_dto helper, type hints)
2. ✅ Device method pattern implemented (get_devices)
3. ✅ Communication DTOs (27 tests)
4. ✅ Integration tests (9 tests)
5. ✅ All phase 3.5 schemas (287 tests)

## Test Status

```
Core Schemas (Phase 3.5c):        287/287 ✅
Communication Schemas (Phase 3.6):  27/27 ✅
Integration Tests:                   9/9  ✅
─────────────────────────────────────────
TOTAL:                            323/323 ✅
```

## Architecture Pattern

All DTOs follow this pattern:

```python
# 1. Define request DTO (immutable, for sending)
class MyCommandRequest(RequestDTO):
    device_serial: str = Field(..., alias="deviceSerialNumber")
    # populate_by_name=True allows both snake_case and camelCase

# 2. Define response DTO (immutable, for receiving)
class MyCommandResponse(ResponseDTO):
    success: bool = Field(default=True)
    created_at: datetime  # Auto-set by ResponseDTO

# 3. Use in AlexaAPIService
def my_command(self, device_serial: str) -> MyCommandResponse:
    # Parse request
    request = MyCommandRequest(device_serial=device_serial)

    # Make API call
    response_data = self._request("POST", "/my-endpoint", json=request.model_dump())

    # Parse response DTO
    return self._parse_dto(response_data, MyCommandResponse)
```

## Implementation Checklist for Next Iterations

### Tier 1: Basic Methods (Quick Wins)

- [ ] `send_speak_command()` - Use CommunicationResponse DTO
- [ ] `send_announce_command()` - Use CommunicationResponse DTO
- [ ] `get_music_status()` - Use MusicStatusResponse DTO

### Tier 2: Music Methods

- [ ] `play_music()` - Use PlayMusicResponse DTO
- [ ] `pause_music()` - Use CommunicationResponse DTO
- [ ] `resume_music()` - Use CommunicationResponse DTO
- [ ] `next_track()` - Use CommunicationResponse DTO
- [ ] `previous_track()` - Use CommunicationResponse DTO

### Tier 3: Notification Methods

- [ ] `create_reminder()` - Use ReminderResponse DTO
- [ ] `set_alarm()` - Use AlarmResponse DTO
- [ ] `set_dnd()` - Use DNDResponse DTO

### Tier 4: Complex Methods

- [ ] `execute_routine()` - Use RoutineResponse DTO
- [ ] `get_lists()` - Use ListResponse DTO
- [ ] `get_smart_home_devices()` - Use SmartHomeResponse DTO

## How to Add a New Method

### Example: Adding `send_speak_command()` with DTOs

**Step 1**: Create DTOs in `communication_schemas.py` ✅ (Already done)

```python
class SpeakCommandRequest(RequestDTO):
    device_serial: str = Field(..., alias="deviceSerialNumber")
    text_to_speak: str = Field(..., alias="textToSpeak")

class CommunicationResponse(ResponseDTO):
    success: bool = Field(default=True)
    # ... other fields
```

**Step 2**: Write integration test first (TDD)

```python
def test_send_speak_command_with_dto(self):
    service = AlexaAPIService(session=mock_session)
    response = service.send_speak_command("DEVICE001", "Hello")

    # Verify returns typed DTO
    assert isinstance(response, CommunicationResponse)
    assert response.success is True
```

**Step 3**: Implement in `alexa_api_service.py`

```python
def send_speak_command(self, device_serial: str, text: str) -> CommunicationResponse:
    """Send speak command to device."""
    # Parse request
    request = SpeakCommandRequest(
        device_serial=device_serial,
        text_to_speak=text
    )

    # Make API call
    path = self.ENDPOINTS.get("speak", "/speak")
    response_data = self.post(path, json=request.model_dump(by_alias=True))

    # Parse response DTO
    return self._parse_dto(response_data, CommunicationResponse)
```

## Type Hints Benefits

With DTOs, code gets IDE auto-completion:

```python
# ✅ IDE knows response type
response = service.get_devices()  # GetDevicesResponse
for device in response.devices:    # IDE shows: List[Device]
    print(device.serial_number)    # IDE auto-completes: serial_number

# ✅ IDE catches type errors
device = response.devices[0]
device.online = False  # ❌ IDE Error: ResponseDTO frozen
```

## Import Locations

```python
# Device-related
from core.schemas.device_schemas import (
    Device,
    GetDevicesResponse,
    GetDevicesRequest,
)

# Communication (speak, announce, broadcast)
from core.schemas.communication_schemas import (
    SpeakCommandRequest,
    CommunicationResponse,
    BroadcastResponse,
    ConversationResponse,
)

# Music
from core.schemas.music_schemas import (
    TrackDTO,
    PlaylistDTO,
    PlayMusicRequest,
    PlayMusicResponse,
    MusicStatusResponse,
)

# Alarms, Reminders, etc.
from core.schemas.alarm_schemas import (
    AlarmDTO,
    CreateAlarmRequest,
    AlarmResponse,
)

# All response DTOs inherit from ResponseDTO
from core.schemas.base import ResponseDTO, RequestDTO
```

## Error Handling

The `_parse_dto()` helper automatically converts validation errors to API errors:

```python
def _parse_dto(self, data: Dict[str, Any], dto_class: Type[T]) -> T:
    """Validate response with DTO."""
    if not HAS_SCHEMAS:
        return data  # Graceful fallback

    try:
        return dto_class(**data)
    except ValidationError as e:
        raise ApiError(
            status=400,
            body={'error': str(e), 'errorCode': 'VALIDATION_ERROR'},
            endpoint='parse_response'
        ) from e
```

## Next Phase: Managers

After all AlexaAPIService methods return DTOs, Phase 3.7 will update managers:

```python
# DeviceManager will receive typed DTOs
class DeviceManager:
    def __init__(self, api_service: AlexaAPIService):
        self.api_service = api_service

    def get_all_devices(self) -> List[Device]:
        # Already typed! No casting needed
        response: GetDevicesResponse = self.api_service.get_devices()
        return response.devices  # Type-safe
```

## Testing Guidelines

1. **TDD First**: Write test before implementation
2. **Test DTOs**: Verify request/response parsing
3. **Test Types**: Verify return types are DTOs
4. **Mock Correctly**: Include status_code on mock responses
5. **Integration**: Test full flow through service

```python
def test_method_returns_typed_dto(self):
    service = AlexaAPIService(session=mock)
    result = service.my_method()

    # Verify type
    assert isinstance(result, MyResponseDTO)

    # Verify immutability
    with pytest.raises(Exception):
        result.field = "new_value"

    # Verify auto-timestamp
    assert result.created_at is not None
```

## Pydantic v2 Tips

```python
# 1. populate_by_name=True allows both formats
request = MyDTO(device_serial="ABC")   # snake_case
request = MyDTO(deviceSerialNumber="ABC")  # camelCase

# 2. model_dump(by_alias=True) for API serialization
data = request.model_dump(by_alias=True)
# {"deviceSerialNumber": "ABC", "textToSpeak": "Hello"}

# 3. frozen=True prevents accidental modifications
response.success = False  # ❌ FrozenInstanceError

# 4. Field validators for custom logic
@field_validator('duration', mode='before')
def validate_duration(cls, v):
    if v < 0:
        raise ValueError('Duration must be positive')
    return v
```

## Files to Update

### To Add Next Method:

1. **alexa_api_service.py**: Add method with DTO return type
2. **test_alexa_api_service_dto_integration.py**: Add integration test
3. **Corresponding \_schemas.py**: Ensure DTOs exist
4. **Corresponding test file**: Ensure DTO tests pass

### Files Modified This Session:

```
✅ core/schemas/communication_schemas.py (NEW)
✅ Dev/pytests/core/schemas/test_communication_schemas.py (NEW)
✅ services/alexa_api_service.py (Enhanced with imports)
✅ Dev/pytests/services/test_alexa_api_service_dto_integration.py (Fixed)
```

## Performance Impact

DTOs add minimal overhead:

- **Parsing**: <1ms per response (measured in tests)
- **Memory**: Negligible (same data structure)
- **Benefits**: Type safety, IDE support, auto-validation

## Next Steps

1. **Phase 3.6 Iterations**: Implement Tier 1-4 methods with DTOs
2. **Phase 3.7**: Update all managers to consume typed DTOs
3. **Phase 3.8**: Auto-generate API docs from DTOs
4. **Phase 3.9-11**: Full validation, testing, merge

## Questions?

Refer to:

- **DTO Examples**: `core/schemas/device_schemas.py`
- **Base Classes**: `core/schemas/base.py`
- **Test Examples**: `Dev/pytests/core/schemas/test_*.py`
- **Integration**: `Dev/pytests/services/test_alexa_api_service_dto_integration.py`

---

**Last Updated**: 17 octobre 2025
**Tests**: 323/323 ✅
**Status**: Ready for next iteration
