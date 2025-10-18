﻿"""
Gestion des minuteurs Alexa.

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse
import json
from typing import Any, Dict, List, Optional

from utils.cli.command_parser import UniversalHelpFormatter
from utils.cli.base_command import BaseCommand as TimeSubCommand


class TimersCommands(TimeSubCommand):
    """Commandes de gestion des minuteurs."""

    def create(self, args: argparse.Namespace) -> bool:
        """
        Cr�er un minuteur via VoiceCommandService.

        Note: L'API /api/timers retourne 405 Method Not Allowed pour POST.
              Utilisation de VoiceCommandService comme alternative fiable.
        """
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            # Parser la dur�e
            duration_seconds = self._parse_duration(args.duration)
            if duration_seconds is None:
                self.error(f"Format de dur�e invalide: '{args.duration}'")
                self.info("Formats valides: 10m, 1h30m, 2h, 90s, '1 minute', '2 heures', '1 heure 30 minutes'")
                return False

            if duration_seconds <= 0:
                self.error("La dur�e doit �tre sup�rieure � 0")
                return False

            label_text = f" '{args.label}'" if args.label else ""
            duration_text = self._format_duration(duration_seconds)

            self.info(f"??  Cr�ation minuteur{label_text} ({duration_text}) sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "voice_service", None):
                self.error("VoiceCommandService non disponible")
                return False

            # Construire la commande vocale
            command = self._build_voice_command(duration_seconds, args.label)

            self.debug(f"Commande vocale: '{command}'")

            # Envoyer via VoiceCommandService
            result = self.call_with_breaker(
                ctx.voice_service.speak,
                command,
                serial,
            )

            if result:
                self.success(f"? Minuteur cr��{label_text} ({duration_text})")
                self.info("?? V�rifiez votre appareil pour confirmer")
                return True
            else:
                self.error("�chec de la cr�ation du minuteur")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la cr�ation du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def list(self, args: argparse.Namespace) -> bool:
        """Lister les minuteurs."""
        try:
            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            # Si un device est sp�cifi�, lister seulement ses timers
            if args.device:
                device_info = self.get_device_info(args.device)
                if not device_info:
                    return False

                serial, device_type = device_info

                self.info(f"??  Minuteurs de '{args.device}'...")
                timers = self.call_with_breaker(ctx.timer_mgr.list_timers, serial)
            else:
                # Aucun device sp�cifi�, lister tous les timers
                self.info("??  Minuteurs de tous les appareils...")
                timers = self.call_with_breaker(ctx.timer_mgr.list_timers)

            if timers:
                # Filtrer si n�cessaire
                if args.active_only:
                    timers = [t for t in timers if t.get("status") == "ACTIVE"]

                if not timers:
                    self.warning("Aucun minuteur actif")
                    return True

                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(timers, indent=2, ensure_ascii=False))
                else:
                    self._display(timers)

                return True

            self.warning("Aucun minuteur trouv�")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la liste des minuteurs")
            self.error(f"Erreur: {e}")
            return False

    def cancel(self, args: argparse.Namespace) -> bool:
        """Annuler un minuteur."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            if args.all:
                self.info(f"???  Annulation de tous les minuteurs de '{args.device}'...")

                result = self.call_with_breaker(ctx.timer_mgr.cancel_all_timers, serial, device_type)

                if result:
                    count = result.get("cancelled_count", 0)
                    self.success(f"? {count} minuteur(s) annul�(s)")
                    return True
            else:
                self.info(f"???  Annulation minuteur {args.id} sur '{args.device}'...")

                result = self.call_with_breaker(ctx.timer_mgr.cancel_timer, serial, device_type, args.id)

                if result:
                    self.success("? Minuteur annul�")
                    return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'annulation du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def pause(self, args: argparse.Namespace) -> bool:
        """Mettre en pause un minuteur."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"??  Pause minuteur {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            result = self.call_with_breaker(ctx.timer_mgr.pause_timer, serial, device_type, args.id)

            if result:
                self.success("? Minuteur mis en pause")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la pause du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def resume(self, args: argparse.Namespace) -> bool:
        """Reprendre un minuteur."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"??  Reprise minuteur {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            result = self.call_with_breaker(ctx.timer_mgr.resume_timer, serial, device_type, args.id)

            if result:
                self.success("? Minuteur repris")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la reprise du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def _build_voice_command(self, duration_seconds: int, label: Optional[str] = None) -> str:
        """
        Construit la commande vocale pour cr�er un timer.

        Args:
            duration_seconds: Dur�e en secondes
            label: �tiquette optionnelle du timer

        Returns:
            Commande vocale (ex: "r�gle un minuteur de 5 minutes nomm� P�tes")
        """
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60

        # Construire la partie dur�e
        parts = []
        if hours > 0:
            parts.append(f"{hours} heure{'s' if hours > 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        if seconds > 0 and hours == 0:  # Afficher secondes seulement si < 1h
            parts.append(f"{seconds} seconde{'s' if seconds > 1 else ''}")

        duration_text = " ".join(parts) if parts else "1 minute"

        # Construire la commande compl�te
        command = f"r�gle un minuteur de {duration_text}"

        if label:
            command += f" nomm� {label}"

        return command

    def _display(self, timers: List[Dict[str, Any]]) -> None:
        """Affiche les minuteurs."""
        print(f"\n??  {len(timers)} minuteur(s):\n")

        for timer in timers:
            timer_id = timer.get("id", "N/A")
            label = timer.get("timerLabel", "Sans nom")
            status = timer.get("status", "UNKNOWN")
            remaining_ms = timer.get("remainingTime", 0)
            device_serial = timer.get("deviceSerialNumber", "N/A")

            # Essayer de r�cup�rer le nom de l'appareil
            device_name = "Inconnu"
            ctx = getattr(self, "context", None)
            if ctx and getattr(ctx, "device_mgr", None):
                try:
                    device_info = ctx.device_mgr.find_device_by_serial(device_serial)
                    if device_info:
                        device_name = device_info.get("accountName", device_serial)
                except Exception:
                    device_name = device_serial

            # Convertir millisecondes en secondes
            remaining_seconds = remaining_ms // 1000

            status_emoji = {
                "ON": "?? ",
                "PAUSED": "?? ",
                "OFF": "?",
                "CANCELLED": "?",
            }.get(status, "?")

            remaining_text = self._format_duration(remaining_seconds) if remaining_seconds > 0 else "Termin�"

            print(f"  {status_emoji} {label}")
            print(f"     ID: {timer_id}")
            print(f"     Appareil: {device_name}")
            print(f"     Temps restant: {remaining_text}")
            print()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser pour les commandes de minuteurs."""
        subparsers = parser.add_subparsers(
            dest="action",
            title="Actions timer",
            description="G�rer les minuteurs sur Amazon Alexa",
            help="Action � ex�cuter",
            required=True,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="Cr�er un minuteur",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        create_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )
        create_parser.add_argument(
            "--duration",
            type=str,
            required=True,
            metavar="DURATION",
            help="Dur�e du minuteur (ex: 10m, 1h30m, 2h, 90s, '1 minute', '2 heures')",
        )
        create_parser.add_argument("--label", type=str, metavar="LABEL", help="�tiquette du minuteur (optionnel)")

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Lister les minuteurs",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil (optionnel, liste tous les appareils si non sp�cifi�)",
        )
        list_parser.add_argument("--active-only", action="store_true", help="Afficher uniquement les minuteurs actifs")

        # Action: cancel
        cancel_parser = subparsers.add_parser(
            "cancel",
            help="Annuler un minuteur",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        cancel_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        cancel_group = cancel_parser.add_mutually_exclusive_group(required=True)
        cancel_group.add_argument("--id", type=str, metavar="TIMER_ID", help="ID du minuteur � annuler")
        cancel_group.add_argument("--all", action="store_true", help="Annuler tous les minuteurs")

        # Action: pause
        pause_parser = subparsers.add_parser(
            "pause",
            help="Mettre en pause un minuteur",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        pause_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        pause_parser.add_argument("--id", type=str, required=True, metavar="TIMER_ID", help="ID du minuteur")

        # Action: resume
        resume_parser = subparsers.add_parser(
            "resume",
            help="Reprendre un minuteur",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        resume_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        resume_parser.add_argument("--id", type=str, required=True, metavar="TIMER_ID", help="ID du minuteur")

    def execute(self, args: argparse.Namespace) -> bool:
        """Ex�cute la commande."""
        if args.action == "create":
            return self.create(args)
        elif args.action == "list":
            return self.list(args)
        elif args.action == "cancel":
            return self.cancel(args)
        elif args.action == "pause":
            return self.pause(args)
        elif args.action == "resume":
            return self.resume(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False




