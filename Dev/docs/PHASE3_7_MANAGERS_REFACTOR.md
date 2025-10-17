# Phase 3.7: Managers Refactoring with DTOs

**Objective**: Refactor all manager classes to consume type-safe DTOs from AlexaAPIService instead of raw dicts.

**Status**: Planning Phase

**Timeline**: ~2-3 hours estimated

## 1. Managers Inventory

### Core Managers (Phase 1-2)

- [x] **DeviceManager** - `core/device_manager.py`

  - Uses: `self._api_service.get_devices()` → List[Dict]
  - Needs: Consume `GetDevicesResponse` DTO
  - Priority: HIGH (foundational)

- [ ] **ActivityManager** - `core/activity_manager.py`
  - Uses: Legacy \_api_call
  - Needs: Audit if uses api_service
  - Priority: MEDIUM

### Communication Managers (Phase 3.6.1)

- [ ] **DND Manager** - `core/dnd_manager.py`
  - Potential use: `set_dnd()` → DNDResponse DTO
  - Priority: HIGH

### Timer/Reminder/Alarm Managers (Phase 3.6.3)

- [ ] **TimerManager** - `core/timers/timer_manager.py`

  - Potential use: Alarm/Reminder operations
  - Priority: HIGH

- [ ] **ReminderManager** - `core/reminders/reminder_manager.py`

  - Potential use: `create_reminder()` → ReminderResponse DTO
  - Priority: HIGH

- [ ] **AlarmManager** - `core/timers/alarm_manager.py`
  - Potential use: `set_alarm()` → AlarmResponse DTO
  - Priority: HIGH

### Music Managers (Phase 3.6.2)

- [ ] **PlaybackManager** - `core/music/playback_manager.py`

  - Potential use: `play_music()`, `get_music_status()`
  - Priority: HIGH

- [ ] **TuneInManager** - `core/music/tunein_manager.py`

  - Potential use: Music operations
  - Priority: MEDIUM

- [ ] **LibraryManager** - `core/music/library_manager.py`
  - Potential use: Music library operations
  - Priority: MEDIUM

### Complex Managers (Phase 3.6.4)

- [ ] **RoutineManager** - `core/routines/routine_manager.py`

  - Potential use: `execute_routine()` → RoutineResponse DTO
  - Priority: HIGH

- [ ] **ScenarioManager** - `core/scenario/scenario_manager.py`

  - Potential use: Scenario operations
  - Priority: MEDIUM

- [ ] **ListsManager** - `core/lists/lists_manager.py`

  - Potential use: `get_lists()` → ListResponse DTO
  - Priority: HIGH

- [ ] **MultiRoomManager** - `core/multiroom/multiroom_manager.py`

  - Potential use: Multiroom operations
  - Priority: MEDIUM

- [ ] **SmartHomeManager** - `core/smart_home/` (if exists)
  - Potential use: `get_smart_home_devices()` → SmartHomeResponse DTO
  - Priority: HIGH

### Infrastructure Managers

- [ ] **NotificationManager** - `core/notification_manager.py`

  - Priority: MEDIUM

- [ ] **DeviceSettingsManager** - `core/settings/device_settings_manager.py`
  - Priority: LOW

## 2. Refactoring Pattern

### Before (Raw dicts):

```python
def get_devices(self, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
    # ...
    devices = self._api_service.get_devices()  # Returns List[Dict]
    self._cache = devices  # Store raw list
    return devices
```

### After (Typed DTOs):

```python
from core.schemas.device_schemas import GetDevicesResponse

def get_devices(self, force_refresh: bool = False) -> Optional[GetDevicesResponse]:
    # ...
    response = self._api_service.get_devices()  # Returns GetDevicesResponse DTO

    # Extract typed data from DTO
    if isinstance(response, GetDevicesResponse):
        devices = response.devices  # Properly typed List[Device]
        self._cache = devices
        return response

    return None
```

### Type Safety Benefits:

1. IDE auto-completion on response fields
2. Type checking at development time
3. Runtime validation via Pydantic
4. Automatic error handling with ApiError codes
5. Consistent timestamp tracking

## 3. Implementation Plan

