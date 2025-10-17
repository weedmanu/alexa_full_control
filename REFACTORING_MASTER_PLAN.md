# Alexa Full Control - Refactoring Master Plan (3 Phases)

## 🎯 MISSION

Migrate from legacy HTTP architecture to centralized `AlexaAPIService` with optional dependency injection, improving testability, maintainability, and resilience.

---

## 📅 PHASES OVERVIEW

| Phase       | Duration  | Status      | Focus                       | Deliverables                            |
| ----------- | --------- | ----------- | --------------------------- | --------------------------------------- |
| **Phase 1** | 1 week    | ✅ COMPLETE | Foundation: AlexaAPIService | Service + Device Manager POC + 13 tests |
| **Phase 2** | 1-2 weeks | 🔵 PLANNED  | Manager Migration           | 6 managers refactored + 50+ tests       |
| **Phase 3** | 1-2 weeks | ⏳ FUTURE   | Cleanup & Release           | Legacy removal + v2.0 release           |

---

## 📖 PHASE 1: FOUNDATION (COMPLETE ✅)

**Branch**: `pr/refacto-phase1-di-wiring`  
**Status**: ✅ Ready for merge  
**Completion**: October 17, 2025

### What Was Done

1. ✅ **AlexaAPIService** created (central HTTP abstraction)
   - Dual constructor (legacy + new style)
   - Circuit breaker (simple counter, 2-failure rule)
   - Cache fallback on NetworkError
   - Exception hierarchy (4 types)
2. ✅ **Device Manager** refactored (POC)
   - Now requires mandatory `api_service` parameter
   - Removed fallback to `_api_call`
   - Direct calls via `_api_service.get_devices()`
3. ✅ **Tests Written & Passing**
   - 10 AlexaAPIService TDD tests ✅
   - 3 Device Manager integration tests ✅
   - **Total: 13/13 tests passing**
4. ✅ **Documentation Complete**
   - `design_alexa_api_service.md` - Specification
   - `PHASE1_STATUS.md` - Living status
   - `PHASE1_COMPLETION_REPORT.md` - Comprehensive report
   - `PHASE1_FINAL_STATUS.md` - Executive summary
   - `PR_SUMMARY.md` - PR description

### Key Files

- **New**: `services/alexa_api_service.py` (240 lines)
- **Modified**: `core/device_manager.py` (now mandatory injection)
- **Tests**: `Dev/pytests/services/test_alexa_api_service.py` (10 tests)
- **Tests**: `Dev/pytests/core/test_device_manager_phase1.py` (3 tests)

### Success Metrics

- ✅ 13/13 tests passing
- ✅ 4 clean commits
- ✅ No breaking changes to other modules
- ✅ Circuit breaker implemented
- ✅ Cache fallback working
- ✅ Documentation complete

**Read More**: 📄 `Dev/docs/PHASE1_COMPLETION_REPORT.md`

---

## 🚀 PHASE 2: MANAGER MIGRATION (PLANNED 🔵)

**Expected Start**: After Phase 1 merge  
**Duration**: 1-2 weeks  
**Scope**: Refactor all 6 remaining managers

### Phase 2 Objectives

1. **Manager Refactoring** (Priority: HIGH)

   - [ ] Timers Manager → mandatory `api_service`
   - [ ] Routines Manager → mandatory `api_service`
   - [ ] Music Manager → mandatory `api_service`
   - [ ] Reminders Manager → mandatory `api_service`
   - [ ] DND Manager → mandatory `api_service`
   - [ ] Settings Manager → mandatory `api_service`

2. **Testing** (Priority: HIGH)

   - [ ] 5-8 unit tests per manager (30-48 tests total)
   - [ ] Integration tests (multi-manager scenarios)
   - [ ] Target: 50+ new tests

3. **Cleanup** (Priority: MEDIUM)

   - [ ] Remove `_api_call` pattern (deprecate in BaseManager)
   - [ ] Lint/type fixes (ruff, flake8, mypy strict)
   - [ ] Coverage improvements (+10 points)

4. **CI/CD** (Priority: MEDIUM)

   - [ ] GitHub Actions workflow (pytest, ruff, mypy, coverage)
   - [ ] Pre-commit hooks (auto-format, lint, type check)

5. **Documentation** (Priority: MEDIUM)
   - [ ] Update MIGRATION.md (examples for all 6 managers)
   - [ ] Update ARCHITECTURE.md (DI pattern documentation)
   - [ ] Create CHANGELOG.md (Phase 1 & 2 changes)

### Phase 2 Task Breakdown

