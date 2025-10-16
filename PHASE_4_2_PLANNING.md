# PHASE 4.2 PLANNING - CLI Commands Refactoring

**Status:** Planning phase  
**Date:** 16 octobre 2025  
**Objective:** Refactor 15+ CLI commands to use ManagerCommand template  
**Expected Time:** 2-3 hours  
**Target:** 100% backward compatible, all 150 tests passing

---

## 📋 Commands to Refactor (Priority Order)

### **BATCH 1: Music Commands (High Priority)**

- [ ] `cli/commands/music/playback.py` - PlaybackCommands class

  - Methods: pause(), stop(), control(), shuffle(), repeat()
  - Manager: PlaybackManager
  - Priority: HIGH (complex, multiple methods)

- [ ] `cli/commands/music/library.py` - LibraryCommands

  - Manager: LibraryManager
  - Priority: MEDIUM

- [ ] `cli/commands/music/status.py` - StatusCommands

  - Manager: PlaybackManager
  - Priority: MEDIUM

- [ ] `cli/commands/music/tunein.py` - TuneInCommands
  - Manager: TuneInManager
  - Priority: MEDIUM

### **BATCH 2: Device Commands (Medium Priority)**

- [ ] `cli/commands/device.py` - DeviceCommand
  - Methods: list(), info()
  - Manager: DeviceManager
  - Priority: MEDIUM (example commands already exist)

### **BATCH 3: Routine/Alarm/Lists Commands (Medium Priority)**

- [ ] `cli/commands/routine.py` - RoutineCommand

  - Methods: list(), execute(), create(), delete()
  - Manager: RoutineManager (just implemented!)
  - Priority: MEDIUM-HIGH (newly implemented)

- [ ] `cli/commands/alarm.py` - AlarmCommand

  - Methods: add(), list(), delete()
  - Manager: AlarmManager
  - Priority: MEDIUM

- [ ] `cli/commands/lists.py` - ListsCommand
  - Methods: create(), add(), list()
  - Manager: ListsManager
  - Priority: MEDIUM

### **BATCH 4: Other Commands (Lower Priority)**

- [ ] `cli/commands/announcement.py` - AnnouncementCommand

  - Manager: DeviceManager / Services
  - Priority: LOW

- [ ] `cli/commands/activity.py` - ActivityCommand

  - Manager: ActivityManager
  - Priority: LOW

- [ ] `cli/commands/reminder.py` - ReminderCommand

  - Manager: ReminderManager
  - Priority: LOW

- [ ] `cli/commands/dnd.py` - DndCommand

  - Manager: DndManager
  - Priority: LOW

- [ ] `cli/commands/smarthome.py` - SmarthomeCommand

  - Manager: SmartHomeManager
  - Priority: LOW

- [ ] `cli/commands/calendar.py` - CalendarCommand

  - Manager: CalendarManager
  - Priority: LOW

- [ ] `cli/commands/multiroom.py` - MultiroomCommand

  - Manager: N/A
  - Priority: LOW

- [ ] `cli/commands/timers/` - TimerCommands
  - Manager: TimerManager
  - Priority: LOW

### **BATCH 5: Special Commands (Infrastructure)**

- [ ] `cli/commands/auth.py` - AuthCommand

  - Special: Auth-related, may need custom handling
  - Priority: LOW

- [ ] `cli/commands/cache.py` - CacheCommand
  - Special: Cache management
  - Priority: LOW

---

## 🎯 Refactoring Pattern

### Current Pattern (Old)

```python
class DeviceCommand(BaseCommand):
    """Command class."""

    def setup_parser(self, parser):
        """Setup argparse."""
        # Manual parser setup

    def execute(self, args):
        """Execute command."""
        # Manual execution logic
        device_name = args.device
        # ... manual logic ...
```

### Target Pattern (New - Using ManagerCommand)

```python
class DeviceListCommand(ManagerCommand):
    """List devices command."""

    def get_manager(self):
        """Get DeviceManager from DI container."""
        return self.di_container.get(DeviceManager)

    def validate(self):
        """Validate prerequisites."""
        return True

    def execute(self):
        """Execute with validated manager."""
        devices = self.manager.get_devices()
        return devices

    def help(self):
        """Return help text."""
        return "List all connected devices"
```

