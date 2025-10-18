"""
Commandes TuneIn radio.

G�re: radio (TuneIn)

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from utils.cli.base_command import BaseCommand as MusicSubCommand


class TuneInCommands(MusicSubCommand):
    """Commandes TuneIn radio."""

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser pour les commandes TuneIn."""
        subparsers = parser.add_subparsers(dest="action", help="Action � effectuer")

        # Action: radio
        radio_parser = subparsers.add_parser(
            "radio",
            help="Jouer une station TuneIn",
            description="Lance une station de radio TuneIn.",
        )
        radio_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        radio_parser.add_argument(
            "--station-id",
            type=str,
            required=True,
            metavar="STATION_ID",
            help="ID de la station TuneIn (ex: s24939)",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """Ex�cute la commande."""
        if args.action == "radio":
            return self.radio(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def radio(self, args: argparse.Namespace) -> bool:
        """Jouer une station TuneIn."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "music_library", None):
                self.error("MusicLibraryService non disponible")
                return False

            self.info(f"?? Lecture station TuneIn {args.station_id} sur '{args.device}'...")

            result = self.call_with_breaker(
                ctx.music_library.play_tunein_radio,
                serial,
                device_type,
                args.station_id,
            )

            if result:
                self.success("? Station TuneIn lanc�e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lecture TuneIn")
            self.error(f"Erreur: {e}")
            return False




