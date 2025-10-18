"""
Commandes de gestion des alarmes Alexa.

Ce module gère toutes les opérations liées aux alarmes:
- create: Créer une nouvelle alarme
- list: Lister toutes les alarmes
- delete: Supprimer une alarme
- update: Modifier une alarme existante
- enable: Activer une alarme
- disable: Désactiver une alarme

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import json
import re
from datetime import time
from typing import Optional

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter


class AlarmCommand(BaseCommand):
    """
    Commande de gestion des alarmes Alexa.

    Gère create, list, delete, update, enable, disable.

    Actions:
        - create: Créer une nouvelle alarme
        - list: Lister toutes les alarmes
        - delete: Supprimer une alarme
        - update: Modifier une alarme
        - enable: Activer une alarme
        - disable: Désactiver une alarme

    Example:
        >>> alexa alarm create -d "Chambre" --time 07:30 --label "Réveil"
        >>> alexa alarm create -d "Chambre" --time 08:00 --repeat WEEKDAYS
        >>> alexa alarm list -d "Chambre"
        >>> alexa alarm delete -d "Chambre" --id ALARM_ID
        >>> alexa alarm update -d "Chambre" --id ALARM_ID --time 08:00
        >>> alexa alarm enable -d "Chambre" --id ALARM_ID
        >>> alexa alarm disable -d "Chambre" --id ALARM_ID
    """

    # Patterns de répétition
    REPEAT_PATTERNS = {
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

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes alarm.

        Args:
            parser: Sous-parser pour la catégorie 'alarm'
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description simple
        parser.description = ""

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="Créer une alarme",
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
            "--time",
            type=str,
            required=True,
            metavar="HH:MM",
            help="Heure de l'alarme (format 24h: 07:30, 18:45)",
        )
        create_parser.add_argument("--label", type=str, metavar="LABEL", help="Étiquette de l'alarme (optionnel)")
        create_parser.add_argument(
            "--repeat",
            type=str,
            choices=list(AlarmCommand.REPEAT_PATTERNS.keys()),
            default="ONCE",
            metavar="PATTERN",
            help=f"Pattern de répétition (défaut: ONCE). Choix: {', '.join(AlarmCommand.REPEAT_PATTERNS.keys())}",
        )
        create_parser.add_argument(
            "--sound", type=str, metavar="SOUND_ID", help="ID du son/musique d'alarme (optionnel)"
        )

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Lister les alarmes",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil (optionnel, tous les appareils si non spécifié)",
        )
        list_parser.add_argument("--active-only", action="store_true", help="Afficher uniquement les alarmes activées")

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Supprimer une alarme",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
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
            "--id", type=str, required=True, metavar="ALARM_ID", help="ID de l'alarme à supprimer"
        )

        # Action: update
        update_parser = subparsers.add_parser(
            "update",
            help="Modifier une alarme",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
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
            "--id", type=str, required=True, metavar="ALARM_ID", help="ID de l'alarme à modifier"
        )
        update_parser.add_argument("--time", type=str, metavar="HH:MM", help="Nouvelle heure (optionnel)")
        update_parser.add_argument("--label", type=str, metavar="LABEL", help="Nouvelle étiquette (optionnel)")
        update_parser.add_argument(
            "--repeat",
            type=str,
            choices=list(AlarmCommand.REPEAT_PATTERNS.keys()),
            metavar="PATTERN",
            help="Nouveau pattern de répétition (optionnel)",
        )
        update_parser.add_argument("--sound", type=str, metavar="SOUND_ID", help="Nouveau son d'alarme (optionnel)")

        # Action: enable
        enable_parser = subparsers.add_parser(
            "enable",
            help="Activer une alarme",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        enable_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        enable_parser.add_argument("--id", type=str, required=True, metavar="ALARM_ID", help="ID de l'alarme à activer")

        # Action: disable
        disable_parser = subparsers.add_parser(
            "disable",
            help="Désactiver une alarme",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
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
            "--id", type=str, required=True, metavar="ALARM_ID", help="ID de l'alarme à désactiver"
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande alarm.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "create":
            return self._create_alarm(args)
        elif args.action == "list":
            return self._list_alarms(args)
        elif args.action == "delete":
            return self._delete_alarm(args)
        elif args.action == "update":
            return self._update_alarm(args)
        elif args.action == "enable":
            return self._enable_alarm(args)
        elif args.action == "disable":
            return self._disable_alarm(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _create_alarm(self, args: argparse.Namespace) -> bool:
        """Créer une alarme."""
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
            repeat_text = self.REPEAT_PATTERNS.get(args.repeat, args.repeat)

            self.info(f"⏰ Création alarme{label_text} à {args.time} ({repeat_text}) sur '{args.device}'...")

            ctx = self.require_context()
            if not ctx.alarm_mgr:
                self.error("AlarmManager non disponible")
                return False

            # Créer l'alarme
            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(
                ctx.alarm_mgr.create_alarm,
                serial,
                device_type,
                alarm_time,
                args.repeat,
                args.label,
                args.sound,
            )

            if result:
                alarm_id = result.get("id", "N/A")
                self.success(f"✅ Alarme créée (ID: {alarm_id})")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la création de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def _list_alarms(self, args: argparse.Namespace) -> bool:
        """Lister les alarmes."""
        try:
            device_name = getattr(args, "device", None)

            if device_name:
                self.info(f"⏰ Alarmes de '{device_name}'...")
                serial = self.get_device_serial(device_name)
                if not serial:
                    return False
            else:
                self.info("⏰ Alarmes de tous les appareils...")
                serial = None

            ctx = self.require_context()
            if not ctx.alarm_mgr:
                self.error("AlarmManager non disponible")
                return False

            # AlarmManager.list_alarms attend device_serial (optionnel)
            alarms = self.call_with_breaker(ctx.alarm_mgr.list_alarms, serial)

            if alarms:
                # Filtrer si nécessaire
                if args.active_only:
                    alarms = [a for a in alarms if a.get("alarmTime", 0) > 0]

                if not alarms:
                    self.warning("Aucune alarme active")
                    return True

                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(alarms, indent=2, ensure_ascii=False))
                else:
                    self._display_alarms(alarms)

                return True

            self.warning("Aucune alarme trouvée")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la liste des alarmes")
            self.error(f"Erreur: {e}")
            return False

    def _delete_alarm(self, args: argparse.Namespace) -> bool:
        """Supprimer une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"🗑️  Suppression alarme {args.id} sur '{args.device}'...")

            ctx = self.require_context()
            if not ctx.alarm_mgr:
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.delete_alarm, serial, device_type, args.id)

            if result:
                self.success("✅ Alarme supprimée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def _update_alarm(self, args: argparse.Namespace) -> bool:
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

            if args.repeat:
                updates["repeat"] = args.repeat

            if args.sound:
                updates["sound"] = args.sound

            if not updates:
                self.error("Aucune modification spécifiée")
                self.info("Utilisez --time, --label, --repeat ou --sound")
                return False

            self.info(f"✏️  Modification alarme {args.id} sur '{args.device}'...")

            ctx = self.require_context()
            if not ctx.alarm_mgr:
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.update_alarm, serial, device_type, args.id, **updates)

            if result:
                self.success("✅ Alarme modifiée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la modification de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def _enable_alarm(self, args: argparse.Namespace) -> bool:
        """Activer une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"✅ Activation alarme {args.id} sur '{args.device}'...")

            ctx = self.require_context()
            if not ctx.alarm_mgr:
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.set_alarm_enabled, serial, device_type, args.id, True)

            if result:
                self.success("✅ Alarme activée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'activation de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    def _disable_alarm(self, args: argparse.Namespace) -> bool:
        """Désactiver une alarme."""
        try:
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"❌ Désactivation alarme {args.id} sur '{args.device}'...")

            ctx = self.require_context()
            if not ctx.alarm_mgr:
                self.error("AlarmManager non disponible")
                return False

            device_type = self._get_device_type(args.device)
            result = self.call_with_breaker(ctx.alarm_mgr.set_alarm_enabled, serial, device_type, args.id, False)

            if result:
                self.success("✅ Alarme désactivée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la désactivation de l'alarme")
            self.error(f"Erreur: {e}")
            return False

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _get_device_type(self, device_name: str) -> str:
        """Récupère le type d'appareil (placeholder)."""
        # TODO: Récupérer depuis device_mgr
        return "ECHO_DEVICE"

    def _parse_time(self, time_str: str) -> Optional[str]:
        """
        Parse une heure au format HH:MM.

        Args:
            time_str: Chaîne d'heure (ex: "07:30", "18:45")

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

        # Créer un objet time et convertir en ISO 8601
        alarm_time = time(hours, minutes)
        return alarm_time.isoformat()

    def _display_alarms(self, alarms: list) -> None:
        """Affiche les alarmes sous forme de tableau."""
        self.info(f"⏰ {len(alarms)} alarme(s) trouvée(s):\n")

        # Préparer les données du tableau
        table_data = []
        for alarm in alarms:
            alarm_id = alarm.get("id", "N/A")
            label = alarm.get("alarmLabel", "Sans nom") or "Sans nom"
            original_time = alarm.get("originalTime", "N/A")
            original_date = alarm.get("originalDate", "N/A")
            device_serial = alarm.get("deviceSerialNumber", "N/A")
            recurrence_eligible = alarm.get("recurrenceEligible", False)
            alarm_time_ms = alarm.get("alarmTime", 0)

            # Résoudre le nom d'appareil
            device_name = "N/A"
            if device_serial != "N/A" and self.device_mgr:
                try:
                    device = self.device_mgr.find_device_by_serial(device_serial)
                    if device:
                        device_name = device.get("name", device_serial)
                except Exception:
                    device_name = device_serial

            # Déterminer le statut (activé/désactivé)
            enabled = alarm_time_ms > 0  # Si alarmTime > 0, c'est activé
            status_emoji = "✅ Activée" if enabled else "❌ Désactivée"

            # Formater l'heure
            time_display = original_time[:5] if original_time != "N/A" and len(original_time) >= 8 else "N/A"

            # Récurrence
            repeat_text = "Récurrente" if recurrence_eligible else "Une seule fois"

            # Tronquer l'ID pour l'affichage
            short_id = alarm_id.split("-")[-1][:8] if "-" in alarm_id else alarm_id[:8]

            table_data.append(
                [
                    time_display,
                    label,
                    device_name,
                    status_emoji,
                    repeat_text,
                    original_date,
                    short_id,
                ]
            )

        # Afficher le tableau
        table = self.format_table(table_data, ["Heure", "Nom", "Appareil", "Statut", "Répétition", "Date", "ID"])
        print(table)