---

## 📊 Implementation Strategy

### Phase 4.2a: Create Adapter Layer (5-10 min)

- Create `cli/commands/adapter.py` with adapter pattern
- Allow old BaseCommand classes to work with new DI system
- Ensure backward compatibility during transition

### Phase 4.2b: Refactor Music Commands (30-45 min)

1. **Music Playback** (Most complex)

   - Create individual command classes for each action
   - PlaybackPlayCommand, PlaybackPauseCommand, etc.
   - Integrate with PlaybackManager via DI

2. **Music Library/Status/TuneIn** (3 commands)
   - Similar pattern
   - Parallel refactoring

### Phase 4.2c: Refactor Device/Routine/Alarm (30-45 min)

- Device commands (2 methods)
- Routine commands (4+ methods) - Use new RoutineManager!
- Alarm commands (3 methods)
- Lists commands (3 methods)

### Phase 4.2d: Refactor Remaining Commands (15-30 min)

- Activity, Reminder, DND, SmartHome, Calendar
- Multiroom, Timers, Auth, Cache
- Most are simple wrappers

### Phase 4.2e: Testing & Validation (20-30 min)

- Run all 150 existing tests
- Verify backward compatibility
- Fix any regressions
- Commit and push

---

## 🔄 Integration Points

### DI Container Integration

```python
# In cli/command_parser.py or main entry point
di_container = DIContainer.instance()

# For each command
command = DeviceListCommand(di_container)
result = command.execute()
```

### Manager Access Pattern

```python
class ManagerCommand(BaseCommand):
    def __init__(self, di_container):
        self.di_container = di_container
        self.manager = None

    def get_manager_type(self):
        """Override in subclass."""
        raise NotImplementedError

    def execute(self, args):
        """Get manager from DI, then execute."""
        manager_type = self.get_manager_type()
        self.manager = self.di_container.get(manager_type)
        return self.run(args)
```

---

## ✅ Validation Checklist

- [ ] All 150 CLI tests passing
- [ ] All 43 RoutineManager tests passing
- [ ] Backward compatibility maintained (old command syntax still works)
- [ ] New ManagerCommand pattern used for all commands
- [ ] DIContainer properly integrated
- [ ] All error cases handled
- [ ] No regressions in existing functionality
- [ ] Code follows project style (mypy strict, Black formatted)
- [ ] Docstrings updated for all refactored commands
- [ ] Git commits organized by command batch

---

## 📝 Commit Strategy

### Commits (Suggested Order)

1. `feat(Phase 4.2): add command adapter layer for DI integration`
2. `refactor(Phase 4.2): music commands to use ManagerCommand template`
3. `refactor(Phase 4.2): device/routine/alarm commands to ManagerCommand`
4. `refactor(Phase 4.2): remaining commands to ManagerCommand`
5. `test(Phase 4.2): verify all 150 tests passing, zero regressions`

---

## 🚀 Success Criteria

| Criteria                    | Target       | Current       |
| --------------------------- | ------------ | ------------- |
| **Tests Passing**           | 150/150      | ? (to verify) |
| **Code Coverage**           | 90%+         | ?             |
| **Regressions**             | 0            | ?             |
| **Backward Compat**         | 100%         | ?             |
| **ManagerCommand Usage**    | 15+ commands | ?             |
| **DIContainer Integration** | All commands | ?             |
| **Estimated Time**          | 2-3 hours    | In progress   |

---

## 🎓 Learning Outcomes

This phase demonstrates:

- Adapter patterns in Python
- Gradual refactoring in live codebases
- Dependency injection in CLI applications
- Maintaining backward compatibility during refactoring
- Large-scale refactoring best practices

---

## 📞 Implementation Notes

- **Start with:** Music/Playback (most complex, establishes pattern)
- **Key Pattern:** Each command method → separate ManagerCommand subclass
- **Testing:** Run pytest after each batch to catch regressions early
- **DI Integration:** Use DIContainer.instance() for singleton access
- **Backward Compat:** Keep old BaseCommand subclasses working during transition

---

**Next:** Create adapter layer and start BATCH 1 refactoring
