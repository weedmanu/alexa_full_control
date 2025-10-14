"""
Commandes de contrôle de lecture (playback).

Gère: play, pause, stop, control, shuffle, repeat

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from cli.commands.music.base import MusicSubCommand
from cli.help_texts.music_help import PAUSE_HELP, STOP_HELP, CONTROL_HELP, SHUFFLE_HELP, REPEAT_HELP
from cli.command_parser import ActionHelpFormatter


class PlaybackCommands(MusicSubCommand):
    """Commandes de contrôle de lecture."""

    @staticmethod
    def setup_parsers(subparsers):
        """Configure les parsers pour les commandes de playback."""

        # Action: pause
        pause_parser = subparsers.add_parser(
            "pause",
            help="Mettre en pause la lecture",
            description=PAUSE_HELP,
            formatter_class=ActionHelpFormatter,
        )
        pause_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )

        # Action: stop
        stop_parser = subparsers.add_parser(
            "stop",
            help="Arrêter la lecture",
            description=STOP_HELP,
            formatter_class=ActionHelpFormatter,
        )
        stop_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )

        # Action: control
        control_parser = subparsers.add_parser(
            "control",
            help="Contrôler la lecture",
            description=CONTROL_HELP,
            formatter_class=ActionHelpFormatter,
        )
        control_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )
        control_parser.add_argument(
            "action_type",
            type=str,
            choices=["play", "pause", "next", "prev", "stop"],
            help="Action de contrôle",
        )

        # Action: shuffle
        shuffle_parser = subparsers.add_parser(
            "shuffle",
            help="Mode aléatoire",
            description=SHUFFLE_HELP,
            formatter_class=ActionHelpFormatter,
        )
        shuffle_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        shuffle_parser.add_argument(
            "mode",
            type=str,
            choices=["on", "off", "enable", "disable"],
            help="Activer (on/enable) ou désactiver (off/disable)",
        )

        # Action: repeat
        repeat_parser = subparsers.add_parser(
            "repeat",
            help="Mode répétition",
            description=REPEAT_HELP,
            formatter_class=ActionHelpFormatter,
        )
        repeat_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        repeat_parser.add_argument(
            "mode",
            type=str,
            choices=["off", "one", "all"],
            help="Mode: off (désactivé), one (répéter 1), all (répéter tout)",
        )

    def pause(self, args: argparse.Namespace) -> bool:
        """Mettre en pause la lecture."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"⏸️  Pause sur '{args.device}'...")

            if not self.context.playback_mgr:
                self.error("PlaybackManager non disponible")
                return False

            result = self.context.playback_mgr.pause(serial, device_type)

            if result:
                self.success("✅ Lecture mise en pause")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur pause")
            self.error(f"Erreur: {e}")
            return False

    def stop(self, args: argparse.Namespace) -> bool:
        """Arrêter la lecture."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"⏹️  Arrêt sur '{args.device}'...")

            if not self.context.playback_mgr:
                self.error("PlaybackManager non disponible")
                return False

            result = self.context.playback_mgr.stop(serial, device_type)

            if result:
                self.success("✅ Lecture arrêtée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur stop")
            self.error(f"Erreur: {e}")
            return False

    def control(self, args: argparse.Namespace) -> bool:
        """Contrôler la lecture (play, pause, next, prev, stop)."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            action_icons = {
                "play": "▶️",
                "pause": "⏸️",
                "next": "⏭️",
                "prev": "⏮️",
                "stop": "⏹️",
            }

            icon = action_icons.get(args.action_type, "🎵")
            self.info(f"{icon} {args.action_type.title()} sur '{args.device}'...")

            if not self.context.playback_mgr:
                self.error("PlaybackManager non disponible")
                return False

            # Mapper l'action à la méthode
            method_map = {
                "play": self.context.playback_mgr.play,
                "pause": self.context.playback_mgr.pause,
                "next": self.context.playback_mgr.next_track,
                "prev": self.context.playback_mgr.previous_track,
                "stop": self.context.playback_mgr.stop,
            }

            result = method_map[args.action_type](serial, device_type)

            if result:
                self.success(f"✅ {args.action_type.title()} exécuté")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur control")
            self.error(f"Erreur: {e}")
            return False

    def shuffle(self, args: argparse.Namespace) -> bool:
        """Activer/désactiver le mode aléatoire."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            enabled = args.mode in ["on", "enable"]
            mode_text = "activé" if enabled else "désactivé"

            self.info(f"🔀 Mode aléatoire {mode_text} sur '{args.device}'...")

            if not self.context.playback_mgr:
                self.error("PlaybackManager non disponible")
                return False

            result = self.context.playback_mgr.set_shuffle(serial, device_type, enabled)

            if result:
                self.success(f"✅ Mode aléatoire {mode_text}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur shuffle")
            self.error(f"Erreur: {e}")
            return False

    def repeat(self, args: argparse.Namespace) -> bool:
        """Définir le mode répétition."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            mode_text = {
                "off": "désactivé",
                "one": "répéter 1 morceau",
                "all": "répéter tout",
            }

            self.info(f"🔁 Mode répétition: {mode_text[args.mode]} sur '{args.device}'...")

            if not self.context.playback_mgr:
                self.error("PlaybackManager non disponible")
                return False

            result = self.context.playback_mgr.set_repeat(serial, device_type, args.mode.upper())

            if result:
                self.success(f"✅ Mode répétition: {mode_text[args.mode]}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur repeat")
            self.error(f"Erreur: {e}")
            return False
