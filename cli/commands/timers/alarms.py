﻿"""
Gestion des alarmes Alexa.

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse
import json
import re
from datetime import time
from typing import Any, Dict, List, Optional

from cli.command_parser import UniversalHelpFormatter
from cli.commands.timers.base import TimeSubCommand


class AlarmsCommands(TimeSubCommand):
    """Commandes de gestion des alarmes."""

    # Patterns de rÃ©pÃ©tition
    ALARM_REPEAT_PATTERNS = {
        "ONCE": "Une seule fois",
        "DAILY": "Chaque jour",
        "WEEKLY": "Chaque semaine",
        "WEEKDAYS": "Jours de semaine (lun-ven)",
        "WEEKENDS": "Week-ends (sam-dim)",
        "MONDAY": "Chaque lundi",
        "TUESDAY": "Chaque mardi",
        "WEDNESDAY": "Chaque mercredi",
        "THURSDAY": "Chaque jeudi",
        "FRIDAY": "Chaque vendredi",
        "SATURDAY": "Chaque samedi",
        "SUNDAY": "Chaque dimanche",
    }

    def create(self, args: argparse.Namespace) -> bool:
        """CrÃ©er une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            # Valider et parser l'heure
            alarm_time = self._parse_time(args.time)
            if alarm_time is None:
                self.error(f"Format d'heure invalide: '{args.time}'")
                self.info("Format attendu: HH:MM (24h) - Ex: 07:30, 18:45")
                return False

            label_text = f" '{args.label}'" if args.label else ""
            repeat_text = self.ALARM_REPEAT_PATTERNS.get(args.recurring, args.recurring)

            self.info(f"â° CrÃ©ation alarme{label_text} Ã  {args.time} ({repeat_text}) sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "alarm_mgr", None):
                self.error("AlarmManager non disponible")
                return False

            # CrÃ©er l'alarme
            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(
                ctx.alarm_mgr.create_alarm,
                serial,
                device_type,
                alarm_time,
                args.recurring,
                args.label,
            )

            if result:
                alarm_id = result.get("id", "N/A")
                self.success(f"âœ… Alarme crÃ©Ã©e (ID: {alarm_id})")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la crÃ©ation de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def list(self, args: argparse.Namespace) -> bool:
        """Lister les alarmes."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"â° Alarmes de '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "alarm_mgr", None):
                self.error("AlarmManager non disponible")
                return False

            alarms = self.call_with_breaker(ctx.alarm_mgr.list_alarms, serial)

            if alarms:
                if not alarms:
                    self.warning("Aucune alarme trouvÃ©e")
                    return True

                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(alarms, indent=2, ensure_ascii=False))
                else:
                    self._display(alarms)

                return True

            self.warning("Aucune alarme trouvÃ©e")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la liste des alarmes")
            self.error(f"Erreur: {e}")
            return False

    def delete(self, args: argparse.Namespace) -> bool:
        """Supprimer une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"ðŸ—‘ï¸  Suppression alarme {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "alarm_mgr", None):
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.delete_alarm, serial, device_type, args.id)

            if result:
                self.success("âœ… Alarme supprimÃ©e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def update(self, args: argparse.Namespace) -> bool:
        """Modifier une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            # Valider les modifications
            updates = {}

            if args.time:
                alarm_time = self._parse_time(args.time)
                if alarm_time is None:
                    self.error(f"Format d'heure invalide: '{args.time}'")
                    return False
                updates["time"] = alarm_time

            if args.label:
                updates["label"] = args.label

            if args.recurring:
                updates["repeat"] = args.recurring

            if not updates:
                self.error("Aucune modification spÃ©cifiÃ©e")
                self.info("Utilisez --time, --label ou --recurring")
                return False

            self.info(f"âœï¸  Modification alarme {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "alarm_mgr", None):
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.update_alarm, serial, device_type, args.id, **updates)

            if result:
                self.success("âœ… Alarme modifiÃ©e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la modification de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def enable(self, args: argparse.Namespace) -> bool:
        """Activer une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"âœ… Activation alarme {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "alarm_mgr", None):
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.set_alarm_enabled, serial, device_type, args.id, True)

            if result:
                self.success("âœ… Alarme activÃ©e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'activation de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def disable(self, args: argparse.Namespace) -> bool:
        """DÃ©sactiver une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"âŒ DÃ©sactivation alarme {args.id} sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "alarm_mgr", None):
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.set_alarm_enabled, serial, device_type, args.id, False)

            if result:
                self.success("âœ… Alarme dÃ©sactivÃ©e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la dÃ©sactivation de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def _parse_time(self, time_str: str) -> Optional[str]:
        """
        Parse une heure au format HH:MM.

        Args:
            time_str: ChaÃ®ne d'heure (ex: "07:30", "18:45")

        Returns:
            Heure au format ISO 8601, None si invalide
        """
        # Regex pour HH:MM
        pattern = r"^([01]?[0-9]|2[0-3]):([0-5][0-9])$"
        match = re.fullmatch(pattern, time_str.strip())

        if not match:
            return None

        hours = int(match.group(1))
        minutes = int(match.group(2))

        # CrÃ©er un objet time et convertir en ISO 8601
        alarm_time = time(hours, minutes)
        return alarm_time.isoformat()

    def _display(self, alarms: List[Dict[str, Any]]) -> None:
        """Affiche les alarmes."""
        print(f"\nâ° {len(alarms)} alarme(s):\n")

        for alarm in alarms:
            alarm_id = alarm.get("id", "N/A")
            label = alarm.get("label", "Sans nom")
            alarm_time = alarm.get("time", "N/A")
            repeat = alarm.get("repeat", "ONCE")
            enabled = alarm.get("enabled", False)

            status_emoji = "âœ…" if enabled else "âŒ"
            repeat_text = self.ALARM_REPEAT_PATTERNS.get(repeat, repeat)

            print(f"  {status_emoji} {alarm_time} - {label}")
            print(f"     ID: {alarm_id}")
            print(f"     RÃ©pÃ©tition: {repeat_text}")
            print()

    @staticmethod
    def setup_parsers(subparsers) -> None:
        """
        Configure le sous-parser pour les alarmes.

        Args:
            subparsers: Sous-parsers de la catÃ©gorie timer
        """
        # Sous-catÃ©gorie: alarm
        alarm_parser = subparsers.add_parser(
            "alarm",
            help="GÃ©rer les alarmes",
            description="CrÃ©er et gÃ©rer les alarmes sur Amazon Alexa",
            formatter_class=UniversalHelpFormatter,
        )

        alarm_subparsers = alarm_parser.add_subparsers(
            dest="action",
            title="Actions alarm",
            description="GÃ©rer les alarmes sur Amazon Alexa",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: create
        create_parser = alarm_subparsers.add_parser(
            "create",
            help="CrÃ©er une alarme",
            description="",
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
            "--time",
            type=str,
            required=True,
            metavar="TIME",
            help="Heure de l'alarme (ex: 07:30, 14:15)",
        )
        create_parser.add_argument("--label", type=str, metavar="LABEL", help="Ã‰tiquette de l'alarme (optionnel)")
        create_parser.add_argument(
            "--recurring",
            type=str,
            metavar="DAYS",
            help="Jours de rÃ©currence (ex: mon,wed,fri ou weekdays,weekends)",
        )

        # Action: list
        list_parser = alarm_subparsers.add_parser(
            "list",
            help="Lister les alarmes",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )

        # Action: delete
        delete_parser = alarm_subparsers.add_parser(
            "delete",
            help="Supprimer une alarme",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        delete_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        delete_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="ALARM_ID",
            help="ID de l'alarme Ã  supprimer",
        )

        # Action: update
        update_parser = alarm_subparsers.add_parser(
            "update",
            help="Modifier une alarme",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        update_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        update_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="ALARM_ID",
            help="ID de l'alarme Ã  modifier",
        )
        update_parser.add_argument(
            "--time",
            type=str,
            metavar="TIME",
            help="Nouvelle heure (ex: 07:30, 14:15)",
        )
        update_parser.add_argument("--label", type=str, metavar="LABEL", help="Nouvelle Ã©tiquette")
        update_parser.add_argument(
            "--recurring",
            type=str,
            metavar="DAYS",
            help="Nouveaux jours de rÃ©currence",
        )

        # Action: enable
        enable_parser = alarm_subparsers.add_parser(
            "enable",
            help="Activer une alarme",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        enable_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        enable_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="ALARM_ID",
            help="ID de l'alarme Ã  activer",
        )

        # Action: disable
        disable_parser = alarm_subparsers.add_parser(
            "disable",
            help="DÃ©sactiver une alarme",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        disable_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        disable_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="ALARM_ID",
            help="ID de l'alarme Ã  dÃ©sactiver",
        )

