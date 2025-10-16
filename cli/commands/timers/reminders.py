"""
Gestion des rappels Alexa.

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse
from typing import Any, Dict, List

from cli.command_parser import UniversalHelpFormatter
from cli.commands.timers.base import TimeSubCommand


class RemindersCommands(TimeSubCommand):
    """Commandes de gestion des rappels."""

    def create(self, args: argparse.Namespace) -> bool:
        """CrÃ©er un nouveau rappel."""
        try:
            device_name = getattr(args, "device", None)
            if not device_name:
                self.error("L'appareil est requis (-d/--device)")
                return False

            # Validation: soit datetime, soit recurrence+time
            if args.datetime and (getattr(args, "recurrence", None) or getattr(args, "time", None)):
                self.error("Utilisez soit --datetime, soit --recurrence + --time (pas les deux)")
                return False

            if not args.datetime and not (getattr(args, "recurrence", None) and getattr(args, "time", None)):
                self.error("SpÃ©cifiez soit --datetime, soit --recurrence + --time")
                return False

            serial = self.get_device_serial(device_name)
            if not serial:
                return False

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "reminder_mgr", None):
                self.error("ReminderManager non disponible")
                return False

            # CrÃ©er le rappel
            if args.datetime:
                # Rappel ponctuel
                self.info(f"â° CrÃ©ation rappel pour '{device_name}'...")
                self.info(f"   Texte: {args.label}")
                self.info(f"   Date: {args.datetime}")

                result = self.call_with_breaker(ctx.reminder_mgr.create_reminder, serial, args.label, args.datetime)
            else:
                # Rappel rÃ©current
                recurrence = getattr(args, "recurrence", None)
                time_val = getattr(args, "time", None)
                self.info(f"ðŸ” CrÃ©ation rappel rÃ©current pour '{device_name}'...")
                self.info(f"   Texte: {args.label}")
                self.info(f"   RÃ©currence: {recurrence}")
                self.info(f"   Heure: {time_val}")

                result = self.call_with_breaker(
                    ctx.reminder_mgr.create_recurring_reminder,
                    serial,
                    args.label,
                    recurrence,
                    time_val,
                )

            if result:
                self.success("âœ… Rappel crÃ©Ã© avec succÃ¨s")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la crÃ©ation du rappel")
            self.error(f"Erreur: {e}")
            return False

    def list(self, args: argparse.Namespace) -> bool:
        """Lister les rappels."""
        try:
            show_all = getattr(args, "all", False)
            device_name = getattr(args, "device", None)

            if device_name:
                self.info(f"ðŸ“‹ RÃ©cupÃ©ration des rappels pour '{device_name}'...")
                serial = self.get_device_serial(device_name)
                if not serial:
                    return False
            else:
                self.info("ðŸ“‹ RÃ©cupÃ©ration de tous les rappels...")
                serial = None

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "reminder_mgr", None):
                self.error("ReminderManager non disponible")
                return False

            reminders = self.call_with_breaker(ctx.reminder_mgr.list_reminders)

            if not reminders:
                self.warning("Aucun rappel trouvÃ©")
                return True

            # Filtrer les rappels complÃ©tÃ©s si pas --all
            if not show_all:
                reminders = [r for r in reminders if not r.get("completed", False)]

            # Afficher les rappels
            self._display(reminders)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration des rappels")
            self.error(f"Erreur: {e}")
            return False

    def delete(self, args: argparse.Namespace) -> bool:
        """Supprimer un rappel."""
        try:
            force = getattr(args, "force", False)

            # Confirmation si pas --force
            if not force:
                self.warning(f"âš ï¸  Vous allez supprimer le rappel '{args.id}'")
                self.info("Utilisez --force pour supprimer sans confirmation")
                return False

            self.info(f"ðŸ—‘ï¸  Suppression rappel '{args.id}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "reminder_mgr", None):
                self.error("ReminderManager non disponible")
                return False

            result = self.call_with_breaker(ctx.reminder_mgr.delete_reminder, args.id)

            if result:
                self.success(f"âœ… Rappel '{args.id}' supprimÃ©")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression du rappel")
            self.error(f"Erreur: {e}")
            return False

    def complete(self, args: argparse.Namespace) -> bool:
        """Marquer un rappel comme complÃ©tÃ©."""
        try:
            self.info(f"âœ… Marquage rappel '{args.id}' comme complÃ©tÃ©...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "reminder_mgr", None):
                self.error("ReminderManager non disponible")
                return False

            result = self.call_with_breaker(ctx.reminder_mgr.complete_reminder, args.id)

            if result:
                self.success(f"âœ… Rappel '{args.id}' marquÃ© comme complÃ©tÃ©")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors du marquage du rappel")
            self.error(f"Erreur: {e}")
            return False

    def _display(self, reminders: List[Dict[str, Any]]) -> None:
        """Affiche la liste des rappels de maniÃ¨re formatÃ©e."""
        print(f"\nðŸ“‹ Rappels ({len(reminders)}):")
        print("=" * 80)

        # Trier par statut
        active_reminders = [r for r in reminders if not r.get("completed", False)]
        completed_reminders = [r for r in reminders if r.get("completed", False)]

        if active_reminders:
            print("\nðŸ”” Rappels actifs:")
            for reminder in active_reminders:
                self._display_single(reminder)

        if completed_reminders:
            print("\nâœ… Rappels complÃ©tÃ©s:")
            for reminder in completed_reminders:
                self._display_single(reminder)

    def _display_single(self, reminder: Dict[str, Any]) -> None:
        """Affiche un rappel de maniÃ¨re formatÃ©e."""
        reminder_id = reminder.get("id", "N/A")
        label = reminder.get("label", "N/A")
        datetime_str = reminder.get("datetime", "N/A")
        recurrence = reminder.get("recurrence")
        device_name = reminder.get("device_name", "N/A")
        completed = reminder.get("completed", False)

        status = "âœ…" if completed else "ðŸ””"

        print(f"\n{status} {label}")
        print(f"   ID: {reminder_id}")
        print(f"   Appareil: {device_name}")

        if recurrence:
            print(f"   RÃ©currence: {recurrence}")
            print(f"   Heure: {datetime_str}")
        else:
            print(f"   Date: {datetime_str}")

    @staticmethod
    def setup_parsers(subparsers) -> None:
        """
        Configure le sous-parser pour les rappels.

        Args:
            subparsers: Sous-parsers de la catÃ©gorie timer
        """
        # Sous-catÃ©gorie: reminder
        reminder_parser = subparsers.add_parser(
            "reminder",
            help="GÃ©rer les rappels",
            description="CrÃ©er et gÃ©rer les rappels sur Amazon Alexa",
            formatter_class=UniversalHelpFormatter,
        )

        reminder_subparsers = reminder_parser.add_subparsers(
            dest="action",
            title="Actions reminder",
            description="GÃ©rer les rappels sur Amazon Alexa",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: create
        create_parser = reminder_subparsers.add_parser(
            "create",
            help="CrÃ©er un rappel",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        create_parser.add_argument(
            "--label",
            type=str,
            required=True,
            metavar="LABEL",
            help="Ã‰tiquette du rappel",
        )
        create_parser.add_argument(
            "--datetime",
            type=str,
            required=True,
            metavar="DATETIME",
            help="Date et heure (ex: '2025-10-08 14:00', 'demain 15:30')",
        )
        create_parser.add_argument(
            "-d",
            "--device",
            type=str,
            metavar="DEVICE_NAME",
            help="Appareil cible (optionnel, utilise le premier disponible sinon)",
        )

        # Action: list
        list_parser = reminder_subparsers.add_parser(
            "list",
            help="Lister les rappels",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil (optionnel)",
        )

        # Action: delete
        delete_parser = reminder_subparsers.add_parser(
            "delete",
            help="Supprimer un rappel",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        delete_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="REMINDER_ID",
            help="ID du rappel Ã  supprimer",
        )

        # Action: complete
        complete_parser = reminder_subparsers.add_parser(
            "complete",
            help="Marquer un rappel comme terminÃ©",
            description="",
            formatter_class=UniversalHelpFormatter,
        )
        complete_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="REMINDER_ID",
            help="ID du rappel Ã  marquer comme terminÃ©",
        )

