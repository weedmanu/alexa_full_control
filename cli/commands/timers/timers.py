"""
Gestion des minuteurs Alexa.

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse
import json
from typing import Any, Dict, List, Optional

from cli.command_parser import UniversalHelpFormatter
from cli.commands.timers.base import TimeSubCommand
from cli.help_texts.timers_help import (
    TIMER_CANCEL_HELP,
    TIMER_CREATE_HELP,
    TIMER_LIST_HELP,
    TIMER_PAUSE_HELP,
    TIMER_RESUME_HELP,
)


class TimersCommands(TimeSubCommand):
    """Commandes de gestion des minuteurs."""

    def create(self, args: argparse.Namespace) -> bool:
        """
        Créer un minuteur via VoiceCommandService.

        Note: L'API /api/timers retourne 405 Method Not Allowed pour POST.
              Utilisation de VoiceCommandService comme alternative fiable.
        """
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            # Parser la durée
            duration_seconds = self._parse_duration(args.duration)
            if duration_seconds is None:
                self.error(f"Format de durée invalide: '{args.duration}'")
                self.info(
                    "Formats valides: 10m, 1h30m, 2h, 90s, '1 minute', '2 heures', '1 heure 30 minutes'"
                )
                return False

            if duration_seconds <= 0:
                self.error("La durée doit être supérieure à 0")
                return False

            label_text = f" '{args.label}'" if args.label else ""
            duration_text = self._format_duration(duration_seconds)

            self.info(f"⏱️  Création minuteur{label_text} ({duration_text}) sur '{args.device}'...")

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
                self.success(f"✅ Minuteur créé{label_text} ({duration_text})")
                self.info("💡 Vérifiez votre appareil pour confirmer")
                return True
            else:
                self.error("Échec de la création du minuteur")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la création du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def list(self, args: argparse.Namespace) -> bool:
        """Lister les minuteurs."""
        try:
            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            # Si un device est spécifié, lister seulement ses timers
            if args.device:
                serial = self.get_device_serial(args.device)
                if not serial:
                    return False

                self.info(f"⏱️  Minuteurs de '{args.device}'...")
                timers = self.call_with_breaker(ctx.timer_mgr.list_timers, serial)
            else:
                # Aucun device spécifié, lister tous les timers
                self.info("⏱️  Minuteurs de tous les appareils...")
                timers = self.call_with_breaker(ctx.timer_mgr.list_timers)

            if timers:
                # Filtrer si nécessaire
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

            self.warning("Aucun minuteur trouvé")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la liste des minuteurs")
            self.error(f"Erreur: {e}")
            return False

    def cancel(self, args: argparse.Namespace) -> bool:
        """Annuler un minuteur."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            device_type = self._get_device_type(args.device)

            if args.all:
                self.info(f"🗑️  Annulation de tous les minuteurs de '{args.device}'...")

                result = self.call_with_breaker(
                    ctx.timer_mgr.cancel_all_timers, serial, device_type
                )

                if result:
                    count = result.get("cancelled_count", 0)
                    self.success(f"✅ {count} minuteur(s) annulé(s)")
                    return True
            else:
                self.info(f"🗑️  Annulation minuteur {args.id} sur '{args.device}'...")

                result = self.call_with_breaker(
                    ctx.timer_mgr.cancel_timer, serial, device_type, args.id
                )

                if result:
                    self.success("✅ Minuteur annulé")
                    return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'annulation du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def pause(self, args: argparse.Namespace) -> bool:
        """Mettre en pause un minuteur."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"⏸️  Pause minuteur {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(
                ctx.timer_mgr.pause_timer, serial, device_type, args.id
            )

            if result:
                self.success("✅ Minuteur mis en pause")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la pause du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def resume(self, args: argparse.Namespace) -> bool:
        """Reprendre un minuteur."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"▶️  Reprise minuteur {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "timer_mgr", None):
                self.error("TimerManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(
                ctx.timer_mgr.resume_timer, serial, device_type, args.id
            )

            if result:
                self.success("✅ Minuteur repris")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la reprise du minuteur")
            self.error(f"Erreur: {e}")
            return False

    def _build_voice_command(self, duration_seconds: int, label: Optional[str] = None) -> str:
        """
        Construit la commande vocale pour créer un timer.

        Args:
            duration_seconds: Durée en secondes
            label: Étiquette optionnelle du timer

        Returns:
            Commande vocale (ex: "règle un minuteur de 5 minutes nommé Pâtes")
        """
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60

        # Construire la partie durée
        parts = []
        if hours > 0:
            parts.append(f"{hours} heure{'s' if hours > 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        if seconds > 0 and hours == 0:  # Afficher secondes seulement si < 1h
            parts.append(f"{seconds} seconde{'s' if seconds > 1 else ''}")

        duration_text = " ".join(parts) if parts else "1 minute"

        # Construire la commande complète
        command = f"règle un minuteur de {duration_text}"

        if label:
            command += f" nommé {label}"

        return command

    def _display(self, timers: List[Dict[str, Any]]) -> None:
        """Affiche les minuteurs."""
        print(f"\n⏱️  {len(timers)} minuteur(s):\n")

        for timer in timers:
            timer_id = timer.get("id", "N/A")
            label = timer.get("timerLabel", "Sans nom")
            status = timer.get("status", "UNKNOWN")
            remaining_ms = timer.get("remainingTime", 0)
            device_serial = timer.get("deviceSerialNumber", "N/A")

            # Essayer de récupérer le nom de l'appareil
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
                "ON": "▶️ ",
                "PAUSED": "⏸️ ",
                "OFF": "✅",
                "CANCELLED": "❌",
            }.get(status, "❓")

            remaining_text = (
                self._format_duration(remaining_seconds) if remaining_seconds > 0 else "Terminé"
            )

            print(f"  {status_emoji} {label}")
            print(f"     ID: {timer_id}")
            print(f"     Appareil: {device_name}")
            print(f"     Temps restant: {remaining_text}")
            print()

    @staticmethod
    def setup_parsers(subparsers) -> None:
        """
        Configure le sous-parser pour les minuteurs.

        Args:
            subparsers: Sous-parsers de la catégorie timer
        """
        # Sous-catégorie: countdown (anciennement timer)
        timer_parser = subparsers.add_parser(
            "countdown",
            help="Gérer les minuteurs",
            description="Créer et gérer les minuteurs sur Amazon Alexa",
            formatter_class=UniversalHelpFormatter,
        )

        timer_subparsers = timer_parser.add_subparsers(
            dest="action",
            title="Actions timer",
            description="Gérer les minuteurs sur Amazon Alexa",
            help="Action à exécuter",
            required=True,
        )

        # Action: create
        create_parser = timer_subparsers.add_parser(
            "create",
            help="Créer un minuteur",
            description=TIMER_CREATE_HELP,
            formatter_class=UniversalHelpFormatter,
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
            help="Durée du minuteur (ex: 10m, 1h30m, 2h, 90s, '1 minute', '2 heures')",
        )
        create_parser.add_argument(
            "--label", type=str, metavar="LABEL", help="Étiquette du minuteur (optionnel)"
        )

        # Action: list
        list_parser = timer_subparsers.add_parser(
            "list",
            help="Lister les minuteurs",
            description=TIMER_LIST_HELP,
            formatter_class=UniversalHelpFormatter,
        )
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil (optionnel, liste tous les appareils si non spécifié)",
        )
        list_parser.add_argument(
            "--active-only", action="store_true", help="Afficher uniquement les minuteurs actifs"
        )

        # Action: cancel
        cancel_parser = timer_subparsers.add_parser(
            "cancel",
            help="Annuler un minuteur",
            description=TIMER_CANCEL_HELP,
            formatter_class=UniversalHelpFormatter,
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
        cancel_group.add_argument(
            "--id", type=str, metavar="TIMER_ID", help="ID du minuteur à annuler"
        )
        cancel_group.add_argument("--all", action="store_true", help="Annuler tous les minuteurs")

        # Action: pause
        pause_parser = timer_subparsers.add_parser(
            "pause",
            help="Mettre en pause un minuteur",
            description=TIMER_PAUSE_HELP,
            formatter_class=UniversalHelpFormatter,
        )
        pause_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        pause_parser.add_argument(
            "--id", type=str, required=True, metavar="TIMER_ID", help="ID du minuteur"
        )

        # Action: resume
        resume_parser = timer_subparsers.add_parser(
            "resume",
            help="Reprendre un minuteur",
            description=TIMER_RESUME_HELP,
            formatter_class=UniversalHelpFormatter,
        )
        resume_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        resume_parser.add_argument(
            "--id", type=str, required=True, metavar="TIMER_ID", help="ID du minuteur"
        )
