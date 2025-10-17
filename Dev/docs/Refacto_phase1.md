
# 🏢 PROFESSIONAL REFACTORING PROMPT - AlexaAPIService Centralization

**Project**: Alexa Voice Control CLI  
**Objective**: Phase 1 - Centralize API Calls  
**Methodology**: TDD (Test-Driven Development)  
**Environment**: VSCode + Git + Python 3.8+  
**Duration**: 2-3 sprints (2 weeks)

---

## 📋 EXECUTIVE BRIEF

### Context
The current codebase has dispersed API calls throughout managers and auth services, leading to:
- Hardcoded endpoints across multiple files
- No centralized error handling
- Missing circuit breaker implementation (pybreaker in requirements but unused)
- Difficult to test managers in isolation
- High maintenance burden for API changes

### Goal
Create `AlexaAPIService` as a single source of truth for all HTTP communication with Alexa APIs, following SOLID principles and enabling full test coverage.

### Success Criteria
- ✅ All API calls routed through AlexaAPIService
- ✅ 100% unit test coverage (>90% for new code)
- ✅ Circuit breaker integrated (pybreaker)
- ✅ Cache fallback on API failure
- ✅ Centralized error handling with typed exceptions
- ✅ Request logging with correlation IDs
- ✅ All existing tests pass (88/88)
- ✅ New tests added following AAA (Arrange-Act-Assert) pattern
- ✅ Code review ready with zero tech debt markers

---

## 🎯 PHASE 1 DETAILED BREAKDOWN

### 1.1 Audit & Discovery (3-5 days)
**Objective**: Map current API call patterns

**Tasks**:
```bash
# Task 1.1.1: Identify all HTTP calls
grep -r "self\._auth\.post\|self\._auth\.get\|requests\." \
  --include="*.py" core/ services/ | tee audit_api_calls.txt

# Task 1.1.2: Extract all endpoints
grep -oP "https?://[^\"'\s]+" core/ services/ \
  --include="*.py" -r | sort | uniq | tee endpoints_list.txt

# Task 1.1.3: Document current patterns
# Create audit_report.md with:
# - All endpoints used
# - Current error handling
# - Timeout values
# - Retry logic (if any)
```

**Deliverables**:
- `docs/audit_report.md` - Current state documentation
- `docs/endpoints_mapping.json` - All endpoints with usage count
- Jira/GitHub issue documenting findings

**Definition of Done**:
- [ ] All API calls identified
- [ ] Endpoints documented with usage location
- [ ] Error patterns identified
- [ ] Report approved by team lead

---

### 1.2 Design AlexaAPIService (2-3 days)

**Objective**: Create architecture before implementation

**Design Document** (`docs/design_alexa_api_service.md`):
```markdown
# AlexaAPIService Design

## Architecture

### Responsibility: Single Source of Truth for all API calls
- No HTTP calls outside this service
- All endpoints defined in one place
- Centralized error handling
- Unified timeout/retry logic
- Circuit breaker integration
- Cache fallback strategy

### Dependencies
- `alexa_auth.AlexaAuth` - Session management only
- `services.cache_service.CacheService` - Fallback caching
- `core.exceptions` - Typed exceptions
- `pybreaker.CircuitBreaker` - Resilience
- `loguru.logger` - Structured logging

### Class Structure
```python
class AlexaAPIService:
    ENDPOINTS = {...}  # All API endpoints
    
    def __init__(self, auth: AlexaAuth, cache: CacheService)
    
    # Public interface: Domain-specific methods
    def get_devices(self) -> List[DeviceDTO]
    def send_speak_command(self, device_id: str, text: str)
    def get_music_status(self, device_id: str)
    
    # Private: Generic HTTP call with resilience
    def _call(self, method: str, endpoint: str, data=None)
```

### Error Handling Strategy
- APIError wrapper for all HTTP errors
- CircuitBreakerOpenError when CB trips
- Fallback to cache on failure (with warning)
- Structured logging of all failures

### Testing Strategy
- Mock AlexaAuth at session level
- Mock responses from cache
- Test circuit breaker behavior
- Test timeout scenarios
- Test retry logic
```

**Deliverables**:
- `docs/design_alexa_api_service.md`
- Architecture diagram (ASCII or Mermaid)
- Decision log (why this design)

---

### 1.3 Implement AlexaAPIService - TDD Approach (5-7 days)

#### 1.3.1 Test First - Write Failing Tests

