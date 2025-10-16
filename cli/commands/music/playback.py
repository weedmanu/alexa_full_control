"""
Commandes de contrÃ´le de lecture (playback).

GÃ¨re: play, pause, stop, control, shuffle, repeat

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from cli.command_parser import ActionHelpFormatter
from cli.commands.music.base import MusicSubCommand


# Constantes de description simplifiÃ©es
CONTROL_HELP = "ContrÃ´ler la lecture musicale"
PAUSE_HELP = "Mettre en pause la lecture"
REPEAT_HELP = "GÃ©rer la rÃ©pÃ©tition"
SHUFFLE_HELP = "GÃ©rer le mode alÃ©atoire"
STOP_HELP = "ArrÃªter la lecture"


class PlaybackCommands(MusicSubCommand):
    """Commandes de contrÃ´le de lecture."""

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
            help="ArrÃªter la lecture",
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
            help="ContrÃ´ler la lecture",
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
            help="Action de contrÃ´le",
        )

        # Action: shuffle
        shuffle_parser = subparsers.add_parser(
            "shuffle",
            help="Mode alÃ©atoire",
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
            help="Activer (on/enable) ou dÃ©sactiver (off/disable)",
        )

        # Action: repeat
        repeat_parser = subparsers.add_parser(
            "repeat",
            help="Mode rÃ©pÃ©tition",
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
            help="Mode: off (dÃ©sactivÃ©), one (rÃ©pÃ©ter 1), all (rÃ©pÃ©ter tout)",
        )

    def pause(self, args: argparse.Namespace) -> bool:
        """Mettre en pause la lecture."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"â¸ï¸  Pause sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.pause(serial, device_type)

            if result:
                self.success("âœ… Lecture mise en pause")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur pause")
            self.error(f"Erreur: {e}")
            return False

    def stop(self, args: argparse.Namespace) -> bool:
        """ArrÃªter la lecture."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"â¹ï¸  ArrÃªt sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.stop(serial, device_type)

            if result:
                self.success("âœ… Lecture arrÃªtÃ©e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur stop")
            self.error(f"Erreur: {e}")
            return False

    def control(self, args: argparse.Namespace) -> bool:
        """ContrÃ´ler la lecture (play, pause, next, prev, stop)."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            action_icons = {
                "play": "â–¶ï¸",
                "pause": "â¸ï¸",
                "next": "â­ï¸",
                "prev": "â®ï¸",
                "stop": "â¹ï¸",
            }

            icon = action_icons.get(args.action_type, "ðŸŽµ")
            self.info(f"{icon} {args.action_type.title()} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            # Mapper l'action Ã  la mÃ©thode
            method_map = {
                "play": ctx.playback_mgr.play,
                "pause": ctx.playback_mgr.pause,
                "next": ctx.playback_mgr.next_track,
                "prev": ctx.playback_mgr.previous_track,
                "stop": ctx.playback_mgr.stop,
            }

            result = method_map[args.action_type](serial, device_type)

            if result:
                self.success(f"âœ… {args.action_type.title()} exÃ©cutÃ©")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur control")
            self.error(f"Erreur: {e}")
            return False

    def shuffle(self, args: argparse.Namespace) -> bool:
        """Activer/dÃ©sactiver le mode alÃ©atoire."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            enabled = args.mode in ["on", "enable"]
            mode_text = "activÃ©" if enabled else "dÃ©sactivÃ©"

            self.info(f"ðŸ”€ Mode alÃ©atoire {mode_text} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.set_shuffle(serial, device_type, enabled)

            if result:
                self.success(f"âœ… Mode alÃ©atoire {mode_text}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur shuffle")
            self.error(f"Erreur: {e}")
            return False

    def repeat(self, args: argparse.Namespace) -> bool:
        """DÃ©finir le mode rÃ©pÃ©tition."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            mode_text = {
                "off": "dÃ©sactivÃ©",
                "one": "rÃ©pÃ©ter 1 morceau",
                "all": "rÃ©pÃ©ter tout",
            }

            self.info(f"ðŸ” Mode rÃ©pÃ©tition: {mode_text[args.mode]} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.set_repeat(serial, device_type, args.mode.upper())

            if result:
                self.success(f"âœ… Mode rÃ©pÃ©tition: {mode_text[args.mode]}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur repeat")
            self.error(f"Erreur: {e}")
            return False

