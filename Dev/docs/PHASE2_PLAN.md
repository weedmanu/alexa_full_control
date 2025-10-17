# Phase 2 Planning: Complete Manager Migration & Cleanup

## Overview

Phase 2 focuses on completing the migration of all remaining managers to use `AlexaAPIService` (mandatory), removing all fallback patterns, and preparing for Phase 3 (cleanup).

**Timeline**: Estimated 1-2 weeks  
**Scope**: Timers, Routines, Music, Reminders, DND, Settings managers  
**Success Criteria**: All managers use AlexaAPIService, all tests green, toolchain passes

---

## Phase 2 Deliverables

### 1. Manager Refactoring (Priority: HIGH)

#### 1.1 Timers Manager

**File**: `core/timers/timer_manager.py`  
**Status**: Not started  
**Scope**:

- Make `api_service` mandatory (like Device Manager)
- Replace all `self._api_call()` calls with `self._api_service.*()`
- Update constructor to require `api_service` parameter
- Write 5-8 TDD tests covering main operations (create, delete, update)

**Endpoints to replace**:

```python
# OLD:
self._api_call("get", "/api/timers", timeout=10)
self._api_call("post", "/api/timers", json=payload, timeout=10)
self._api_call("delete", f"/api/timers/{timer_id}", timeout=10)

# NEW:
self._api_service.get("/api/timers")
self._api_service.post("/api/timers", json=payload)
self._api_service.post(f"/api/timers/{timer_id}")  # or appropriate method
```

**Test File**: `Dev/pytests/core/test_timers_manager_phase2.py` (new)  
**Estimated Time**: 3-4 hours

#### 1.2 Routines Manager

**File**: `core/routines/routine_manager.py`  
**Status**: Not started  
**Scope**: Same as Timers Manager

**Estimated Time**: 3-4 hours

#### 1.3 Music Manager

**File**: `core/music/music_manager.py`  
**Status**: Not started  
**Scope**: Same as Timers Manager (may have more endpoints)

**Estimated Time**: 4-5 hours

#### 1.4 Reminders Manager

**File**: `core/reminders/reminder_manager.py`  
**Status**: Not started  
**Scope**: Same pattern

**Estimated Time**: 3-4 hours

#### 1.5 DND Manager

**File**: `core/dnd_manager.py`  
**Status**: Not started  
**Scope**: Same pattern

**Estimated Time**: 2-3 hours

#### 1.6 Settings Manager

**File**: `core/settings/device_settings_manager.py`  
**Status**: Not started  
**Scope**: Same pattern (may need header handling)

**Estimated Time**: 3-4 hours

**Total Manager Refactoring**: ~20-24 hours

---

### 2. Testing (Priority: HIGH)

#### 2.1 Unit Tests for Each Manager

- Write 5-8 tests per manager (same pattern as Device Manager POC)
- Verify mandatory `api_service` requirement
- Test cache operations
- Test error handling

**Estimated Time**: 12-16 hours

#### 2.2 Integration Tests

**File**: `Dev/pytests/integration/test_phase2_managers.py` (new)

- Verify multiple managers work with same service instance
- Test circuit breaker protection across managers
- Test cache coordination

**Estimated Time**: 4-6 hours

**Total Testing**: ~18-24 hours

---

### 3. Cleanup & Fixes (Priority: MEDIUM)

#### 3.1 Remove Legacy `_api_call` Pattern

- Remove `_api_call` method from `BaseManager` (or mark deprecated)
- Verify no remaining references in core/ and managers/
- Update `create_http_client_from_auth` if no longer needed

**Estimated Time**: 2-3 hours

#### 3.2 Lint & Type Fixes (ruff, flake8, mypy)

**Commands**:

```bash
python -m ruff check . --select=F,E,W,B --fix
python -m flake8 core/ services/ --max-line-length=120
python -m mypy core/ services/ --strict
```

**Estimated Time**: 4-6 hours

#### 3.3 Coverage Improvements

- Target: +10 points in `core/` and `services/`
- Focus on high-ROI tests (auth flow, error paths)
- Generate HTML report: `Dev/docs/htmlcov/`

**Estimated Time**: 6-8 hours

---

### 4. CI/CD Setup (Priority: MEDIUM)

#### 4.1 GitHub Actions Workflow

**File**: `.github/workflows/phase2-ci.yml` (new)  
**Triggers**: On push to `main` and PR branches  
**Jobs**:

- pytest (all tests)
- ruff (lint)
- flake8 (style)
- mypy (type check)
- coverage (report + upload artifact)

**Estimated Time**: 3-4 hours

#### 4.2 Pre-commit Hooks

**File**: `.pre-commit-config.yaml` (new/update)

- Auto-format (black, isort)
- Lint (ruff, flake8)
- Type check (mypy)

**Estimated Time**: 1-2 hours

---

### 5. Documentation (Priority: MEDIUM)

