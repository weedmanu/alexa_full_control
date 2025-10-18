"""
Shim for ReminderManager: delegate to `core.reminders.reminder_manager.ReminderManager`.

Preserve backward-compatible import paths during refactor.
"""

from core.reminders.reminder_manager import ReminderManager  # type: ignore

__all__ = ["ReminderManager"]