**File**: `Dev/pytests/services/test_alexa_api_service.py`

```python
# DO NOT IMPLEMENT YET - WRITE TESTS FIRST!

import pytest
from unittest.mock import Mock, MagicMock, patch
from core.exceptions import APIError, CircuitBreakerOpenError
from services.alexa_api_service import AlexaAPIService

class TestAlexaAPIServiceInitialization:
    """Test service initialization and configuration"""
    
    def test_service_initializes_with_auth_and_cache(self):
        """Service should initialize with dependencies"""
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        assert service._auth == auth
        assert service._cache == cache
    
    def test_service_has_all_endpoints_defined(self):
        """All endpoints must be centralized in ENDPOINTS dict"""
        assert hasattr(AlexaAPIService, 'ENDPOINTS')
        assert isinstance(AlexaAPIService.ENDPOINTS, dict)
        assert len(AlexaAPIService.ENDPOINTS) > 0
        # Verify structure: "key": "path"
        for key, path in AlexaAPIService.ENDPOINTS.items():
            assert isinstance(key, str)
            assert isinstance(path, str)
            assert path.startswith("/api/")

class TestGetDevices:
    """Test get_devices() method"""
    
    def test_get_devices_returns_list_of_devices(self):
        """get_devices should return list of valid device objects"""
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "devices": [
                {"serialNumber": "ABC123", "deviceName": "Salon"},
                {"serialNumber": "DEF456", "deviceName": "Cuisine"},
            ]
        }
        auth.get.return_value = mock_response
        
        result = service.get_devices()
        
        assert len(result) == 2
        assert result[0]["serialNumber"] == "ABC123"
    
    def test_get_devices_raises_api_error_on_failure(self):
        """get_devices should raise APIError on HTTP failure"""
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        
        auth.get.side_effect = Exception("Connection failed")
        
        with pytest.raises(APIError):
            service.get_devices()
    
    def test_get_devices_falls_back_to_cache_on_failure(self):
        """get_devices should use cache fallback when API fails"""
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        
        auth.get.side_effect = Exception("API down")
        cache.get.return_value = {"devices": [{"serialNumber": "CACHED"}]}
        
        result = service.get_devices(use_cache_fallback=True)
        
        assert result[0]["serialNumber"] == "CACHED"

class TestCircuitBreaker:
    """Test circuit breaker integration"""
    
    def test_circuit_breaker_opens_after_failures(self):
        """Circuit breaker should open after N failures"""
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        
        auth.get.side_effect = Exception("Failure")
        
        # Trigger failures
        for _ in range(5):  # Adjust threshold to actual
            try:
                service.get_devices()
            except:
                pass
        
        # Next call should raise CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            service.get_devices()
    
    def test_circuit_breaker_recovery(self):
        """Circuit breaker should recover after timeout"""
        # Implementation depends on pybreaker behavior

class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_http_401_raises_authentication_error(self):
        """401 response should raise AuthenticationError"""
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        
        auth.get.side_effect = APIError("Unauthorized", status_code=401)
        
        with pytest.raises(APIError) as exc_info:
            service.get_devices()
        assert exc_info.value.status_code == 401
    
    def test_http_429_raises_rate_limit_error(self):
        """429 response should raise RateLimitError"""
        # Requires custom RateLimitError exception

class TestRequestLogging:
    """Test request logging with correlation IDs"""
    
    def test_request_logged_with_correlation_id(self, caplog):
        """Each request should be logged with correlation ID"""
        auth = Mock()
        cache = Mock()
        service = AlexaAPIService(auth, cache)
        
        mock_response = Mock()
        mock_response.json.return_value = {"devices": []}
        auth.get.return_value = mock_response
        
        with caplog.at_level("DEBUG"):
            service.get_devices()
        
        # Verify log contains correlation_id
        assert "correlation_id" in caplog.text or "request_id" in caplog.text
```

**Run Tests (they should fail)**:
```bash
cd alexa_full_control
pytest Dev/pytests/services/test_alexa_api_service.py -v
# Expected: All tests FAIL (red)
```

#### 1.3.2 Implement to Make Tests Pass

**File**: `services/alexa_api_service.py`

