# Test Structure Strategy - Consolidated Organization

## 📁 Test Directory Organization

### Current State

```
Dev/
├── pytests/              # TDD tests (security layer, new modules)
│   ├── __init__.py
│   ├── test_csrf_manager.py         ✅ (21/22 passing)
│   ├── test_input_validators.py     ✅ (40/41 passing)
│   ├── test_base_manager_headers.py
│   ├── test_integration.py
│   └── __pycache__/
│
└── tests/                # Legacy integration tests (30+ files)
    ├── test_exceptions.py
    ├── test_core.py
    ├── test_cli.py
    ├── test_alarm_manager.py
    ├── test_*_manager.py (multiple managers)
    └── ... (44 more test files)
```

### Target Structure

```
Dev/
├── pytests/              # TDD & Unit Tests (all new)
│   ├── __init__.py
│   ├── security/         # Phase 1 security layer tests
│   │   ├── __init__.py
│   │   ├── test_csrf_manager.py
│   │   ├── test_input_validators.py
│   │   └── test_secure_headers.py
│   │
│   ├── managers/         # Phase 2 manager inheritance tests
│   │   ├── __init__.py
│   │   ├── test_base_manager.py
│   │   ├── test_routine_manager.py
│   │   ├── test_playback_manager.py
│   │   └── ... (others by phase)
│   │
│   ├── core/             # Phase 3 core infrastructure tests
│   │   ├── __init__.py
│   │   ├── test_circuit_breaker_registry.py
│   │   ├── test_di_container.py  (future)
│   │   └── test_manager_factory.py (future)
│   │
│   ├── cli/              # Phase 3 CLI tests
│   │   ├── __init__.py
│   │   ├── test_command_parser.py
│   │   └── test_command_template.py (future)
│   │
│   ├── integration/      # Integration tests (cross-module)
│   │   ├── __init__.py
│   │   ├── test_full_workflow.py
│   │   ├── test_e2e_scenarios.py
│   │   └── test_security_integration.py
│   │
│   ├── fixtures/         # Shared test fixtures & mocks
│   │   ├── __init__.py
│   │   ├── mock_auth.py
│   │   ├── mock_http_client.py
│   │   ├── mock_managers.py
│   │   └── conftest.py   ← pytest fixtures
│   │
│   ├── conftest.py       ← Root pytest config (Dev/pytests/)
│   └── __pycache__/
│
└── tests/                # DEPRECATED (legacy, to be removed)
    ├── README.md         ← Note: Use Dev/pytests/ instead
    └── ... (old files keep for reference during migration)
```

### Root Level

```
alexa_full_control/
├── pytest.ini           ← Pytest configuration (stays at root)
├── pyproject.toml       ← Test config section (stays at root)
├── conftest.py          ← Root conftest if needed (optional)
├── run_tests.py         ← Test runner script (stays at root)
├── run_tests.ps1        ← Windows test runner (stays at root)
└── run_tests.sh         ← Unix test runner (stays at root)
```

## 📋 Migration Plan

### Phase 1: Organize Security Tests ✅ DONE

- [x] `Dev/pytests/security/test_csrf_manager.py`
- [x] `Dev/pytests/security/test_input_validators.py`
- [x] `Dev/pytests/security/__init__.py`
- [x] Create `Dev/pytests/fixtures/conftest.py`

### Phase 2: Manager Tests 🟡 IN PROGRESS

- [ ] `Dev/pytests/managers/test_routine_manager.py`
- [ ] `Dev/pytests/managers/test_playback_manager.py`
- [ ] `Dev/pytests/managers/test_tunein_manager.py`
- [ ] `Dev/pytests/managers/test_library_manager.py`
- [ ] `Dev/pytests/managers/test_lists_manager.py`
- [ ] `Dev/pytests/managers/test_bluetooth_manager.py`
- [ ] `Dev/pytests/managers/test_equalizer_manager.py`
- [ ] `Dev/pytests/managers/test_device_settings_manager.py`
- [ ] `Dev/pytests/managers/__init__.py`

### Phase 3: Core Infrastructure Tests ❌ NOT STARTED

- [ ] `Dev/pytests/core/test_circuit_breaker_registry.py`
- [ ] `Dev/pytests/core/test_di_container.py`
- [ ] `Dev/pytests/core/test_manager_factory.py`
- [ ] `Dev/pytests/core/__init__.py`

### Phase 4: CLI & Integration Tests ❌ NOT STARTED

- [ ] `Dev/pytests/cli/test_command_parser.py`
- [ ] `Dev/pytests/cli/test_command_template.py`
- [ ] `Dev/pytests/integration/test_full_workflow.py`
- [ ] `Dev/pytests/integration/test_e2e_scenarios.py`
- [ ] Create shared fixtures in `Dev/pytests/fixtures/`

### Phase 5: Cleanup ❌ NOT STARTED

- [ ] Move legacy `Dev/tests/` to `Dev/tests_legacy/`
- [ ] Update documentation in `Dev/tests/README.md`
- [ ] Update CI/CD to run `Dev/pytests/` instead
- [ ] Remove old test runners if no longer needed

## 🎯 Test Coverage Goals

