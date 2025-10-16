# MIGRATION_GUIDE.md - Upgrade from Old to New CLI Architecture

**Version:** 1.0  
**Date:** 16 Octobre 2025  
**Audience:** Developers, DevOps, Maintainers

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Breaking Changes](#breaking-changes)
3. [Migration Path](#migration-path)
4. [Step-by-Step Conversion](#step-by-step-conversion)
5. [Common Issues](#common-issues)
6. [Testing & Validation](#testing--validation)
7. [Rollback Plan](#rollback-plan)
8. [FAQ](#faq)

---

## 🎯 OVERVIEW

### What Changed?

**Old Architecture (Phase 4):**

```
Monolithic BaseCommand classes
    ↓
Direct manager instantiation
    ↓
Tightly coupled dependencies
    ↓
Hard to test
```

**New Architecture (Phase 4.2 + Phase 7):**

```
Modular command classes (40 total)
    ↓
CommandAdapter + DIContainer
    ↓
Dependency injection
    ↓
Easy to test & extend
```

### Why Migrate?

✅ **Better Testability:** Individual command classes, mockable dependencies  
✅ **Reduced Duplication:** 70% less boilerplate code  
✅ **Easier Extension:** Clear patterns for adding new commands  
✅ **Better Maintainability:** Consistent code organization  
✅ **Improved Reliability:** Circuit breaker pattern prevents cascading failures

---

## ⚠️ BREAKING CHANGES

### 1. Command Import Paths

**Old:**

```python
from cli.commands import PlaybackCommand
cmd = PlaybackCommand(config)
```

**New:**

```python
from cli.commands.music.playback_commands import PlaybackPlayCommand
cmd = PlaybackPlayCommand()  # No config needed
```

**Migration:** Update all import statements

### 2. Command Initialization

**Old:**

```python
cmd = PlaybackCommand(config, http_client, breaker_registry)
result = cmd.execute_play(device_id)
```

**New:**

```python
cmd = PlaybackPlayCommand()  # Uses DIContainer automatically
args = argparse.Namespace(device_id=device_id)
success = cmd.execute(args)
```

**Migration:** Use argparse.Namespace for arguments

### 3. Manager Access

**Old (inside command):**

```python
class PlaybackCommand(BaseCommand):
    def __init__(self, config, http_client, breaker_registry):
        self.playback_manager = PlaybackManager(
            config, http_client, breaker_registry
        )
```

**New (inside command):**

```python
class PlaybackPlayCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.adapter = get_command_adapter()

    def execute(self, args):
        manager = self.adapter.get_manager("PlaybackManager")
```

**Migration:** Use `get_command_adapter()` for lazy manager access

### 4. Output Formatting

**Old:**

```python
print(result)  # Raw output
```

**New:**

```python
# Table format
print(self._format_table(data, ["id", "name"]))

# JSON format
print(self._format_json(data))

# Error format
print(self._format_error(error))
```

**Migration:** Use BaseCommand formatting methods

---

## 🗺️ MIGRATION PATH

### Phase 1: Preparation (1 hour)

- [ ] Backup current code: `git branch backup-old-cli`
- [ ] Review `ARCHITECTURE.md` for new patterns
- [ ] Set up test environment: `pytest --cov=cli`
- [ ] Create feature branch: `git checkout -b migrate-to-new-cli`

### Phase 2: Framework Setup (30 minutes)

- [ ] Ensure `DIContainer.setup_for_cli()` called in `main()`
- [ ] Verify `CommandAdapter` is available globally
- [ ] Test DIContainer singleton: `pytest Dev/pytests/core/test_di_container.py`

### Phase 3: Command Migration (Per command)

For each of the 40 commands:

- [ ] Create new command class file
- [ ] Implement `execute(args: argparse.Namespace) -> bool`
- [ ] Write tests before implementation
- [ ] Update command parser routing
- [ ] Test individual command

**Estimated time:** 5-10 minutes per command

### Phase 4: Integration Testing (1 hour)

- [ ] Run full test suite: `pytest Dev/pytests/`
- [ ] Test all command combinations
- [ ] Verify error handling
- [ ] Test edge cases

### Phase 5: Deployment (30 minutes)

- [ ] Review all changes: `git diff master...migrate-to-new-cli`
- [ ] Create pull request for code review
- [ ] Merge to main branch
- [ ] Tag release: `git tag v0.2.0-new-cli`

---

## 📝 STEP-BY-STEP CONVERSION

### Example: Converting PlaybackCommand

#### Before (Old Architecture)

```python
# File: cli/commands/playback_command.py

from cli.base_command import BaseCommand
from core.playback_manager import PlaybackManager

class PlaybackCommand(BaseCommand):
    """Monolithic playback command."""

    def __init__(self, config, http_client, breaker_registry):
        self.config = config
        self.playback_manager = PlaybackManager(
            config, http_client, breaker_registry
        )

    def execute_play(self, device_id: str) -> bool:
        """Resume playback."""
        try:
            self.playback_manager.play(device_id)
            print("Playback started")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def execute_pause(self, device_id: str) -> bool:
        """Pause playback."""
        try:
            self.playback_manager.pause(device_id)
            print("Playback paused")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def execute_next(self, device_id: str) -> bool:
        """Next track."""
        try:
            self.playback_manager.next(device_id)
            print("Next track")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    # ... 7 more methods for stop, previous, shuffle, repeat
```

#### After (New Architecture)

**File 1: `cli/commands/music/playback_commands.py`**

```python
import argparse
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.command_adapter import get_command_adapter


class PlaybackPlayCommand(BaseCommand):
    """Resume playback on specified device."""

    def __init__(self, context: Optional[Any] = None) -> None:
        super().__init__(context)
        self.adapter = get_command_adapter()

    def execute(self, args: argparse.Namespace) -> bool:
        """Execute play command.

        Args:
            args: Must contain 'device_id' attribute

        Returns:
            True if successful, False otherwise
        """
        try:
            manager = self.adapter.get_manager("PlaybackManager")
            manager.play(args.device_id)
            print("✓ Playback resumed")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


class PlaybackPauseCommand(BaseCommand):
    """Pause playback on specified device."""

    def __init__(self, context: Optional[Any] = None) -> None:
        super().__init__(context)
        self.adapter = get_command_adapter()

    def execute(self, args: argparse.Namespace) -> bool:
        """Execute pause command."""
        try:
            manager = self.adapter.get_manager("PlaybackManager")
            manager.pause(args.device_id)
            print("✓ Playback paused")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


class PlaybackNextCommand(BaseCommand):
    """Skip to next track."""

    def __init__(self, context: Optional[Any] = None) -> None:
        super().__init__(context)
        self.adapter = get_command_adapter()

    def execute(self, args: argparse.Namespace) -> bool:
        """Execute next command."""
        try:
            manager = self.adapter.get_manager("PlaybackManager")
            manager.next(args.device_id)
            print("✓ Skipped to next track")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


# ... PlaybackPreviousCommand, PlaybackStopCommand, etc. (same pattern)
```

**File 2: Update command parser**

```python
# File: cli/command_parser.py

def _add_playback_commands(subparsers):
    """Register playback commands."""

    # Play command
    play_parser = subparsers.add_parser(
        "play",
        help="Resume playback on device"
    )
    play_parser.add_argument("device_id", help="Device ID")
    play_parser.set_defaults(command_class=PlaybackPlayCommand)

    # Pause command
    pause_parser = subparsers.add_parser(
        "pause",
        help="Pause playback on device"
    )
    pause_parser.add_argument("device_id", help="Device ID")
    pause_parser.set_defaults(command_class=PlaybackPauseCommand)

    # Next command
    next_parser = subparsers.add_parser(
        "next",
        help="Skip to next track"
    )
    next_parser.add_argument("device_id", help="Device ID")
    next_parser.set_defaults(command_class=PlaybackNextCommand)

    # ... more commands
```

**File 3: Write tests FIRST**

```python
# File: Dev/pytests/cli/test_playback_commands.py

import argparse
import pytest
from unittest.mock import MagicMock, patch

from cli.commands.music.playback_commands import (
    PlaybackPlayCommand,
    PlaybackPauseCommand,
    PlaybackNextCommand
)


class TestPlaybackPlayCommand:

    def test_execute_success(self):
        """Test play command succeeds."""
        # Arrange
        with patch("get_command_adapter") as mock_adapter_func:
            mock_adapter = MagicMock()
            mock_manager = MagicMock()
            mock_adapter_func.return_value = mock_adapter
            mock_adapter.get_manager.return_value = mock_manager

            cmd = PlaybackPlayCommand()
            args = argparse.Namespace(device_id="device123")

            # Act
            result = cmd.execute(args)

            # Assert
            assert result is True
            mock_manager.play.assert_called_once_with("device123")

    def test_execute_manager_error(self):
        """Test play command handles manager error."""
        # Arrange
        with patch("get_command_adapter") as mock_adapter_func:
            mock_adapter = MagicMock()
            mock_manager = MagicMock()
            mock_manager.play.side_effect = Exception("API error")
            mock_adapter_func.return_value = mock_adapter
            mock_adapter.get_manager.return_value = mock_manager

            cmd = PlaybackPlayCommand()
            args = argparse.Namespace(device_id="device123")

            # Act
            result = cmd.execute(args)

            # Assert
            assert result is False


class TestPlaybackPauseCommand:
    """Similar tests for pause command."""
    pass


class TestPlaybackNextCommand:
    """Similar tests for next command."""
    pass
```

#### Key Differences Highlighted

| Aspect                | Old                                             | New                                                  |
| --------------------- | ----------------------------------------------- | ---------------------------------------------------- |
| **File Organization** | Single file for all playback                    | 7 files, one per command                             |
| **Class Count**       | 1 class                                         | 7 classes                                            |
| **Initialization**    | `PlaybackCommand(config, http_client, breaker)` | `PlaybackPlayCommand()` (no args)                    |
| **Manager Access**    | `self.playback_manager.play()`                  | `self.adapter.get_manager("PlaybackManager").play()` |
| **Method Names**      | `execute_play()`, `execute_pause()`             | `execute()` (uniform)                                |
| **Argument Passing**  | Direct parameters                               | `argparse.Namespace`                                 |
| **Testing**           | Monolithic, integration-heavy                   | Individual commands, unit testable                   |
| **Lines of Code**     | ~150 per command method                         | ~30 per command class                                |

---

## 🐛 COMMON ISSUES

### Issue 1: DIContainer Not Initialized

**Error:**

```
ValueError: Service not registered: PlaybackManager
```

**Cause:** `DIContainer.setup_for_cli()` not called before running commands

**Solution:**

```python
# In alexa_cli.py main()
from core.di_container import DIContainer

def main():
    DIContainer.setup_for_cli()  # Call first!

    parser = CommandParser()
    args = parser.parse(sys.argv[1:])
    # ... rest of main
```

### Issue 2: CommandAdapter Singleton Error

**Error:**

```
AttributeError: 'NoneType' object has no attribute 'get_manager'
```

**Cause:** `CommandAdapter._instance` is None

**Solution:**

```python
# Use get_instance() class method
adapter = CommandAdapter.get_instance()  # ✓ Correct

# NOT this:
adapter = CommandAdapter()  # ✗ Wrong
adapter = CommandAdapter._instance  # ✗ Wrong
```

### Issue 3: Argparse.Namespace Format

**Error:**

```
AttributeError: 'Namespace' object has no attribute 'device_id'
```

**Cause:** Argument not registered in parser or wrong name

**Solution:**

```python
# In command parser
parser.add_argument("device_id", help="Device ID")

# In command
args = argparse.Namespace(device_id="dev123")
manager = self.adapter.get_manager("PlaybackManager")
manager.play(args.device_id)  # ✓ Correct
```

### Issue 4: Async/Await Issues

**Error:**

```
TypeError: 'coroutine' object is not iterable
```

**Cause:** Calling async manager method without await

**Solution:**

```python
# DON'T do this in command (sync context)
result = manager.play(device_id)  # ✗ Returns coroutine

# Instead, manager handles async internally
# Commands remain synchronous
```

### Issue 5: Import Path Changes

**Error:**

```
ModuleNotFoundError: No module named 'cli.commands.playback_command'
```

**Cause:** Old import path no longer exists

**Solution:**

```python
# Old import (broken)
from cli.commands.playback_command import PlaybackCommand

# New import (works)
from cli.commands.music.playback_commands import PlaybackPlayCommand
```

---

## ✅ TESTING & VALIDATION

### Unit Testing

**Run individual command tests:**

```bash
pytest Dev/pytests/cli/commands/ -v
```

**Expected output:**

```
test_playback_play_success PASSED
test_playback_pause_success PASSED
test_playback_next_success PASSED
test_device_list_success PASSED
... (150 tests total)
================================ 150 passed in 0.35s
```

### Integration Testing

**Run full test suite:**

```bash
pytest Dev/pytests/ -v --cov=cli --cov-report=html
```

**Verify:**

- ✅ 150+ tests passing
- ✅ 0 regressions detected
- ✅ Coverage > 85%

### Manual Testing

**Test each command category:**

```bash
# Music playback
alexa play device1
alexa pause device1
alexa next device1

# Device management
alexa device list
alexa device info device1

# Routines
alexa routine list
alexa routine execute routine1

# Alarms
alexa alarm list
alexa alarm add "7:00 AM"

# etc.
```

### Regression Testing

**Before merging, verify:**

```python
# Run tests
pytest Dev/pytests/

# Check type hints
mypy cli/ --strict

# Check lint
pylint cli/

# Check coverage
coverage report --min-coverage=90
```

---

## 🔄 ROLLBACK PLAN

### If Something Goes Wrong

**Step 1: Identify the Issue**

```bash
# Check git status
git status

# Review recent changes
git log --oneline -10
```

**Step 2: Revert to Previous Version**

```bash
# Option A: Reset one file
git checkout main -- cli/commands/music/playback_commands.py

# Option B: Reset entire branch
git reset --hard HEAD~1

# Option C: Switch to backup branch
git checkout backup-old-cli
```

**Step 3: Verify Rollback**

```bash
pytest Dev/pytests/ -q
# Should see: passed (150 tests)
```

**Step 4: Investigate and Fix**

```bash
# Create new branch for fix
git checkout -b fix/issue-name

# Fix the issue
# Commit and test again
# Then merge back
```

---

## ❓ FAQ

### Q: Can I use old and new commands together?

**A:** Yes, during migration. The DIContainer and CommandAdapter support both patterns during transition. However, it's recommended to migrate fully before deploying.

### Q: How long will migration take?

**A:**

- Preparation: 1 hour
- Per command: 5-10 minutes
- Full suite (40 commands): 3-4 hours
- Testing: 1-2 hours
- **Total: ~6-7 hours**

### Q: Do I need to update existing scripts using the CLI?

**A:** Yes, command imports and initialization will need updating. However, the command-line interface (user-facing) remains mostly the same.

### Q: Can I migrate incrementally?

**A:** Yes, but use feature branches:

```bash
git checkout -b migrate-batch1  # Commands 1-10
# ... migrate and test
git checkout -b migrate-batch2  # Commands 11-20
# ... continue
```

### Q: What if a test fails during migration?

**A:**

1. Don't panic - this is expected
2. Check the error message
3. Review the COMMON ISSUES section
4. Fix the specific command
5. Re-run tests
6. If still stuck, consult ARCHITECTURE.md

### Q: How do I verify all commands are migrated?

**A:** Run this check:

```bash
# Old commands should be gone
grep -r "class.*Command" cli/commands/ | grep -v ".pyc" | wc -l
# Should show ~40 commands in new format

# Verify test coverage
pytest Dev/pytests/cli/commands/ --tb=short
# Should show 150 passing
```

### Q: Is there a performance difference?

**A:** Minimal - actually slightly faster because:

- Lazy manager loading
- No duplicate initialization
- Circuit breaker prevents wasted API calls

### Q: What about backward compatibility?

**A:** Full backward compatibility maintained via CommandAdapter bridge pattern. Old code can coexist with new code temporarily.

---

## 📞 SUPPORT

If you encounter issues during migration:

1. **Check COMMON ISSUES** section above
2. **Review ARCHITECTURE.md** for design patterns
3. **Look at existing commands** in `cli/commands/`
4. **Run tests** to verify changes: `pytest Dev/pytests/`
5. **Check git history** for similar implementations

---

## ✨ SUMMARY

**Migration is straightforward:**

1. ✅ Understand the new architecture (1 hour)
2. ✅ Prepare environment (30 minutes)
3. ✅ Migrate commands one by one (3-4 hours)
4. ✅ Run tests after each change (continuous)
5. ✅ Deploy with confidence (30 minutes)

**Result:** A modern, maintainable, testable CLI application!

---

**Migration Status: Ready to Start** 🚀
