"""
Shim for AlarmManager: delegate to `core.alarms.alarm_manager.AlarmManager`.

This keeps imports like `from core.timers import AlarmManager` working while
the authoritative implementation lives in `core.alarms`.
"""

from core.alarms.alarm_manager import AlarmManager  # type: ignore

__all__ = ["AlarmManager"]

