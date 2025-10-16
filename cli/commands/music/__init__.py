"""
Module de commandes musicales - Architecture modulaire.

Organisation:
- base.py: Classe de base commune
- playback.py: Contrôle lecture (pause, stop, control, shuffle, repeat)
- library.py: Bibliothèque (track, playlist, library)
- tunein.py: Radio TuneIn
- status.py: Informations (status, queue)

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter
from cli.commands.music.library import LibraryCommands
from cli.commands.music.playback import PlaybackCommands
from cli.commands.music.status import StatusCommands
from cli.commands.music.tunein import TuneInCommands


# Constante de description simplifiée
MUSIC_DESCRIPTION = "Gérer la musique et la lecture audio"


class MusicCommand(BaseCommand):
    """
    Commande de contrôle musical Alexa (architecture modulaire).

    Délègue les actions aux sous-modules spécialisés.
    """

    def __init__(self, context=None):
        """Initialise la commande music avec ses sous-modules."""
        super().__init__(context)

        # Initialiser les sous-commandes
        self.playback = PlaybackCommands()
        self.library = LibraryCommands()
        self.tunein = TuneInCommands()
        self.status = StatusCommands()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes musicales.

        Délègue la configuration aux sous-modules.

        Args:
            parser: Sous-parser pour la catégorie 'music'
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Description réorganisée: utiliser la constante partagée
        parser.description = MUSIC_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Configuration des sous-parsers par module
        PlaybackCommands.setup_parsers(subparsers)
        LibraryCommands.setup_parsers(subparsers)
        TuneInCommands.setup_parsers(subparsers)
        StatusCommands.setup_parsers(subparsers)

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande musicale.

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
        action = args.action

        # Commandes Playback
        if action in ["pause", "stop", "control", "shuffle", "repeat"]:
            return getattr(self.playback, action)(args)

        # Commandes Library
        elif action in ["track", "playlist", "library"]:
            return getattr(self.library, action)(args)

        # Commandes TuneIn
        elif action == "radio":
            return self.tunein.radio(args)

        # Commandes Status
        elif action in ["status", "queue"]:
            return getattr(self.status, action)(args)

        else:
            self.error(f"Action '{action}' non reconnue")
            return False

    def _transfer_context(self):
        """Transfère le contexte aux sous-modules."""
        for sub_command in [self.playback, self.library, self.tunein, self.status]:
            sub_command.context = self.context
            sub_command.logger = self.logger