```python
"""
Centralized service for all Alexa API communication.

Single source of truth for:
- All API endpoints
- HTTP method handling (GET, POST, etc)
- Timeout and retry logic
- Circuit breaker integration
- Error handling and wrapping
- Request logging with correlation IDs
- Cache fallback strategy

This service ensures consistency and enables easy modification
of API interaction patterns without touching individual managers.
"""

import uuid
from typing import Any, Dict, List, Optional

from loguru import logger
from pybreaker import CircuitBreaker

from alexa_auth.alexa_auth import AlexaAuth
from core.exceptions import APIError, AuthenticationError
from services.cache_service import CacheService


class AlexaAPIService:
    """
    Centralized API communication service.
    
    Replaces direct AlexaAuth usage in managers with a domain-aware service.
    Provides typed methods for each API operation instead of generic HTTP calls.
    """

    # Central endpoint registry - single source of truth
    ENDPOINTS = {
        "get_devices": "/api/devices-v2/device",
        "speak": "/api/speak",
        # Add all endpoints discovered in audit
    }

    def __init__(
        self,
        auth: AlexaAuth,
        cache: CacheService,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
    ):
        """
        Initialize API service.
        
        Args:
            auth: AlexaAuth session manager
            cache: CacheService for fallback
            circuit_breaker_threshold: Failures before opening circuit
            circuit_breaker_timeout: Seconds to wait before half-open
        """
        self._auth = auth
        self._cache = cache
        self._circuit_breaker = CircuitBreaker(
            fail_max=circuit_breaker_threshold,
            reset_timeout=circuit_breaker_timeout,
        )

    def get_devices(
        self, use_cache_fallback: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve list of devices.
        
        Args:
            use_cache_fallback: Use cached devices if API fails
            
        Returns:
            List of device dictionaries
            
        Raises:
            APIError: If API call fails and no cache available
        """
        cache_key = "devices_list"
        
        try:
            url = f"https://alexa.{self._auth.amazon_domain}{self.ENDPOINTS['get_devices']}"
            response = self._circuit_breaker.call(
                self._auth.get,
                url,
                timeout=10,
            )
            devices = response.json().get("devices", [])
            
            logger.info(
                "Devices retrieved successfully",
                extra={
                    "count": len(devices),
                    "correlation_id": self._get_correlation_id(),
                }
            )
            return devices
            
        except Exception as e:
            logger.warning(f"get_devices failed: {e}")
            
            if use_cache_fallback:
                cached = self._cache.get(cache_key, ignore_ttl=True)
                if cached:
                    logger.info("Falling back to cached devices")
                    return cached.get("devices", [])
            
            raise APIError(f"Failed to get devices: {e}") from e

    def send_speak_command(
        self, device_serial: str, text: str
    ) -> None:
        """
        Send speak command to device.
        
        Args:
            device_serial: Device serial number
            text: Text to speak
            
        Raises:
            APIError: If API call fails
            AuthenticationError: If CSRF token missing
        """
        try:
            url = f"https://alexa.{self._auth.amazon_domain}{self.ENDPOINTS['speak']}"
            payload = {
                "deviceSerialNumber": device_serial,
                "textToSpeak": text,
            }
            
            self._circuit_breaker.call(
                self._auth.post,
                url,
                data=payload,
                timeout=10,
            )
            
            logger.info(
                "Speak command sent",
                extra={
                    "device": device_serial,
                    "correlation_id": self._get_correlation_id(),
                }
            )
            
        except Exception as e:
            logger.error(f"send_speak_command failed: {e}")
            raise APIError(f"Failed to send speak command: {e}") from e

    def _get_correlation_id(self) -> str:
        """Get or create correlation ID for request tracing."""
        if not hasattr(self, '_current_correlation_id'):
            self._current_correlation_id = str(uuid.uuid4())
        return self._current_correlation_id
```

**Run Tests Again**:
```bash
pytest Dev/pytests/services/test_alexa_api_service.py -v
# Expected: Tests PASS (green)
```

#### 1.3.3 Refactor Existing Code to Use New Service

**File**: `core/managers/scenario_manager.py` (BEFORE)
```python
# OLD CODE - DIRECT API CALLS
def execute_scenario(self, name: str, device_resolver: callable) -> None:
    scenario = self.find_scenario(name)
    
    # Hardcoded endpoint!
    endpoint = f"https://alexa.{self._auth.amazon_domain}/api/speak"
    payload = {"deviceSerialNumber": device["serialNumber"], ...}
    self._auth.post(endpoint, data=payload)
```

