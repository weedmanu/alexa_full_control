# Phase 3: PROFESSIONAL REFACTORING PROMPT - Pydantic Schemas & DTOs

**Project**: Alexa Voice Control CLI  
**Objective**: Phase 3 - Type-Safe Data Contracts  
**Methodology**: TDD + Schema-First Design  
**Depends On**: Phase 1 (AlexaAPIService) + Phase 2 (Configuration) COMPLETE  
**Duration**: 2-3 sprints (12-15 days)

---

## 📋 EXECUTIVE BRIEF

### Context
Current implementation lacks data contracts:
- API responses treated as raw dictionaries
- No validation of API data structure
- Runtime errors from unexpected response formats
- Difficult to document API contracts
- IDE auto-completion missing for API responses
- No clear separation between internal/external data models

### Goal
Create comprehensive Pydantic DTO (Data Transfer Object) layer providing:
- Type-safe data contracts for all API interactions
- Automatic validation of incoming/outgoing data
- Clear API documentation through schemas
- IDE support with auto-completion
- Runtime error detection before business logic

### Success Criteria
- ✅ All API requests have request DTOs
- ✅ All API responses have response DTOs
- ✅ 100% of API calls use DTOs
- ✅ Automatic validation on all boundaries
- ✅ All 88+ existing tests pass
- ✅ 40+ new schema tests added
- ✅ JSON Schema documentation auto-generated
- ✅ Zero unhandled response format errors

---

## 🎯 PHASE 3 DETAILED BREAKDOWN

### 3.1 API Contract Audit & Discovery (2-3 days)

**Objective**: Document all API data structures

**Tasks**:

```bash
# Task 3.1.1: Audit all API responses
# Run actual commands and capture response structures
python -c "
from alexa_auth.alexa_auth import AlexaAuth
from services.cache_service import CacheService

# Get sample responses from actual API or mocks
# Document structure in docs/api_contracts.md
"

# Task 3.1.2: Document request/response pairs
cat > docs/api_contracts.md << 'EOF'
# API Contracts

## GET /api/devices-v2/device

### Response
```json
{
  "devices": [
    {
      "serialNumber": "string",
      "deviceName": "string",
      "deviceType": "string (ECHO, ECHO_DOT, etc)",
      "online": boolean,
      "supportedOperations": ["string"],
      "capabilities": ["string"]
    }
  ]
}
```

## POST /api/speak

### Request
```json
{
  "deviceSerialNumber": "string",
  "textToSpeak": "string"
}
```

### Response
```json
{
  "success": true
}
```

### Errors
- 401: Unauthorized
- 404: Device not found
- 429: Rate limited
EOF
```

**Deliverables**:
- `docs/api_contracts.md` - All API contracts documented
- `docs/dto_mapping.json` - Request/Response mapping

**Definition of Done**:
- [ ] All endpoints documented
- [ ] Request/response structures captured
- [ ] Error responses documented
- [ ] Edge cases identified

---

### 3.2 Design DTO Layer Architecture (2-3 days)

**Objective**: Plan DTO structure and organization

**Design Document** (`docs/design_dto_layer.md`):

```markdown
# DTO Layer Design

## Directory Structure
```
core/
├── schemas/
│   ├── __init__.py
│   ├── base.py              # Base classes, common types
│   ├── device_schemas.py    # Device-related DTOs
│   ├── music_schemas.py     # Music-related DTOs
│   ├── auth_schemas.py      # Auth DTOs
│   ├── api_schemas.py       # Generic API response wrapper
│   └── validators.py        # Custom Pydantic validators
```

## DTO Naming Convention

### Request DTOs: `{Domain}Request` or `{Action}Request`
```python
class GetDevicesRequest(BaseModel):
    """Request for GET /api/devices"""
    pass  # Usually empty for GET requests

class SendSpeakCommandRequest(BaseModel):
    """Request for POST /api/speak"""
    device_serial: str
    text_to_speak: str
```

### Response DTOs: `{Domain}Response` or `{Noun}DTO`
```python
class Device(BaseModel):
    """Single device data"""
    serial_number: str
    device_name: str
    device_type: str
    online: bool

class GetDevicesResponse(BaseModel):
    """Response from GET /api/devices"""
    devices: List[Device]
```

## Inheritance Hierarchy

```
BaseModel (Pydantic)
├── BaseDTOModel         # Custom base with common config
│   ├── RequestDTO       # All requests inherit
│   ├── ResponseDTO      # All responses inherit
│   └── DomainModel      # Domain objects (Device, Music, etc)
```

## Common Features

- Config: `model_config = ConfigDict(str_strip_whitespace=True)`
- Validators: `field_validator('field_name')`
- Examples in docstrings for documentation
- `frozen=True` for immutability where appropriate

## Error Handling

Every endpoint response includes error possibilities:
```python
class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
```

## Validation Strategy

- **Pydantic v2** features for modern validation
- Custom validators for complex business logic
- Coercion for common transforms (strip, lowercase)
- Clear error messages for invalid data
```

