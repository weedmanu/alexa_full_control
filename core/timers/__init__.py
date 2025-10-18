"""
Shim d'import pour garder la compatibilité pendant la réorganisation.

Ce fichier ré-exporte les gestionnaires d'alarmes et de rappels depuis
leurs dossiers dédiés (`core.alarms`, `core.reminders`) tout en conservant
`TimerManager` local. Ainsi les imports existants `from core.timers import ...`
continuent de fonctionner pendant la migration.
"""

from core.alarms.alarm_manager import AlarmManager as AlarmManager
from core.reminders.reminder_manager import ReminderManager as ReminderManager

# Conserver TimerManager local (implémentation spécifique aux minuteurs)
from .timer_manager import TimerManager

__all__ = [
    "TimerManager",
    "AlarmManager",
    "ReminderManager",
]
