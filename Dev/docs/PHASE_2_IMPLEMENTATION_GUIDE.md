# Phase 2 Implementation Guide - Manager Inheritance Refactoring

## Completed ✅

- [x] 1. CSRF Token Centralization (core/security/csrf_manager.py)
- [x] 2. Secure Headers Builder (core/security/secure_headers.py)
- [x] 3. Input Validators (core/security/validators.py)
- [x] 4. CircuitBreaker Registry (core/breaker_registry.py)

## TODO - Quick Implementation Template

### Pattern: Convert Manager to BaseManager Inheritance

**Before (RoutineManager example):**

```python
class RoutineManager:
    def __init__(self, auth, config, state_machine=None, cache_service=None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.cache_service = cache_service or CacheService()
        self.breaker = CircuitBreaker(...)  # ← DUPLICATED
        self._lock = threading.RLock()      # ← DUPLICATED
        # ... more duplicate code
```

**After (BaseManager Inheritance):**

```python
from core.base_manager import BaseManager, create_http_client_from_auth

class RoutineManager(BaseManager[Dict[str, Any]]):
    def __init__(self, auth, config, state_machine=None, cache_service=None):
        http_client = create_http_client_from_auth(auth)
        super().__init__(
            http_client=http_client,
            config=config,
            state_machine=state_machine,
            cache_service=cache_service,
            cache_ttl=300
        )
        self.auth = auth  # Keep for backward compatibility if needed
```

### Key Changes

1. **Imports:**

   - Remove: `import threading`, `from core.circuit_breaker import CircuitBreaker`
   - Add: `from core.base_manager import BaseManager, create_http_client_from_auth`

2. **Class Definition:**

   - Change: `class RoutineManager:`
   - To: `class RoutineManager(BaseManager[Dict[str, Any]]):`

3. ****init** Method:**

   - Remove breaker creation: `self.breaker = CircuitBreaker(...)`
   - Remove lock creation: `self._lock = threading.RLock()`
   - Remove cache initialization (inherited)
   - Add super().**init**() call

4. **API Calls:**

   - Replace: `self.breaker.call(http_client.method, url, ...)`
   - With: `self._api_call('method', endpoint, ...)`
   - Headers automatically injected by BaseManager

5. **Thread Safety:**
   - Use inherited `self._lock` for critical sections
   - Use inherited `self.breaker` for circuit breaking
   - Use inherited `self.cache_service` for caching

### Managers to Refactor (Priority Order)

1. **RoutineManager** (200+ lines)

   - File: `core/routines/routine_manager.py`
   - Status: Started
   - Effort: 1 hour

2. **PlaybackManager** (150+ lines)

   - File: `core/music/playback_manager.py`
   - Status: Not started
   - Effort: 1 hour

3. **TuneInManager** (80+ lines)

   - File: `core/music/tunein_manager.py`
   - Status: Not started
   - Effort: 30 min

4. **LibraryManager** (70+ lines)

   - File: `core/music/library_manager.py`
   - Status: Not started
   - Effort: 30 min

5. **ListsManager** (60+ lines)

   - File: `core/lists/lists_manager.py`
   - Status: Not started
   - Effort: 30 min

6. **BluetoothManager** (50+ lines)

   - File: `core/audio/bluetooth_manager.py`
   - Status: Not started
   - Effort: 20 min

7. **EqualizerManager** (50+ lines)

   - File: `core/audio/equalizer_manager.py`
   - Status: Not started
   - Effort: 20 min

8. **DeviceSettingsManager** (60+ lines)
   - File: `core/settings/device_settings_manager.py`
   - Status: Not started
   - Effort: 30 min

### Total Refactoring Effort

- **Lines to eliminate:** ~560
- **Estimated time:** 4-5 hours
- **Test coverage target:** 95%+
- **Breaking changes:** None (backward compatible)

### Testing Strategy

1. Write TDD tests for each manager BEFORE refactoring
2. Keep old managers as "\_old.py" during refactoring
3. Run tests to ensure behavior is identical
4. Delete old files once tests pass
5. Integration tests to verify with CLI commands

### Rollback Plan

If issues occur:

```bash
git reset --hard HEAD~1  # Rollback last commit
git checkout origin/main core/  # Restore from main if needed
```

## Next Steps

1. Complete RoutineManager inheritance
2. Refactor PlaybackManager
3. Bulk refactor remaining 6 managers
4. Run full test suite (target 95%+)
5. Commit all changes with comprehensive message
6. Merge refacto → main for v2.0 release

---

**Date:** 16 octobre 2025
**Phase:** 2 - Manager Inheritance & Code Deduplication
**Status:** 50% Complete
**Blocked:** None
