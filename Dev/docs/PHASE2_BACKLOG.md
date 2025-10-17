# Phase 2 Backlog: Issues & Epics for GitHub

## Epic: Complete Manager Migration to AlexaAPIService

**Description**: Refactor all remaining managers to use the centralized `AlexaAPIService` (mandatory injection, no fallback).

**Phase 1 Completed**:

- ✅ AlexaAPIService implemented
- ✅ Device Manager refactored (POC)
- ✅ 10/10 AlexaAPIService tests passing
- ✅ 3/3 Device Manager tests passing

**Phase 2 Scope** (this epic):

- [ ] Timers Manager migration + tests
- [ ] Routines Manager migration + tests
- [ ] Music Manager migration + tests
- [ ] Reminders Manager migration + tests
- [ ] DND Manager migration + tests
- [ ] Settings Manager migration + tests
- [ ] Remove \_api_call pattern
- [ ] Lint/type fixes (ruff, mypy)
- [ ] Coverage improvements
- [ ] GitHub Actions CI setup

---

## Issues

### Issue #1: Refactor TimersManager to use AlexaAPIService

**Type**: Feature  
**Priority**: HIGH  
**Estimated**: 6-8 hours (3-4 dev + 3-4 testing)  
**Acceptance Criteria**:

- [ ] TimersManager constructor requires `api_service` parameter
- [ ] All `self._api_call()` calls replaced with `self._api_service.*()` calls
- [ ] No fallback to `_api_call` pattern
- [ ] 5-8 unit tests written and passing
- [ ] All existing tests still pass (regression)

**Tasks**:

```
1. [ ] Update TimersManager.__init__() signature
2. [ ] Replace _api_call in create_timer()
3. [ ] Replace _api_call in delete_timer()
4. [ ] Replace _api_call in update_timer()
5. [ ] Replace _api_call in get_timers()
6. [ ] Write unit tests (5-8 tests)
7. [ ] Run regression tests
8. [ ] Code review + merge
```

**Label**: `phase-2`, `manager-migration`, `timers`

---

### Issue #2: Refactor RoutinesManager to use AlexaAPIService

**Type**: Feature  
**Priority**: HIGH  
**Estimated**: 6-8 hours  
**Acceptance Criteria**: Same as Issue #1

**Label**: `phase-2`, `manager-migration`, `routines`

---

### Issue #3: Refactor MusicManager to use AlexaAPIService

**Type**: Feature  
**Priority**: HIGH  
**Estimated**: 8-10 hours (more complex)  
**Acceptance Criteria**: Same as Issue #1

**Label**: `phase-2`, `manager-migration`, `music`

---

### Issue #4: Refactor RemindersManager to use AlexaAPIService

**Type**: Feature  
**Priority**: HIGH  
**Estimated**: 6-8 hours  
**Acceptance Criteria**: Same as Issue #1

**Label**: `phase-2`, `manager-migration`, `reminders`

---

### Issue #5: Refactor DNDManager to use AlexaAPIService

**Type**: Feature  
**Priority**: HIGH  
**Estimated**: 4-6 hours  
**Acceptance Criteria**: Same as Issue #1

**Label**: `phase-2`, `manager-migration`, `dnd`

---

### Issue #6: Refactor SettingsManager to use AlexaAPIService

**Type**: Feature  
**Priority**: HIGH  
**Estimated**: 6-8 hours  
**Acceptance Criteria**: Same as Issue #1

**Label**: `phase-2`, `manager-migration`, `settings`

---

### Issue #7: Remove \_api_call pattern from BaseManager

**Type**: Refactor  
**Priority**: HIGH  
**Estimated**: 2-3 hours  
**Description**:

- Mark BaseManager.\_api_call() as deprecated
- Remove all references in core/ modules
- Verify no usage in services/
- Add deprecation warning if still called

**Acceptance Criteria**:

- [ ] No references to `_api_call` in core/ (except BaseManager deprecated method)
- [ ] Deprecation warning implemented
- [ ] All tests passing
- [ ] Documentation updated (MIGRATION.md)

**Label**: `phase-2`, `cleanup`, `refactor`

---

### Issue #8: Fix Lint & Type Issues (ruff, flake8, mypy)

**Type**: Quality  
**Priority**: MEDIUM  
**Estimated**: 4-6 hours  
**Commands**:

```bash
python -m ruff check . --select=F,E,W,B --fix
python -m flake8 core/ services/ --max-line-length=120
python -m mypy core/ services/ --strict
```

**Acceptance Criteria**:

- [ ] ruff: 0 errors (F, E, W, B)
- [ ] flake8: 0 errors
- [ ] mypy: 0 errors in strict mode
- [ ] All tests still passing

**Label**: `phase-2`, `quality`, `lint`

---

### Issue #9: Improve Test Coverage (+10 points)

**Type**: Quality  
**Priority**: MEDIUM  
**Estimated**: 6-8 hours  
**Target**: Coverage in core/ and services/ increased by 10 points

**Acceptance Criteria**:

