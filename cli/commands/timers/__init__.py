"""
Module de commandes de gestion du temps - Architecture modulaire.

Organisation:
- base.py: Classe de base commune (utilitaires partagés)
- timers.py: Gestion des minuteurs (create, list, cancel, pause, resume)
- alarms.py: Gestion des alarmes (create, list, delete, update, enable, disable)
- reminders.py: Gestion des rappels (create, list, delete, complete)

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter
from cli.commands.timers.alarms import AlarmsCommands
from cli.commands.timers.reminders import RemindersCommands
from cli.commands.timers.timers import TimersCommands
from cli.help_texts.timers_help import TIMER_DESCRIPTION


class TimerCommand(BaseCommand):
    """
    Commande de gestion du temps Alexa (architecture modulaire).

    Délègue les actions aux sous-modules spécialisés.
    """

    def __init__(self, context=None):
        """Initialise la commande timer avec ses sous-modules."""
        super().__init__(context)

        # Initialiser les sous-commandes
        self.timers = TimersCommands()
        self.alarms = AlarmsCommands()
        self.reminders = RemindersCommands()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes de gestion du temps.

        Délègue la configuration aux sous-modules.

        Args:
            parser: Sous-parser pour la catégorie 'timer'
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Description réorganisée: utiliser la constante partagée
        parser.description = TIMER_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="subcategory",
            metavar="SUBCATEGORY",
            help="Sous-catégorie à gérer",
            required=True,
        )

        # Configuration des sous-parsers par module
        TimersCommands.setup_parsers(subparsers)
        AlarmsCommands.setup_parsers(subparsers)
        RemindersCommands.setup_parsers(subparsers)

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande de gestion du temps.

        Délègue l'exécution au sous-module approprié.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        # Transférer le contexte aux sous-modules
        self._transfer_context()

        # Router vers le bon sous-module
        subcategory = args.subcategory
        action = args.action

        # Commandes Timers
        if subcategory == "countdown":
            return getattr(self.timers, action)(args)

        # Commandes Alarms
        elif subcategory == "alarm":
            return getattr(self.alarms, action)(args)

        # Commandes Reminders
        elif subcategory == "reminder":
            return getattr(self.reminders, action)(args)

        else:
            self.error(f"Sous-catégorie '{subcategory}' non reconnue")
            return False

    def _transfer_context(self):
        """Transfère le contexte aux sous-modules."""
        for sub_command in [self.timers, self.alarms, self.reminders]:
            sub_command.context = self.context
            sub_command.logger = self.logger