| Phase     | Module    | Target   | Current  | Status         |
| --------- | --------- | -------- | -------- | -------------- |
| 1         | security/ | 95%+     | 97%      | ✅ Excellent   |
| 2         | managers/ | 90%+     | TBD      | 🟡 Starting    |
| 3         | core/     | 85%+     | TBD      | ❌ Not started |
| 4         | cli/      | 80%+     | TBD      | ❌ Not started |
| **TOTAL** | **ALL**   | **85%+** | **~40%** | 🟡 Mid-phase   |

## 📝 Root-Level Test Configuration Files

### `pytest.ini` (at root)

```ini
[pytest]
testpaths = Dev/pytests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=core --cov=cli --cov=services --cov=utils
    --cov-report=term-missing:skip-covered
    --cov-report=xml:coverage.xml
    --cov-report=html:Dev/coverage_html
    --durations=10
markers =
    unit: Unit tests for isolated components
    integration: Integration tests across modules
    security: Security-specific tests
    slow: Tests that take >1s
    cli: CLI command tests
```

### `pyproject.toml` (test section at root)

```toml
[tool.pytest.ini_options]
testpaths = ["Dev/pytests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--verbose --tb=short"

[tool.coverage.run]
source = ["core", "cli", "services", "utils"]
omit = ["*/__pycache__/*", "*/venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

### `run_tests.ps1` (Windows, at root)

```powershell
# Run all tests in Dev/pytests
python -m pytest Dev/pytests -v --cov=core --cov=cli --cov-report=html

# Or specific suite
# python -m pytest Dev/pytests/security -v
# python -m pytest Dev/pytests/managers -v
```

### `run_tests.sh` (Unix, at root)

```bash
#!/bin/bash
# Run all tests in Dev/pytests
python -m pytest Dev/pytests -v --cov=core --cov=cli --cov-report=html
```

## 🔧 Implementation Steps

### Step 1: Create Directory Structure

```bash
mkdir -p Dev/pytests/security
mkdir -p Dev/pytests/managers
mkdir -p Dev/pytests/core
mkdir -p Dev/pytests/cli
mkdir -p Dev/pytests/integration
mkdir -p Dev/pytests/fixtures
touch Dev/pytests/__init__.py
touch Dev/pytests/security/__init__.py
touch Dev/pytests/managers/__init__.py
touch Dev/pytests/core/__init__.py
touch Dev/pytests/cli/__init__.py
touch Dev/pytests/integration/__init__.py
touch Dev/pytests/fixtures/__init__.py
touch Dev/pytests/fixtures/conftest.py
```

### Step 2: Move Existing Tests

```bash
# Move existing pytest tests
mv Dev/pytests/test_csrf_manager.py Dev/pytests/security/
mv Dev/pytests/test_input_validators.py Dev/pytests/security/
mv Dev/pytests/test_base_manager_headers.py Dev/pytests/managers/

# Create new test files as managers are refactored
# (See Phase 2 Manager Refactoring)
```

### Step 3: Create Fixtures

- `Dev/pytests/fixtures/mock_auth.py` - Mock authentication
- `Dev/pytests/fixtures/mock_http_client.py` - Mock HTTP client
- `Dev/pytests/fixtures/mock_managers.py` - Mock managers
- `Dev/pytests/fixtures/conftest.py` - Shared pytest fixtures

### Step 4: Update Configurations

- Ensure `pytest.ini` points to `Dev/pytests`
- Update `run_tests.py` to use `Dev/pytests`
- Keep `run_tests.ps1` and `run_tests.sh` at root

### Step 5: Archive Legacy Tests

- Move `Dev/tests/` to `Dev/tests_legacy/`
- Create `Dev/tests_legacy/README.md` explaining migration
- Reference new test structure

## 📊 Expected Outcomes

### Current (Before)

```
Root level: No structured tests (pytest.ini but inconsistent)
Dev/tests/: 44+ legacy test files (mixed concerns)
Dev/pytests/: 3 new security tests (isolated)
Coverage: ~40% (incomplete)
```

### Target (After)

```
Root level: pytest.ini, run_tests.* for orchestration
Dev/pytests/: Well-organized by phase (security → managers → core → cli)
Dev/pytests/security/: Phase 1 security tests (97% coverage)
Dev/pytests/managers/: Phase 2 manager tests (90%+ coverage each)
Dev/pytests/core/: Phase 3 core infrastructure tests (85%+)
Dev/pytests/cli/: Phase 4 CLI tests (80%+)
Dev/pytests/integration/: Cross-module tests
Dev/pytests/fixtures/: Shared mocks & conftest
Dev/tests_legacy/: Archived for reference (read-only)
Coverage: 85%+ overall
```

## 🚀 Quick Commands

### Run All Tests

```bash
pytest Dev/pytests -v
```

### Run by Phase

```bash
pytest Dev/pytests/security -v          # Phase 1
pytest Dev/pytests/managers -v          # Phase 2
pytest Dev/pytests/core -v              # Phase 3
pytest Dev/pytests/cli -v               # Phase 4
```

### Run with Coverage

```bash
pytest Dev/pytests --cov=core --cov=cli --cov-report=html
```

### Run Specific Test

```bash
pytest Dev/pytests/security/test_csrf_manager.py::TestCSRFManagerValidation -v
```

### Run Marked Tests Only

```bash
pytest Dev/pytests -m security -v       # Only security tests
pytest Dev/pytests -m integration -v    # Only integration tests
```

---

**Date:** 16 octobre 2025
**Strategy:** Consolidate tests in Dev/pytests/ organized by phase
**Status:** Planning
**Next Step:** Create directory structure + move existing tests