### Phase 3.7.1: DeviceManager (Foundational)

**File**: `core/device_manager.py`
**Changes**:

1. Import GetDevicesResponse DTO
2. Update return type annotation: `Optional[GetDevicesResponse]`
3. Update \_refresh_cache() to work with DTO
4. Update cache storage to use DTO
5. Update downstream methods (find_device_by_name, etc.) to work with DTO devices

**Tests to update**:

- `Dev/pytests/test_core/test_device_manager.py`
- All tests expecting List[Dict] now expect GetDevicesResponse

**Estimated**: 30 minutes

### Phase 3.7.2: Communication Managers

**Files**:

- `core/dnd_manager.py`
- `core/timers/alarm_manager.py`
- `core/reminders/reminder_manager.py`

**Changes**:

1. Audit each for api_service usage
2. Import appropriate DTOs (DNDResponse, AlarmResponse, ReminderResponse)
3. Update methods to consume and return DTOs
4. Update type hints throughout

**Tests**: Update corresponding test files

**Estimated**: 45 minutes (3 managers × 15 min each)

### Phase 3.7.3: Music Managers

**Files**:

- `core/music/playback_manager.py`
- `core/music/tunein_manager.py`
- `core/music/library_manager.py`

**Changes**: Similar to Phase 3.7.2 but for music DTOs

**Estimated**: 45 minutes

### Phase 3.7.4: Complex Managers

**Files**:

- `core/routines/routine_manager.py`
- `core/lists/lists_manager.py`
- `core/scenario/scenario_manager.py`
- `core/multiroom/multiroom_manager.py`

**Changes**: Similar pattern, multiple DTOs

**Estimated**: 60 minutes

### Phase 3.7.5: Test Updates & Verification

**Steps**:

1. Run full test suite after each phase
2. Update assertions to work with DTOs
3. Fix any regressions
4. Verify all 775+ tests pass

**Estimated**: 30 minutes

### Phase 3.7.6: Final Commit & Push

**Steps**:

1. Review all changes for consistency
2. Verify no breaking changes
3. Commit with clear message
4. Push to remote

## 4. Testing Strategy

### Type Safety Tests

```python
def test_device_manager_returns_typed_dto():
    """DeviceManager.get_devices() should return GetDevicesResponse DTO"""
    dm = make_device_manager(api_service=FakeAPIService())
    result = dm.get_devices()

    assert isinstance(result, GetDevicesResponse)
    assert hasattr(result, 'devices')
    assert hasattr(result, 'created_at')
    assert result.created_at is not None
```

### Backward Compatibility Tests

```python
def test_device_manager_devices_still_accessible():
    """Ensure downstream code can still access device data"""
    dm = make_device_manager(api_service=FakeAPIService())
    response = dm.get_devices()

    devices = response.devices
    assert isinstance(devices, list)
    assert all(isinstance(d, Device) for d in devices)
```

## 5. Risk Assessment

### Low Risk Changes:

- Adding DTO imports
- Updating type hints
- Internal refactoring

### Medium Risk Changes:

- Changing return types (breaking change for callers)
- Caching behavior modifications
- Error handling updates

### Mitigation:

- Keep extensive test coverage
- Run full test suite after each phase
- Use git branches for safety
- Type hints catch many issues early

## 6. Success Criteria

- [x] Phase 3.7.0: Audit complete
- [ ] Phase 3.7.1: DeviceManager refactored, tests passing
- [ ] Phase 3.7.2: Communication managers refactored, tests passing
- [ ] Phase 3.7.3: Music managers refactored, tests passing
- [ ] Phase 3.7.4: Complex managers refactored, tests passing
- [ ] Phase 3.7.5: All 775+ tests passing
- [ ] Phase 3.7.6: Committed and pushed
- **Final**: Complete type-safe manager ecosystem with DTOs

## 7. Next Steps

1. Start with DeviceManager (foundational)
2. Test thoroughly before moving to others
3. Update tests incrementally
4. Verify no regressions
5. Push once complete and tested

---

**Estimated Total Time**: 3-4 hours
**Token Budget**: ~55k remaining from 200k
**Status**: Ready to begin Phase 3.7.1
