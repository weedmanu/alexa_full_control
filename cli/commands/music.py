"""
Commande Music - Agrégateur des actions musicales.

Combine:
- music_library.py: library, track, playlist
- music_playback.py: play, pause, stop, control, shuffle, repeat
- music_tunein.py: radio

Auteur: M@nu
Date: 17 octobre 2025
"""

import argparse
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.commands.music_library import LibraryCommands
from cli.commands.music_playback import PlaybackCommands
from cli.commands.music_tunein import TuneInCommands


class MusicCommand(BaseCommand):
    """Commande Music - agrège playback, library, tunein."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        # Charger les sous-commandes
        self.library_cmds = LibraryCommands()
        self.playback_cmds = PlaybackCommands()
        self.tunein_cmds = TuneInCommands()

        # Injecter le contexte
        self.library_cmds.context = context
        self.playback_cmds.context = context
        self.tunein_cmds.context = context

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure les actions disponibles."""
        subparsers = parser.add_subparsers(dest="action", required=True)

        # Bibliothèque musicale
        self.library_cmds.setup_parsers(subparsers)
        # Lecture/contrôle
        self.playback_cmds.setup_parsers(subparsers)
        # TuneIn radio
        self.tunein_cmds.setup_parsers(subparsers)

    def execute(self, args: argparse.Namespace) -> bool:
        """Exécute l'action musicale."""
        try:
            # Router vers la bonne sous-commande
            if hasattr(self.library_cmds, args.action):
                method = getattr(self.library_cmds, args.action)
                return method(args)
            elif hasattr(self.playback_cmds, args.action):
                method = getattr(self.playback_cmds, args.action)
                return method(args)
            elif hasattr(self.tunein_cmds, args.action):
                method = getattr(self.tunein_cmds, args.action)
                return method(args)
            else:
                self.error(f"Action inconnue: {args.action}")
                return False
        except Exception as e:
            self.logger.exception("Erreur music command")
            self.error(f"Erreur: {e}")
            return False


__all__ = ["MusicCommand"]
