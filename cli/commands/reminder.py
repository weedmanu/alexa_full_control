"""Commande de gestion des rappels Alexa.

Ce module fournit une interface CLI pour gérer les rappels :
- Lister les rappels actifs
- Créer un nouveau rappel
- Supprimer un rappel
- Marquer un rappel comme complété
"""

import argparse
from datetime import datetime

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter, ActionHelpFormatter
from cli.help_texts.reminder_help import (
    REMINDER_DESCRIPTION,
    LIST_HELP,
    CREATE_HELP,
    DELETE_HELP,
    COMPLETE_HELP,
)


class ReminderCommand(BaseCommand):
    """
    Commande pour gérer les rappels Alexa.

    Les rappels permettent de programmer des notifications vocales
    à des dates/heures spécifiques ou récurrentes.

    Exemples:
        >>> # Lister tous les rappels
        >>> alexa reminder list

        >>> # Créer un rappel
        >>> alexa reminder create -d "Salon Echo" --label "Réunion" --datetime "2025-10-08 14:00"

        >>> # Créer un rappel récurrent
        >>> alexa reminder create -d "Salon Echo" --label "Médicament" --recurrence daily --time "09:00"

        >>> # Supprimer un rappel
        >>> alexa reminder delete --id "abc123"

        >>> # Marquer comme complété
        >>> alexa reminder complete --id "abc123"
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "reminder"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "Gérer les rappels"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande reminder.

        Args:
            parser: Parser à configurer
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Définir un usage plus détaillé
        parser.usage = "alexa [OPTIONS_GLOBALES] reminder <ACTION> [OPTIONS_ACTION]"

        # Description réorganisée dans l'ordre demandé : Titre → Usage → Options → Actions → Options d'action → Exemples
        parser.description = REMINDER_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: list
        list_parser = subparsers.add_parser("list", help="Lister rappels", description=LIST_HELP, formatter_class=ActionHelpFormatter, add_help=False)
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil (optionnel, tous les appareils si non spécifié)",
        )
        list_parser.add_argument(
            "--active-only",
            action="store_true",
            help="Afficher uniquement les rappels actifs (non complétés)",
        )
        list_parser.add_argument(
            "--all", action="store_true", help="Afficher tous les rappels (incluant les complétés)"
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create", help="Créer rappel", description=CREATE_HELP, formatter_class=ActionHelpFormatter, add_help=False
        )
        create_parser.add_argument(
            "--label", type=str, required=True, metavar="TEXT", help="Texte du rappel"
        )
        create_parser.add_argument(
            "--datetime",
            type=str,
            metavar="YYYY-MM-DD HH:MM",
            help="Date et heure du rappel (format: 2025-10-08 14:00)",
        )
        create_parser.add_argument(
            "--recurrence",
            type=str,
            choices=["daily", "weekly", "monthly"],
            help="Récurrence du rappel (daily, weekly, monthly)",
        )
        create_parser.add_argument(
            "--time", type=str, metavar="HH:MM", help="Heure du rappel récurrent (format: 09:00)"
        )

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete", help="Supprimer rappel", description=DELETE_HELP, formatter_class=ActionHelpFormatter, add_help=False
        )
        delete_parser.add_argument(
            "--id", type=str, required=True, metavar="REMINDER_ID", help="ID du rappel à supprimer"
        )
        delete_parser.add_argument(
            "--force", action="store_true", help="Supprimer sans confirmation"
        )

        # Action: complete
        complete_parser = subparsers.add_parser(
            "complete", help="Marquer complété", description=COMPLETE_HELP, formatter_class=ActionHelpFormatter, add_help=False
        )
        complete_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="REMINDER_ID",
            help="ID du rappel à marquer comme complété",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande reminder.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "list":
            return self._list_reminders(args)
        elif args.action == "create":
            return self._create_reminder(args)
        elif args.action == "delete":
            return self._delete_reminder(args)
        elif args.action == "complete":
            return self._complete_reminder(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _list_reminders(self, args: argparse.Namespace) -> bool:
        """Lister les rappels."""
        try:
            show_all = getattr(args, "all", False)
            active_only = getattr(args, "active_only", False)
            device_name = getattr(args, "device", None)

            if device_name:
                self.info(f"📋 Récupération des rappels pour '{device_name}'...")
                serial = self.get_device_serial(device_name)
                if not serial:
                    return False
            else:
                self.info("📋 Récupération de tous les rappels...")
                serial = None

            if not self.context.reminder_mgr:
                self.error("ReminderManager non disponible")
                return False

            reminders = self.call_with_breaker(self.context.reminder_mgr.get_reminders, serial)

            if not reminders:
                self.warning("Aucun rappel trouvé")
                return True

            # Filtrage selon les options
            if active_only:
                # Afficher uniquement les rappels actifs (non complétés)
                reminders = [r for r in reminders if not r.get("completed", False)]
            elif not show_all:
                # Par défaut, afficher uniquement les actifs (comportement existant)
                reminders = [r for r in reminders if not r.get("completed", False)]

            if not reminders:
                if active_only:
                    self.warning("Aucun rappel actif trouvé")
                else:
                    self.warning("Aucun rappel trouvé")
                return True

            # Afficher les rappels
            self._display_reminders(reminders)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération des rappels")
            self.error(f"Erreur: {e}")
            return False

    def _create_reminder(self, args: argparse.Namespace) -> bool:
        """Créer un nouveau rappel."""
        try:
            device_name = getattr(args, "device", None)
            if not device_name:
                self.error("L'appareil est requis (-d/--device)")
                return False

            # Validation: soit datetime, soit recurrence+time
            if args.datetime and (args.recurrence or args.time):
                self.error("Utilisez soit --datetime, soit --recurrence + --time (pas les deux)")
                return False

            if not args.datetime and not (args.recurrence and args.time):
                self.error("Spécifiez soit --datetime, soit --recurrence + --time")
                return False

            serial = self.get_device_serial(device_name)
            if not serial:
                return False

            if not self.context.reminder_mgr:
                self.error("ReminderManager non disponible")
                return False

            # Créer le rappel
            if args.datetime:
                # Rappel ponctuel
                self.info(f"⏰ Création rappel pour '{device_name}'...")
                self.info(f"   Texte: {args.label}")
                self.info(f"   Date: {args.datetime}")

                result = self.call_with_breaker(
                    self.context.reminder_mgr.create_reminder, serial, args.label, args.datetime
                )
            else:
                # Rappel récurrent
                self.info(f"🔁 Création rappel récurrent pour '{device_name}'...")
                self.info(f"   Texte: {args.label}")
                self.info(f"   Récurrence: {args.recurrence}")
                self.info(f"   Heure: {args.time}")

                result = self.call_with_breaker(
                    self.context.reminder_mgr.create_recurring_reminder,
                    serial,
                    args.label,
                    args.recurrence,
                    args.time,
                )

            if result:
                self.success("✅ Rappel créé avec succès")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la création du rappel")
            self.error(f"Erreur: {e}")
            return False

    def _delete_reminder(self, args: argparse.Namespace) -> bool:
        """Supprimer un rappel."""
        try:
            force = getattr(args, "force", False)

            # Confirmation si pas --force
            if not force:
                self.warning(f"⚠️  Vous allez supprimer le rappel '{args.id}'")
                self.info("Utilisez --force pour supprimer sans confirmation")
                return False

            self.info(f"🗑️  Suppression rappel '{args.id}'...")

            if not self.context.reminder_mgr:
                self.error("ReminderManager non disponible")
                return False

            result = self.call_with_breaker(self.context.reminder_mgr.delete_reminder, args.id)

            if result:
                self.success(f"✅ Rappel '{args.id}' supprimé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression du rappel")
            self.error(f"Erreur: {e}")
            return False

    def _complete_reminder(self, args: argparse.Namespace) -> bool:
        """Marquer un rappel comme complété."""
        try:
            self.info(f"✅ Marquage rappel '{args.id}' comme complété...")

            if not self.context.reminder_mgr:
                self.error("ReminderManager non disponible")
                return False

            result = self.call_with_breaker(self.context.reminder_mgr.complete_reminder, args.id)

            if result:
                self.success(f"✅ Rappel '{args.id}' marqué comme complété")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors du marquage du rappel")
            self.error(f"Erreur: {e}")
            return False

    def _display_reminders(self, reminders: list) -> None:
        """Affiche les rappels sous forme de tableau."""
        self.info(f"📋 {len(reminders)} rappel(s) trouvé(s):\n")

        # Préparer les données du tableau
        table_data = []
        for reminder in reminders:
            reminder_id = reminder.get("id", "N/A")
            label = reminder.get("alarmLabel", "Sans nom") or "Sans nom"
            device_serial = reminder.get("deviceSerialNumber", "N/A")
            original_time = reminder.get("originalTime", "N/A")
            original_date = reminder.get("originalDate", "N/A")
            alarm_time_ms = reminder.get("alarmTime", 0)
            recurrence = reminder.get("recurrence", None)
            follow_up = reminder.get("followUpMetadata", {})
            completed = follow_up.get("followUpStatus") == "COMPLETED"

            # Résoudre le nom d'appareil
            device_name = "N/A"
            if device_serial != "N/A" and self.context.device_mgr:
                try:
                    device = self.context.device_mgr.find_device_by_serial(device_serial)
                    if device:
                        device_name = device.get("name", device_serial)
                except Exception:
                    device_name = device_serial

            # Déterminer le statut
            status_emoji = "✅ Complété" if completed else "🔔 Actif"

            # Formater la date/heure
            if original_date != "N/A" and original_time != "N/A":
                if len(original_time) >= 8:
                    time_display = original_time[:5]  # HH:MM
                else:
                    time_display = original_time
                datetime_display = f"{original_date} {time_display}"
            elif alarm_time_ms > 0:
                # Convertir timestamp en datetime
                dt = datetime.fromtimestamp(alarm_time_ms / 1000)
                datetime_display = dt.strftime("%Y-%m-%d %H:%M")
            else:
                datetime_display = "N/A"

            # Récurrence
            if recurrence:
                repeat_text = f"Récurrent ({recurrence})"
            else:
                repeat_text = "Une seule fois"

            # Tronquer l'ID pour l'affichage
            short_id = reminder_id.split("-")[-1][:8] if "-" in reminder_id else reminder_id[:8]

            table_data.append(
                [label, device_name, datetime_display, status_emoji, repeat_text, short_id]
            )

        # Afficher le tableau
        table = self.format_table(
            table_data, ["Nom", "Appareil", "Date/Heure", "Statut", "Répétition", "ID"]
        )
        print(table)