#### 5.1 Update Migration Guide

**File**: `Dev/docs/MIGRATION.md` (update)

- Add examples for all 6 managers
- Show before/after patterns
- Provide quick-start for new code

**Estimated Time**: 2-3 hours

#### 5.2 Architecture Update

**File**: `Dev/docs/ARCHITECTURE.md` (update)

- Document new DI pattern
- Show manager hierarchy
- Update component diagram

**Estimated Time**: 2-3 hours

#### 5.3 CHANGELOG

**File**: `CHANGELOG.md` (new)

- Document all Phase 1 & 2 changes
- Follow keep-a-changelog format

**Estimated Time**: 1-2 hours

---

## Phase 2 Task Breakdown

| Task                           | Hours           | Priority | Owner |
| ------------------------------ | --------------- | -------- | ----- |
| **Refactor Timers Manager**    | 3-4             | HIGH     | TBD   |
| **Refactor Routines Manager**  | 3-4             | HIGH     | TBD   |
| **Refactor Music Manager**     | 4-5             | HIGH     | TBD   |
| **Refactor Reminders Manager** | 3-4             | HIGH     | TBD   |
| **Refactor DND Manager**       | 2-3             | HIGH     | TBD   |
| **Refactor Settings Manager**  | 3-4             | HIGH     | TBD   |
| **Write Unit Tests (all)**     | 12-16           | HIGH     | TBD   |
| **Integration Tests**          | 4-6             | HIGH     | TBD   |
| **Remove `_api_call` Pattern** | 2-3             | MEDIUM   | TBD   |
| **Lint/Type Fixes**            | 4-6             | MEDIUM   | TBD   |
| **Coverage Improvements**      | 6-8             | MEDIUM   | TBD   |
| **GitHub Actions**             | 3-4             | MEDIUM   | TBD   |
| **Pre-commit Setup**           | 1-2             | MEDIUM   | TBD   |
| **Migration Guide Update**     | 2-3             | MEDIUM   | TBD   |
| **Architecture Docs**          | 2-3             | MEDIUM   | TBD   |
| **CHANGELOG**                  | 1-2             | MEDIUM   | TBD   |
| **Code Review & QA**           | 4-8             | HIGH     | TBD   |
| **Merge & Release**            | 1-2             | HIGH     | TBD   |
| **TOTAL**                      | **60-89 hours** |          |       |

---

## Phase 2 Success Criteria

- [x] All 6 managers refactored to use mandatory `AlexaAPIService`
- [x] No fallback to `_api_call` in any manager
- [x] 50+ new tests written (5-8 per manager + integration)
- [x] All tests passing (target: 100+)
- [x] Lint/type checks passing (ruff, flake8, mypy strict)
- [x] Coverage report generated (+10 points)
- [x] GitHub Actions workflow running on PR/push
- [x] Documentation updated (migration guide, architecture, CHANGELOG)
- [x] No breaking changes to public API
- [x] Ready for Phase 3

---

## Phase 2 Timeline (Estimated)

```
Week 1:
  Mon-Wed: Manager refactoring (Timers, Routines, Music)
  Thu-Fri: Unit tests + integration tests

Week 2:
  Mon-Tue: Cleanup (_api_call removal, lint/type)
  Wed-Thu: Coverage improvements + CI/CD setup
  Fri: Documentation + final QA
```

---

## Phase 2 Risks & Mitigations

| Risk                                     | Impact | Mitigation                                             |
| ---------------------------------------- | ------ | ------------------------------------------------------ |
| Manager refactoring breaks existing code | HIGH   | Comprehensive test coverage, code review               |
| Lint/type fixes cause regressions        | MEDIUM | Run full test suite after each fix                     |
| CI/CD misconfiguration                   | MEDIUM | Test locally first, incremental commits                |
| Time underestimate                       | MEDIUM | Prioritize managers by complexity, defer nice-to-haves |

---

## Phase 2 Dependencies

- ✅ Phase 1 complete (AlexaAPIService working)
- ✅ TDD test patterns established
- ✅ Device Manager POC done
- ⏳ Manager-specific knowledge (what each manager does)
- ⏳ Test environment setup (pytest, fixtures)

---

## Phase 3 Preview (Post-Phase 2)

After Phase 2 completes:

1. **Code Cleanup**: Remove BaseManager.\_api_call() entirely
2. **Performance**: Profiling and optimization
3. **Monitoring**: Add metrics & alerting
4. **Documentation**: API documentation & examples
5. **Release**: v2.0 with full DI support

---

## Sign-Off

**Phase 2 Plan Created**: October 17, 2025  
**Status**: Ready for approval  
**Next Action**: Assign owners to manager refactoring tasks

---

**Questions?**

Contact: M@nu  
Branch: `pr/refacto-phase1-di-wiring` (Phase 1 base)  
Phase 2 Branch: `pr/refacto-phase2-manager-migration` (TBD)
