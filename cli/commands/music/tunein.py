"""
Commandes TuneIn radio.

Gère: radio (TuneIn)

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from cli.commands.music.base import MusicSubCommand


class TuneInCommands(MusicSubCommand):
    """Commandes TuneIn radio."""

    @staticmethod
    def setup_parsers(subparsers):
        """Configure les parsers pour les commandes TuneIn."""

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

    def radio(self, args: argparse.Namespace) -> bool:
        """Jouer une station TuneIn."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            if not hasattr(self.context, "music_library"):
                self.error("MusicLibraryService non disponible")
                return False

            self.info(f"📻 Lecture station TuneIn {args.station_id} sur '{args.device}'...")

            result = self.call_with_breaker(
                self.context.music_library.play_tunein_radio,
                serial,
                device_type,
                args.station_id,
            )

            if result:
                self.success("✅ Station TuneIn lancée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lecture TuneIn")
            self.error(f"Erreur: {e}")
            return False