**File**: `core/managers/scenario_manager.py` (AFTER)
```python
# NEW CODE - USE ALEXA API SERVICE
def execute_scenario(self, name: str, device_resolver: callable) -> None:
    scenario = self.find_scenario(name)
    
    # Use centralized service
    self._api_service.send_speak_command(
        device_serial=device["serialNumber"],
        text=text_to_speak,
    )
```

**Update __init__.py**:
```python
def __init__(
    self,
    json_storage: JsonStorage,
    api_service: AlexaAPIService,  # NEW
):
    self._storage = json_storage
    self._api_service = api_service  # Use this instead of auth
```

**Test Changes**:
```bash
# Run ALL tests to ensure nothing broke
pytest Dev/pytests/ -v --tb=short
# Expected: 88/88 tests PASS
```

**Git Workflow**:
```bash
# Stage refactored manager
git add core/managers/scenario_manager.py
git commit -m "refactor(scenario): use AlexaAPIService instead of direct auth calls

- Replace hardcoded endpoints with service methods
- Remove direct AlexaAuth dependency (now injected)
- Update tests for new dependency structure

Relates to: #PHASE1-CENTRALIZE-API"

# Push feature branch
git push origin feature/phase1-api-centralization
```

---

### 1.4 Update All Managers (3-5 days)

For each manager in `core/managers/`:

**Process** (repeat for each file):
1. Replace direct `self._auth.post/get` calls with `self._api_service.method()`
2. Remove hardcoded endpoints
3. Update unit tests
4. Run full test suite
5. Commit with clear message

**Example Managers to Update**:
- `device_manager.py`
- `music_manager.py`
- `multiroom_manager.py`
- etc.

**Command Template**:
```bash
# For each manager
pytest Dev/pytests/core/managers/test_<manager>.py -v
# Fix failures
git add core/managers/<manager>.py
git commit -m "refactor(<domain>): migrate to AlexaAPIService

- Replace direct auth calls with API service methods
- Remove endpoint hardcodes
- All tests passing (X/X)

Relates to: #PHASE1"
```

---

### 1.5 Integration Testing (2-3 days)

**File**: `Dev/pytests/integration/test_phase1_integration.py`

```python
"""Integration tests for Phase 1 refactoring"""

import pytest
from services.alexa_api_service import AlexaAPIService

class TestPhase1Integration:
    """Verify all managers work with new API service"""
    
    def test_scenario_execution_uses_api_service(self):
        """Scenario manager should use API service, not direct auth"""
        # Full flow test
        pass
    
    def test_all_api_calls_go_through_api_service(self):
        """No direct self._auth.post calls outside AlexaAPIService"""
        # Grep check in test
        pass
    
    def test_circuit_breaker_protects_all_operations(self):
        """All operations should benefit from circuit breaker"""
        # Verify behavior
        pass
```

**Run**:
```bash
pytest Dev/pytests/integration/ -v
# Expected: All pass
```

---

### 1.6 Code Review Checklist

**Before merging to main/refacto**:

```
CHECKLIST: Phase 1 - AlexaAPIService

Code Quality:
- [ ] No hardcoded endpoints outside ENDPOINTS dict
- [ ] No direct HTTP calls outside AlexaAPIService
- [ ] All methods have docstrings (Args, Returns, Raises)
- [ ] Type hints on all parameters and returns
- [ ] No commented-out code
- [ ] No debug print statements

Testing:
- [ ] 100% test coverage on AlexaAPIService (use: pytest --cov)
- [ ] All 88 existing tests pass (pytest Dev/pytests/ -v)
- [ ] New integration tests pass
- [ ] Circuit breaker tested
- [ ] Cache fallback tested
- [ ] Error scenarios tested

Refactoring:
- [ ] All managers updated to use new service
- [ ] No remaining direct auth.post/get calls in managers
- [ ] All manager tests updated and passing
- [ ] No breaking changes to CLI interface

Documentation:
- [ ] AlexaAPIService docstring complete
- [ ] Methods documented with examples
- [ ] Design decisions documented in docs/
- [ ] MIGRATION.md updated (if needed)
- [ ] Architecture diagram updated

Git Quality:
- [ ] Commits have descriptive messages
- [ ] Each commit is logical, self-contained
- [ ] No merge commits (rebase if needed)
- [ ] Branch up-to-date with main

Production Readiness:
- [ ] No console.log or debug statements
- [ ] Error messages informative for users
- [ ] Logging appropriate level (not DEBUG by default)
- [ ] Performance: No new N+1 queries
```

