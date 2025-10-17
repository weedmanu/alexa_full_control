"""
Commande Timers - Agrégateur des actions temporelles.

Combine:
- timers_alarm.py: add, list, delete, update, enable, disable (alarmes)
- timers_reminder.py: add, list, delete, complete (rappels)
- timers_countdown.py: create, list, cancel, pause, resume (minuteurs)

Auteur: M@nu
Date: 17 octobre 2025
"""

from typing import Any, Optional
import argparse

from cli.base_command import BaseCommand
from cli.commands.timers_alarm import AlarmsCommands
from cli.commands.timers_reminder import RemindersCommands
from cli.commands.timers_countdown import TimersCommands


class TimerCommand(BaseCommand):
    """Commande Timers - agrège alarms, reminders, countdown."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        # Charger les sous-commandes
        self.alarms_cmds = AlarmsCommands()
        self.reminder_cmds = RemindersCommands()
        self.timer_cmds = TimersCommands()

        # Injecter le contexte
        self.alarms_cmds.context = context
        self.reminder_cmds.context = context
        self.timer_cmds.context = context

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure les actions disponibles."""
        subparsers = parser.add_subparsers(dest="action", required=True)

        # Alarmes
        self.alarms_cmds.setup_parsers(subparsers)
        # Rappels
        self.reminder_cmds.setup_parsers(subparsers)
        # Minuteurs
        self.timer_cmds.setup_parsers(subparsers)

    def execute(self, args: argparse.Namespace) -> bool:
        """Exécute l'action temporelle."""
        try:
            # Router vers la bonne sous-commande
            if hasattr(self.alarms_cmds, args.action):
                method = getattr(self.alarms_cmds, args.action)
                return method(args)
            elif hasattr(self.reminder_cmds, args.action):
                method = getattr(self.reminder_cmds, args.action)
                return method(args)
            elif hasattr(self.timer_cmds, args.action):
                method = getattr(self.timer_cmds, args.action)
                return method(args)
            else:
                self.error(f"Action inconnue: {args.action}")
                return False
        except Exception as e:
            self.logger.exception("Erreur timers command")
            self.error(f"Erreur: {e}")
            return False


__all__ = ["TimerCommand"]
