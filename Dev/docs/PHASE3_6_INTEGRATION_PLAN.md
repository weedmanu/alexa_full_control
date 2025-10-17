"""
Phase 3.6 Implementation Plan: AlexaAPIService DTO Integration

## Overview:

Refactor AlexaAPIService to use typed DTOs for all API requests/responses.
This enables type safety, automatic validation, and better IDE support.

Current State:

- AlexaAPIService returns raw dicts/lists
- No validation of response structure
- Manual error handling
- No type hints on return values

Target State:

- All API methods return typed DTOs (ResponseDTO subclasses)
- Automatic validation with Pydantic
- Centralized error handling with error_code
- Full type hints and IDE auto-completion

# Implementation Strategy:

1. Core Changes:

   - Add import for relevant schema modules
   - Create helper method: \_parse_response(response_dict, dto_class)
   - Create error handler: \_handle_api_error(status, body, endpoint)
   - Add type hints to all method signatures

2. Error Handling:

   - Wrap ValidationError → APIError with error_code
   - Include original error for debugging
   - Maintain backward compatibility with existing error handling

3. API Methods to Refactor (Suggested Priority):

   TIER 1 (Basic):

   - get_devices() → GetDevicesResponse
   - send_speak_command() → ResponseDTO

   TIER 2 (Music/Playback):

   - play_music(track_id, device) → PlayMusicResponse
   - pause_music(device) → ResponseDTO
   - resume_music(device) → ResponseDTO
   - get_music_status(device) → MusicStatusResponse

   TIER 3 (Notifications):

   - create_reminder() → ReminderResponse
   - set_alarm() → AlarmResponse
   - set_dnd(device) → DNDResponse

   TIER 4 (Complex):

   - get_routines() → List[RoutineDTO]
   - execute_routine() → RoutineResponse
   - manage_lists() → ListResponse
   - get_smart_home_devices() → List[SmartHomeDeviceDTO]

4. Testing:

   - Unit tests for DTO parsing
   - Error handling tests
   - Type checking with mypy
   - Integration tests with mocked responses

5. Backward Compatibility:
   - Existing tests may return dicts initially
   - Manager layer will adapt responses as needed
   - Gradual migration is acceptable

# Benefits:

✓ Type safety: IDE knows method return types
✓ Validation: Automatic field validation
✓ Documentation: DTOs document API contract
✓ Error handling: Consistent error_code patterns
✓ IDE support: Auto-completion for all fields
✓ Maintainability: Clear structure, less boilerplate

# Implementation Order:

1. Add DTO imports to AlexaAPIService
2. Create \_parse_response() helper
3. Update get_devices() as example
4. Update send_speak_command()
5. Add tests for each method
6. Document pattern for other methods
7. Manager layer integration (Phase 3.7)

Example Implementation:

    from core.schemas.device_schemas import GetDevicesResponse, Device

    def get_devices(self, use_cache_fallback: bool = True) -> GetDevicesResponse:
        '''Get list of devices.

        Returns:
            GetDevicesResponse: DTO with devices list and metadata

        Raises:
            ApiError: On API failure
        '''
        try:
            # Make request
            data = self._request_internal(...)

            # Parse devices to DTOs
            devices = [Device(**d) for d in data.get('devices', [])]

            # Create response DTO
            return GetDevicesResponse(devices=devices)

        except ValidationError as e:
            raise ApiError(
                status=400,
                body={'error': str(e), 'errorCode': 'VALIDATION_ERROR'}
            )
        except Exception as e:
            # Handle as before
            ...

# Key Decisions:

1. DTO parsing happens in AlexaAPIService (boundary layer)
2. Managers receive DTOs and can optionally convert to models
3. Response validation is automatic (Pydantic)
4. Error handling includes both message and error_code
5. Maintain existing public API where possible
   """