**Deliverables**:
- `docs/design_dto_layer.md`
- Architecture diagram
- Naming conventions document

---

### 3.3 Implement Base DTO Layer (1-2 days)

**File**: `core/schemas/base.py`

```python
"""
Base classes and common types for all DTOs.

Provides consistent configuration, validation patterns,
and reusable types across all schemas.
"""

from typing import Any, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class BaseDTOModel(BaseModel):
    """
    Base class for all DTOs with common configuration.
    
    Features:
    - Whitespace stripping on all strings
    - Forbid extra fields (strict mode)
    - JSON serialization support
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",  # Reject unknown fields
        populate_by_name=True,  # Accept both camelCase and snake_case
        json_schema_extra={
            "examples": [],  # Override in subclasses
        }
    )


class RequestDTO(BaseDTOModel):
    """Base class for all API request DTOs"""
    
    class Config:
        """Request DTOs are immutable"""
        frozen = True


class ResponseDTO(BaseDTOModel):
    """Base class for all API response DTOs"""
    
    created_at: Optional[datetime] = None
    
    class Config:
        """Response DTOs are immutable"""
        frozen = True


class APIErrorDTO(BaseDTOModel):
    """Standard API error response"""
    
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
    
    class Config:
        frozen = True


class APISuccessResponse(BaseDTOModel, Generic[T]):
    """Generic success response wrapper"""
    
    success: bool = True
    data: T
    
    class Config:
        frozen = True
```

---

### 3.4 Implement Device Schemas - TDD (3-4 days)

#### 3.4.1 Write Tests First

**File**: `Dev/pytests/core/schemas/test_device_schemas.py`

```python
"""Tests for device-related schemas"""

import pytest
from pydantic import ValidationError
from core.schemas.device_schemas import (
    Device,
    GetDevicesRequest,
    GetDevicesResponse,
)


class TestDeviceSchema:
    """Test Device DTO"""
    
    def test_device_from_amazon_response(self):
        """Parse actual Amazon API response"""
        data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "deviceType": "ECHO_DOT",
            "online": True,
        }
        device = Device(**data)
        
        assert device.serial_number == "ABC123"
        assert device.device_name == "Salon"
        assert device.online is True
    
    def test_device_requires_serial_number(self):
        """serial_number is required"""
        data = {
            "deviceName": "Salon",
            "online": True,
        }
        with pytest.raises(ValidationError):
            Device(**data)
    
    def test_device_rejects_unknown_fields(self):
        """Unknown fields should be rejected"""
        data = {
            "serialNumber": "ABC123",
            "deviceName": "Salon",
            "online": True,
            "unknownField": "value",
        }
        with pytest.raises(ValidationError):
            Device(**data)
    
    def test_device_strips_whitespace(self):
        """Whitespace should be stripped from strings"""
        data = {
            "serialNumber": "  ABC123  ",
            "deviceName": "  Salon  ",
            "online": True,
        }
        device = Device(**data)
        
        assert device.serial_number == "ABC123"
        assert device.device_name == "Salon"
    
    def test_device_to_json(self):
        """Device serializes to JSON correctly"""
        device = Device(
            serial_number="ABC123",
            device_name="Salon",
            online=True,
        )
        
        json_data = device.model_dump_json()
        assert "ABC123" in json_data
        assert "Salon" in json_data


class TestGetDevicesResponse:
    """Test GetDevicesResponse DTO"""
    
    def test_parse_devices_response(self):
        """Parse full devices response"""
        response_data = {
            "devices": [
                {
                    "serialNumber": "ABC123",
                    "deviceName": "Salon",
                    "deviceType": "ECHO",
                    "online": True,
                },
                {
                    "serialNumber": "DEF456",
                    "deviceName": "Cuisine",
                    "deviceType": "ECHO_DOT",
                    "online": False,
                }
            ]
        }
        
        response = GetDevicesResponse(**response_data)
        
        assert len(response.devices) == 2
        assert response.devices[0].serial_number == "ABC123"
        assert response.devices[1].online is False
    
    def test_empty_devices_list(self):
        """Empty devices list should be valid"""
        response = GetDevicesResponse(devices=[])
        assert len(response.devices) == 0
    
    def test_invalid_device_in_response(self):
        """Invalid device in response should raise error"""
        response_data = {
            "devices": [
                {
                    "deviceName": "Salon",
                    # Missing required serialNumber
                }
            ]
        }
        
        with pytest.raises(ValidationError):
            GetDevicesResponse(**response_data)
```