- [ ] Coverage report generated (Dev/docs/htmlcov/)
- [ ] Coverage increased by at least 10 points
- [ ] Critical paths covered (auth, error handling)
- [ ] HTML report accessible

**Label**: `phase-2`, `quality`, `testing`

---

### Issue #10: Set up GitHub Actions Workflow

**Type**: DevOps  
**Priority**: MEDIUM  
**Estimated**: 3-4 hours  
**Description**: Create `.github/workflows/phase2-ci.yml` with:

- pytest (all tests)
- ruff (lint)
- flake8 (style)
- mypy (type check)
- coverage (report + artifact)

**Acceptance Criteria**:

- [ ] Workflow file created and committed
- [ ] Workflow runs on push to main + PRs
- [ ] All jobs passing on main branch
- [ ] Coverage report artifact available

**Label**: `phase-2`, `devops`, `ci`

---

### Issue #11: Update Migration Guide

**Type**: Documentation  
**Priority**: MEDIUM  
**Estimated**: 2-3 hours  
**File**: `Dev/docs/MIGRATION.md`

**Updates**:

- [ ] Add examples for all 6 refactored managers
- [ ] Show before/after patterns
- [ ] Quick-start for new code
- [ ] Troubleshooting section

**Label**: `phase-2`, `documentation`

---

### Issue #12: Update Architecture Documentation

**Type**: Documentation  
**Priority**: MEDIUM  
**Estimated**: 2-3 hours  
**File**: `Dev/docs/ARCHITECTURE.md`

**Updates**:

- [ ] Document new DI pattern
- [ ] Update manager hierarchy diagram
- [ ] Explain AlexaAPIService role
- [ ] Add sequence diagrams

**Label**: `phase-2`, `documentation`

---

### Issue #13: Create CHANGELOG

**Type**: Documentation  
**Priority**: LOW  
**Estimated**: 1-2 hours  
**File**: `CHANGELOG.md` (new)

**Format**: Keep-a-Changelog (https://keepachangelog.com/)

**Sections**:

- Phase 1: Core changes
- Phase 2: Manager migration + cleanup
- Dependencies updated
- Breaking changes noted

**Label**: `phase-2`, `documentation`

---

## Epic Summary

| Item                             | Status  | Owner | ETA    |
| -------------------------------- | ------- | ----- | ------ |
| **Issue #1: Timers**             | 🔵 TODO | ?     | Week 1 |
| **Issue #2: Routines**           | 🔵 TODO | ?     | Week 1 |
| **Issue #3: Music**              | 🔵 TODO | ?     | Week 1 |
| **Issue #4: Reminders**          | 🔵 TODO | ?     | Week 2 |
| **Issue #5: DND**                | 🔵 TODO | ?     | Week 2 |
| **Issue #6: Settings**           | 🔵 TODO | ?     | Week 2 |
| **Issue #7: Remove \_api_call**  | 🔵 TODO | ?     | Week 2 |
| **Issue #8: Lint/Type**          | 🔵 TODO | ?     | Week 2 |
| **Issue #9: Coverage**           | 🔵 TODO | ?     | Week 2 |
| **Issue #10: GitHub Actions**    | 🔵 TODO | ?     | Week 2 |
| **Issue #11: Migration Guide**   | 🔵 TODO | ?     | Week 2 |
| **Issue #12: Architecture Docs** | 🔵 TODO | ?     | Week 2 |
| **Issue #13: CHANGELOG**         | 🔵 TODO | ?     | Week 2 |

**Phase 2 Progress**: 0/13 items complete

---

## Dependency Graph

```
Phase 1 (✅ COMPLETE)
    ↓
Issue #1-6 (Managers) [parallel]
    ↓
Issue #7 (Remove _api_call)
    ↓
Issue #8-9 (Quality)
    ↓
Issue #10 (CI/CD)
    ↓
Issue #11-13 (Docs)
    ↓
Phase 3 (Ready for Planning)
```

---

## Acceptance Criteria for Phase 2 Complete

- [x] All 6 managers refactored (Issues #1-6)
- [x] \_api_call pattern removed (Issue #7)
- [x] All tests passing (50+ new tests)
- [x] Lint/type checks passing (Issue #8)
- [x] Coverage increased by 10+ points (Issue #9)
- [x] GitHub Actions workflow running (Issue #10)
- [x] Documentation updated (Issues #11-13)
- [x] No breaking changes to public API
- [x] All commits have semantic messages
- [x] Code review completed

---

## Notes

- **Parallel Work**: Issues #1-6 can be worked on in parallel
- **Dependencies**: Issue #7 depends on #1-6 completion
- **Testing**: Each issue includes comprehensive test coverage
- **Review**: All PRs require code review before merge
- **Estimation**: Times are estimates; adjust based on actual progress

---

**Backlog Created**: October 17, 2025  
**Phase 2 Start**: TBD  
**Phase 2 Duration**: 1-2 weeks  
**Assigned To**: Team  
**Priority**: HIGH