- **Manager Refactoring**: 20-24 hours
- **Unit Tests**: 12-16 hours
- **Integration Tests**: 4-6 hours
- **Cleanup & Fixes**: 10-14 hours
- **CI/CD Setup**: 4-6 hours
- **Documentation**: 7-9 hours
- **Review & QA**: 4-8 hours
- **TOTAL**: ~60-89 hours (1-2 weeks at 40 hrs/week)

### Phase 2 Success Criteria

- [x] All 6 managers use mandatory `AlexaAPIService`
- [x] No fallback to `_api_call` in any manager
- [x] 50+ new tests (all passing)
- [x] Lint/type checks pass (strict mode)
- [x] Coverage increased by 10+ points
- [x] GitHub Actions running
- [x] Documentation updated
- [x] No breaking changes

**Read More**:

- 📄 `Dev/docs/PHASE2_PLAN.md` - Detailed planning
- 📄 `Dev/docs/PHASE2_BACKLOG.md` - GitHub issues/tasks

---

## 🎓 PHASE 3: CLEANUP & RELEASE (FUTURE ⏳)

**Expected Start**: After Phase 2 merge  
**Duration**: 1-2 weeks  
**Scope**: Final cleanup and v2.0 release

### Phase 3 Objectives

1. **Legacy Code Removal**

   - [ ] Remove `BaseManager._api_call()` entirely
   - [ ] Verify zero legacy references in codebase
   - [ ] Deprecation notices resolved

2. **Performance & Optimization**

   - [ ] Profiling (identify hot paths)
   - [ ] Circuit breaker optimization
   - [ ] Cache strategy refinement

3. **Monitoring & Observability**

   - [ ] Add structured logging
   - [ ] Metrics collection
   - [ ] Error tracking integration

4. **API Documentation**

   - [ ] API reference (all managers)
   - [ ] Usage examples
   - [ ] Troubleshooting guide

5. **Release Preparation**
   - [ ] Version bump to v2.0
   - [ ] Release notes
   - [ ] Migration guide for users
   - [ ] Tag release commit

### Phase 3 Success Criteria

- [x] Zero legacy `_api_call` references
- [x] All tests passing (100+)
- [x] Performance benchmarks established
- [x] Full documentation coverage
- [x] v2.0 released

**Read More**: 📄 `Dev/docs/PHASE3_PLAN.md` (TBD - create during Phase 2)

---

## 📊 PROGRESS DASHBOARD

```
PHASE 1 (Foundation)
████████████████████ 100% ✅ COMPLETE
- AlexaAPIService: ✅
- Device Manager POC: ✅
- Tests (13/13): ✅
- Docs: ✅

PHASE 2 (Manager Migration)
░░░░░░░░░░░░░░░░░░░░   0% 🔵 PLANNED
- Manager Refactoring: 🔵
- Testing: 🔵
- Cleanup: 🔵
- CI/CD: 🔵
- Documentation: 🔵

PHASE 3 (Release)
░░░░░░░░░░░░░░░░░░░░   0% ⏳ FUTURE
- Legacy Removal: ⏳
- Performance: ⏳
- Monitoring: ⏳
- API Docs: ⏳
- v2.0 Release: ⏳
```

---

## 🔗 KEY DOCUMENTS BY PHASE

### Phase 1 Documentation (✅ Complete)

- `PHASE1_FINAL_STATUS.md` - Executive summary
- `PHASE1_COMPLETION_REPORT.md` - Comprehensive report
- `design_alexa_api_service.md` - Specification
- `PR_SUMMARY.md` - PR description for review
- Commits: 4 clean semantic messages

### Phase 2 Documentation (🔵 Planned)

- `PHASE2_PLAN.md` - Detailed planning & timeline
- `PHASE2_BACKLOG.md` - GitHub issues & tasks
- `PHASE2_COMPLETION_REPORT.md` - Will create at end

### Phase 3 Documentation (⏳ Future)

- `PHASE3_PLAN.md` - Planning (create during Phase 2)
- `PHASE3_COMPLETION_REPORT.md` - At end of Phase 3

### Cross-Phase Documentation

- `MIGRATION.md` - How to migrate (update in Phase 2)
- `ARCHITECTURE.md` - System design (update in Phase 2)
- `CHANGELOG.md` - All changes (create in Phase 2)

---

## 💾 GIT WORKFLOW

### Branch Structure

```
main (stable)
└── pr/refacto-phase1-di-wiring (Phase 1 - ready for merge)
    └── pr/refacto-phase2-manager-migration (Phase 2 - future)
        └── pr/refacto-phase3-cleanup (Phase 3 - future)
```

### Commit Convention

All commits follow semantic versioning:

```
refactor(component): description
feat(component): add new feature
test(component): add tests
docs: update documentation
chore: maintenance tasks
fix: bug fixes
```