**Run Coverage Report**:
```bash
pytest Dev/pytests/services/test_alexa_api_service.py \
  --cov=services.alexa_api_service \
  --cov-report=html

# Verify >95% coverage
open htmlcov/index.html
```

---

## 📝 GIT WORKFLOW TEMPLATE

### Commit Discipline

```bash
# Branch naming
git checkout -b feature/phase1-api-centralization

# Atomic commits (one logical change per commit)
git add services/alexa_api_service.py
git commit -m "feat(services): create AlexaAPIService as API gateway

- Centralize all Alexa API endpoints in single registry
- Integrate pybreaker circuit breaker for resilience
- Implement cache fallback on API failures
- Add structured logging with correlation IDs
- Full test coverage (100%)

Addresses: Phase 1 Requirement
Test: pytest services/test_alexa_api_service.py -v [PASS 23/23]"

# Code review
git push origin feature/phase1-api-centralization

# After approval and tests pass
git checkout refacto
git pull origin refacto
git merge --ff-only feature/phase1-api-centralization
git push origin refacto

# Tag milestone
git tag -a phase1-api-centralization -m "Phase 1 Complete: API Centralization"
git push origin phase1-api-centralization
```

### Branch Strategy
```
main (production)
  ↓
refacto (development)
  ↓
feature/phase1-api-centralization (your work)
  ↓
feature/phase1-api-centralization/audit (specific sub-task)
feature/phase1-api-centralization/implementation
feature/phase1-api-centralization/integration-tests
```

---

## 🧪 TDD RHYTHM

### Daily Workflow

**Morning** (Planning):
```
1. Review test failures
2. Pick next test to implement
3. Write minimal test
4. Red ← verify test fails
```

**Midday** (Implementation):
```
1. Write minimal code to pass test
2. Green ← verify test passes
3. Refactor code (keep tests green)
4. Commit
```

**Evening** (Integration):
```
1. Run full test suite: pytest -v
2. Ensure no regressions
3. Code review own changes
4. Document decisions in commit messages
```

### Test Command Aliases (add to `.bashrc` or `.zshrc`)
```bash
alias pt='pytest Dev/pytests/ -v'
alias ptt='pytest Dev/pytests/ -v --tb=short'
alias ptf='pytest Dev/pytests/ -v -x'  # Stop on first failure
alias ptc='pytest Dev/pytests/ --cov=services --cov=core'
alias ptkill='pytest Dev/pytests/ -v -k'  # Run specific test
```

---

## 📊 DEFINITION OF DONE (Phase 1)

**Code**:
- [ ] AlexaAPIService implemented with 100% coverage
- [ ] All 40 commands updated to use service (0 direct auth calls)
- [ ] All 88 existing tests passing
- [ ] 30+ new tests written (test-first)

**Documentation**:
- [ ] ARCHITECTURE.md updated with AlexaAPIService pattern
- [ ] API endpoints documented (ENDPOINTS dict with descriptions)
- [ ] Error handling strategy documented
- [ ] Migration guide for future developers

**Quality Metrics**:
- [ ] Code coverage: >95%
- [ ] Cyclomatic complexity: <10 per method
- [ ] Type safety: 100% (mypy passes)
- [ ] Linting: 0 errors (ruff, pylint, flake8)

**Testing**:
- [ ] Unit tests: AlexaAPIService (23/23)
- [ ] Integration tests: Managers (15+/15+)
- [ ] End-to-end: Full scenario flow

**Git**:
- [ ] All commits have detailed messages
- [ ] No merge conflicts
- [ ] Rebased on latest refacto branch
- [ ] Ready for production

---

## 🚀 EXECUTION CHECKLIST

Week 1:
- [ ] Audit complete (1.1)
- [ ] Design reviewed (1.2)
- [ ] Tests written (1.3.1)
- [ ] Implementation started (1.3.2)

Week 2:
- [ ] Implementation complete (1.3.2)
- [ ] Managers refactored (1.4)
- [ ] Integration tests pass (1.5)

Week 3:
- [ ] Code review (1.6)
- [ ] Final polish
- [ ] Merge to main
- [ ] Documentation complete

---

## 📞 SUPPORT RESOURCES

- PyTest Documentation: https://docs.pytest.org/
- PyBreaker: https://github.com/danielfm/pybreaker
- Loguru: https://loguru.readthedocs.io/
- SOLID Principles: https://en.wikipedia.org/wiki/SOLID
- TDD by Robert Martin: https://www.youtube.com/watch?v=GvAzrC6-spQ