**Run Tests (should fail)**:
```bash
pytest Dev/pytests/core/schemas/test_device_schemas.py -v
# Expected: ALL FAIL (red)
```

#### 3.4.2 Implement Device Schemas

**File**: `core/schemas/device_schemas.py`

```python
"""Device-related DTOs"""

from typing import List, Optional
from core.schemas.base import ResponseDTO, RequestDTO


class Device(ResponseDTO):
    """
    Represents an Alexa device.
    
    Maps from Amazon API response:
    {
        "serialNumber": "...",
        "deviceName": "...",
        "deviceType": "...",
        "online": true
    }
    """
    
    serial_number: str  # From serialNumber
    device_name: str    # From deviceName
    device_type: str    # From deviceType (ECHO, ECHO_DOT, etc)
    online: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "serial_number": "ABC123XYZ",
                "device_name": "Salon",
                "device_type": "ECHO_DOT",
                "online": True,
            }
        }


class GetDevicesRequest(RequestDTO):
    """Request for GET /api/devices"""
    pass  # No parameters


class GetDevicesResponse(ResponseDTO):
    """
    Response from GET /api/devices-v2/device
    
    Contains list of all registered devices.
    """
    
    devices: List[Device]
    
    class Config:
        json_schema_extra = {
            "example": {
                "devices": [
                    {
                        "serial_number": "ABC123",
                        "device_name": "Salon",
                        "device_type": "ECHO",
                        "online": True,
                    }
                ]
            }
        }
```

**Run Tests**:
```bash
pytest Dev/pytests/core/schemas/test_device_schemas.py -v
# Expected: Tests PASS (green)
```

---

### 3.5 Implement All Remaining Schemas (4-5 days)

Follow same pattern for each domain:

**Files to create**:
- `core/schemas/music_schemas.py`
- `core/schemas/auth_schemas.py`
- `core/schemas/routine_schemas.py`
- `core/schemas/multiroom_schemas.py`
- `core/schemas/notification_schemas.py`
- etc.

**For each file**:
1. Write tests first (TDD)
2. Implement DTOs
3. Verify tests pass
4. Commit with clear message

**Example commit**:
```bash
git add core/schemas/music_schemas.py
git commit -m "feat(schemas): add music-related DTOs

- PlayMusicRequest: device, search term, service
- MusicStatusResponse: current track, artist, playing
- PlaylistDTO: name, tracks, duration
- Full Pydantic validation with examples

Test coverage: 100% (8/8 tests pass)"
```

---

### 3.6 Integrate DTOs Into AlexaAPIService (2-3 days)

**File**: `services/alexa_api_service.py` (update methods)

**BEFORE**:
```python
def get_devices(self) -> List[Dict[str, Any]]:
    """Return raw dict"""
    url = f"https://alexa.{self._config.api.amazon_domain}/api/devices"
    response = self._circuit_breaker.call(self._auth.get, url)
    return response.json().get("devices", [])
```

**AFTER**:
```python
def get_devices(self) -> GetDevicesResponse:
    """Return typed DTO with validation"""
    url = f"https://alexa.{self._config.api.amazon_domain}/api/devices"
    response = self._circuit_breaker.call(
        self._auth.get,
        url,
        timeout=self._config.api.request_timeout,
    )
    data = response.json()
    
    # Validate and parse with DTO
    try:
        devices_response = GetDevicesResponse(**data)
        logger.debug(f"Parsed {len(devices_response.devices)} devices")
        return devices_response
    except ValidationError as e:
        logger.error(f"Invalid devices response format: {e}")
        raise APIError(f"Invalid API response: {e}") from e
```

**Update all methods in AlexaAPIService to return DTOs**:
```bash
# Count methods to update
grep -c "def " services/alexa_api_service.py
# Update each one
```

---

### 3.7 Update Managers to Use DTOs (2-3 days)

**BEFORE** (`core/managers/scenario_manager.py`):
```python
def execute_scenario(self, name: str):
    devices = self._api_service.get_devices()
    # devices is List[Dict] - no type hints
    device = devices[0]
    device_id = device["serialNumber"]  # String magic!
```

**AFTER**:
```python
def execute_scenario(self, name: str):
    response = self._api_service.get_devices()
    # response is GetDevicesResponse - typed!
    device = response.devices[0]  # IDE auto-completes!
    device_id = device.serial_number  # Type-safe attribute
```

**Update all managers systematically**:
```bash
# For each manager file
for manager in core/managers/*.py; do
    # Update to use DTOs
    # Run tests
    pytest Dev/pytests/core/managers/test_*.py -v
done
```