### Phase 1 Commits (4 total)

1. ✅ `refactor(core): remove _api_call fallback, make AlexaAPIService mandatory`
2. ✅ `test(phase1): add device manager tests without fallback, all 13 tests green`
3. ✅ `docs(phase1): add PR summary and completion report`
4. ✅ `docs: add final Phase 1 status report`

### Phase 2 Commits (TBD)

- Will add commits for each manager (6 commits minimum)
- Cleanup commits (lint, type, coverage)
- Docs commits (MIGRATION, ARCHITECTURE, CHANGELOG)

---

## ✨ MIGRATION PATTERN

### Before Phase 1 (Legacy)

```python
# Old way - direct auth calls
device_mgr = DeviceManager(auth, state_machine)
devices = device_mgr.get_devices()  # Uses internal _api_call
```

### Phase 1 (POC - Device Manager)

```python
# New way - with AlexaAPIService injection
api_service = AlexaAPIService(session=requests.Session(), cache_service=cache)
device_mgr = DeviceManager(auth, state_machine, api_service=api_service)
devices = device_mgr.get_devices()  # Uses api_service directly
```

### Phase 2 (Full Migration)

```python
# All 6 managers refactored to require api_service
api_service = AlexaAPIService(session=requests.Session(), cache_service=cache)

timers_mgr = TimersManager(auth, state_machine, api_service=api_service)
routines_mgr = RoutinesManager(auth, state_machine, api_service=api_service)
music_mgr = MusicManager(auth, state_machine, api_service=api_service)
# ... etc for all 6 managers

# All use centralized AlexaAPIService with circuit breaker + cache fallback
```

### Phase 3 (Cleanup)

```python
# BaseManager._api_call() removed entirely
# All code uses AlexaAPIService pattern
# Legacy patterns gone
```

---

## 📈 TEST COVERAGE PROGRESSION

```
Phase 1:
- AlexaAPIService: 10/10 tests ✅
- Device Manager: 3/3 tests ✅
- Total: 13/13 passing ✅
- Coverage: Base established

Phase 2:
- Add 50+ new tests (5-8 per manager)
- Total: 63+ tests passing
- Coverage: +10 points

Phase 3:
- Performance/monitoring tests
- Total: 70+ tests
- Coverage: Stable at high level
```

---

## 🎯 SUCCESS DEFINITION

**End of Phase 1**: ✅ Done

- AlexaAPIService working
- Device Manager POC done
- 13 tests passing
- Ready for Phase 2

**End of Phase 2**: 🔵 Target

- All 6 managers migrated
- 50+ new tests passing
- Lint/type clean
- GitHub Actions running

**End of Phase 3**: ⏳ Target

- v2.0 released
- Zero legacy code
- Full documentation
- Production-ready

---

## 🚀 NEXT STEPS

### Immediate (Today)

- [x] Push Phase 1 to `pr/refacto-phase1-di-wiring`
- [x] Create Phase 2 plan and backlog
- [x] Create this master document

### Short Term (This Week)

- [ ] Get Phase 1 code review
- [ ] Merge Phase 1 to `main`
- [ ] Start Phase 2 branch

### Medium Term (Next 2 Weeks)

- [ ] Execute Phase 2 (manager migration)
- [ ] Write Phase 2 tests
- [ ] Complete Phase 2 documentation

### Long Term (Week 3-4)

- [ ] Execute Phase 3 (cleanup)
- [ ] Release v2.0
- [ ] Monitor production

---

## 📞 CONTACTS & OWNERSHIP

- **Project Lead**: M@nu
- **Architecture**: Phase 1-3 designed end-to-end
- **Review**: Community & maintainers
- **Release**: Maintainers

---

## 🔖 REFERENCES

**Phase 1 Artifacts**:

- Branch: `pr/refacto-phase1-di-wiring`
- Status: Ready for merge
- Tests: 13/13 passing
- Docs: 4 files

**Phase 2 Artifacts**:

- Branch: (TBD) `pr/refacto-phase2-manager-migration`
- Status: Planned
- Docs: `PHASE2_PLAN.md`, `PHASE2_BACKLOG.md`

**Phase 3 Artifacts**:

- Branch: (TBD) `pr/refacto-phase3-cleanup`
- Status: Future planning

---

**Last Updated**: October 17, 2025  
**Status**: 🟢 Phase 1 Complete, Phase 2 Planned, Phase 3 Future  
**Version**: Master Plan v1.0

---

## 📝 FOOTNOTES

This document serves as the master reference for the 3-phase refactoring initiative. Each phase has detailed planning documents; refer to them for specific tasks and timelines.

**For questions or updates**: See respective phase documents.
