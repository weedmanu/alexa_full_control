"""
Gestion des rappels Alexa.

Ce module contient la commande CLI et le manager pour les rappels.
"""

from .command import RemindersCommands as ReminderCommand
from .manager import ReminderManager

__all__ = ["ReminderCommand", "ReminderManager"]