---

### 3.8 Auto-Generate Documentation (1 day)

**File**: `scripts/generate_schema_docs.py`

```python
"""Auto-generate OpenAPI/JSON Schema documentation"""

from core.schemas.device_schemas import GetDevicesResponse
from core.schemas.music_schemas import PlayMusicRequest
import json


def generate_json_schema():
    """Generate JSON schema from all DTOs"""
    
    schemas = {
        "GetDevicesResponse": GetDevicesResponse.model_json_schema(),
        "PlayMusicRequest": PlayMusicRequest.model_json_schema(),
        # Add all DTOs
    }
    
    with open("docs/api_schemas.json", "w") as f:
        json.dump(schemas, f, indent=2)
    
    print("✅ Generated docs/api_schemas.json")


def generate_markdown_docs():
    """Generate Markdown documentation"""
    
    md_content = "# API Schemas\n\n"
    
    # For each DTO, generate documentation
    
    with open("docs/API_SCHEMAS.md", "w") as f:
        f.write(md_content)
    
    print("✅ Generated docs/API_SCHEMAS.md")


if __name__ == "__main__":
    generate_json_schema()
    generate_markdown_docs()
```

**Run**:
```bash
python scripts/generate_schema_docs.py
# Generates: docs/api_schemas.json + docs/API_SCHEMAS.md
```

---

### 3.9 Code Review Checklist - Phase 3

```
CHECKLIST: Phase 3 - Pydantic Schemas & DTOs

Schema Implementation:
- [ ] All request DTOs created
- [ ] All response DTOs created
- [ ] Proper inheritance from base classes
- [ ] All fields have proper types
- [ ] Validators added where needed
- [ ] Examples in docstrings
- [ ] No unused DTOs

DTO Features:
- [ ] Whitespace stripping enabled
- [ ] Extra fields forbidden (strict mode)
- [ ] Immutability where appropriate (frozen=True)
- [ ] JSON serialization works
- [ ] Field validation comprehensive
- [ ] Error messages clear

API Integration:
- [ ] AlexaAPIService returns DTOs
- [ ] All 40+ API calls validated
- [ ] No raw dicts returned from service
- [ ] Request validation before sending
- [ ] Response validation after receiving
- [ ] Errors wrapped in APIError

Manager Updates:
- [ ] All managers use typed responses
- [ ] IDE auto-completion works
- [ ] No string magic for field access
- [ ] Business logic simplified
- [ ] All manager tests updated

Testing:
- [ ] 100+ new schema tests
- [ ] All 88+ existing tests pass
- [ ] Validation error cases tested
- [ ] Edge cases covered
- [ ] JSON round-trip tested

Documentation:
- [ ] Auto-generated JSON schema
- [ ] Markdown API documentation
- [ ] Examples in each DTO
- [ ] Type system documented
- [ ] Migration guide for developers

Quality:
- [ ] Type coverage: 100%
- [ ] Mypy passes on all schema files
- [ ] No type: ignore comments
- [ ] No Any types (except where necessary)
```

---

## Definition of Done (Phase 3)

Code:
- [ ] 40+ DTOs implemented (100% API coverage)
- [ ] All 88+ existing tests passing
- [ ] 100+ new schema tests added
- [ ] AlexaAPIService fully integrated
- [ ] All managers updated

Documentation:
- [ ] API_SCHEMAS.md auto-generated
- [ ] JSON schema available
- [ ] Examples for each DTO
- [ ] Migration guide provided

Quality:
- [ ] Type safety: 100%
- [ ] Test coverage: >95%
- [ ] Mypy: 0 errors
- [ ] No validation warnings

Testing:
- [ ] Unit tests for each schema
- [ ] Integration tests for API calls
- [ ] Validation error tests
- [ ] Round-trip serialization tests

---

## Execution Timeline

Week 1:
- [ ] Days 1-2: API contract audit (3.1)
- [ ] Days 3-4: Design (3.2)
- [ ] Days 5-7: Base layer (3.3-3.4)

Week 2:
- [ ] Days 8-10: Implement schemas (3.5)
- [ ] Days 11-12: Integrate (3.6-3.7)

Week 3:
- [ ] Days 13-14: Documentation (3.8)
- [ ] Day 15: Code review (3.9)

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/phase3-pydantic-schemas

# Work on each domain (atomic commits)
git add core/schemas/device_schemas.py
git commit -m "feat(schemas): add device DTOs

- Device: serial_number, device_name, device_type
- GetDevicesRequest/Response: full contract
- Validation: required fields, field types
- Tests: 100% coverage (8/8 pass)"

# After all schemas complete
git push origin feature/phase3-pydantic-schemas

# Code review, then merge
```