"""
Commandes de contr�le de lecture (playback).

G�re: play, pause, stop, control, shuffle, repeat

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from utils.cli.command_parser import ActionHelpFormatter
from utils.cli.base_command import BaseCommand as MusicSubCommand

# Constantes de description simplifi�es
CONTROL_HELP = "Contr�ler la lecture musicale"
PAUSE_HELP = "Mettre en pause la lecture"
REPEAT_HELP = "G�rer la r�p�tition"
SHUFFLE_HELP = "G�rer le mode al�atoire"
STOP_HELP = "Arr�ter la lecture"


class PlaybackCommands(MusicSubCommand):
    """Commandes de contr�le de lecture."""

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
            help="Arr�ter la lecture",
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
            help="Contr�ler la lecture",
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
            help="Action de contr�le",
        )

        # Action: shuffle
        shuffle_parser = subparsers.add_parser(
            "shuffle",
            help="Mode al�atoire",
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
            help="Activer (on/enable) ou d�sactiver (off/disable)",
        )

        # Action: repeat
        repeat_parser = subparsers.add_parser(
            "repeat",
            help="Mode r�p�tition",
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
            help="Mode: off (d�sactiv�), one (r�p�ter 1), all (r�p�ter tout)",
        )

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes de playback.

        Args:
            parser: Sous-parser pour la cat�gorie 'playback'
        """
        from utils.cli.command_parser import UniversalHelpFormatter

        # Utiliser le formatter universel pour l'ordre exact demand�
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description simplifi�e
        parser.description = "Contr�ler la lecture musicale Alexa"

        # Cr�er les sous-parsers pour les actions
        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action � ex�cuter",
            required=True,
        )

        # D�l�guer la configuration des sous-parsers � la m�thode statique
        self.setup_parsers(subparsers)

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Ex�cute la commande de playback selon l'action.

        Args:
            args: Arguments pars�s

        Returns:
            True si succ�s, False sinon
        """
        if not self.validate_connection():
            return False

        action = getattr(args, "action", None)
        if not action:
            self.error("Action manquante")
            return False

        # Router vers la bonne m�thode selon l'action
        if action == "pause":
            return self.pause_playback(args)
        elif action == "stop":
            return self.stop_playback(args)
        elif action == "control":
            return self.control_playback(args)
        elif action == "shuffle":
            return self.shuffle_playback(args)
        elif action == "repeat":
            return self.repeat_playback(args)
        else:
            self.error(f"Action '{action}' non reconnue")
            return False

    def pause(self, args: argparse.Namespace) -> bool:
        """Mettre en pause la lecture."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"??  Pause sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.pause(serial, device_type)

            if result:
                self.success("? Lecture mise en pause")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur pause")
            self.error(f"Erreur: {e}")
            return False

    def stop(self, args: argparse.Namespace) -> bool:
        """Arr�ter la lecture."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"??  Arr�t sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.stop(serial, device_type)

            if result:
                self.success("? Lecture arr�t�e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur stop")
            self.error(f"Erreur: {e}")
            return False

    def control(self, args: argparse.Namespace) -> bool:
        """Contr�ler la lecture (play, pause, next, prev, stop)."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            action_icons = {
                "play": "??",
                "pause": "??",
                "next": "??",
                "prev": "??",
                "stop": "??",
            }

            icon = action_icons.get(args.action_type, "??")
            self.info(f"{icon} {args.action_type.title()} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            # Mapper l'action � la m�thode
            method_map = {
                "play": ctx.playback_mgr.play,
                "pause": ctx.playback_mgr.pause,
                "next": ctx.playback_mgr.next_track,
                "prev": ctx.playback_mgr.previous_track,
                "stop": ctx.playback_mgr.stop,
            }

            result = method_map[args.action_type](serial, device_type)

            if result:
                self.success(f"? {args.action_type.title()} ex�cut�")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur control")
            self.error(f"Erreur: {e}")
            return False

    def shuffle(self, args: argparse.Namespace) -> bool:
        """Activer/d�sactiver le mode al�atoire."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            enabled = args.mode in ["on", "enable"]
            mode_text = "activ�" if enabled else "d�sactiv�"

            self.info(f"?? Mode al�atoire {mode_text} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.set_shuffle(serial, device_type, enabled)

            if result:
                self.success(f"? Mode al�atoire {mode_text}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur shuffle")
            self.error(f"Erreur: {e}")
            return False

    def repeat(self, args: argparse.Namespace) -> bool:
        """D�finir le mode r�p�tition."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            mode_text = {
                "off": "d�sactiv�",
                "one": "r�p�ter 1 morceau",
                "all": "r�p�ter tout",
            }

            self.info(f"?? Mode r�p�tition: {mode_text[args.mode]} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            result = ctx.playback_mgr.set_repeat(serial, device_type, args.mode.upper())

            if result:
                self.success(f"? Mode r�p�tition: {mode_text[args.mode]}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur repeat")
            self.error(f"Erreur: {e}")
            return False




