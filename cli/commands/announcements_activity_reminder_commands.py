"""
Commandes restantes - Tier 2 (Announcements, Activity, Reminders) - Refactorisé.

Annonces: broadcast, send (direct message)
Activité: list, get (history)  
Rappels: add, list, delete

Chaque commande est une classe BaseCommand indépendante avec CommandAdapter DI.

Auteur: M@nu
Date: 16 octobre 2025
"""

import argparse
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.command_adapter import get_command_adapter


# ============================================================================
# ANNOUNCEMENT COMMANDS
# ============================================================================


class AnnouncementBroadcastCommand(BaseCommand):
    """Envoyer une annonce à tous les appareils."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.notification_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Envoyer une annonce broadcast."""
        try:
            if not hasattr(args, "message") or not args.message:
                self.error("Paramètre requis: --message")
                return False

            self.info(f"📢 Envoi d'une annonce: {args.message[:50]}...")

            if not self.notification_mgr:
                self.notification_mgr = self.adapter.get_manager("NotificationManager")
                if not self.notification_mgr:
                    self.error("NotificationManager non disponible")
                    return False

            result = self.notification_mgr.announce(args.message)

            if result:
                self.success(f"✅ Annonce envoyée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur broadcast")
            self.error(f"Erreur: {e}")
            return False


class AnnouncementSendCommand(BaseCommand):
    """Envoyer un message direct à un appareil."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.notification_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Envoyer un message direct."""
        try:
            if not hasattr(args, "device") or not args.device:
                self.error("Paramètre requis: --device")
                return False

            if not hasattr(args, "message") or not args.message:
                self.error("Paramètre requis: --message")
                return False

            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"💬 Envoi d'un message à '{args.device}'...")

            if not self.notification_mgr:
                self.notification_mgr = self.adapter.get_manager("NotificationManager")
                if not self.notification_mgr:
                    self.error("NotificationManager non disponible")
                    return False

            result = self.notification_mgr.send_message(serial, device_type, args.message)

            if result:
                self.success(f"✅ Message envoyé à '{args.device}'")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur send")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# ACTIVITY COMMANDS
# ============================================================================


class ActivityListCommand(BaseCommand):
    """Lister l'historique d'activité."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.activity_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister l'activité."""
        try:
            self.info("📜 Récupération de l'historique d'activité...")

            if not self.activity_mgr:
                self.activity_mgr = self.adapter.get_manager("ActivityManager")
                if not self.activity_mgr:
                    self.error("ActivityManager non disponible")
                    return False

            limit = getattr(args, "limit", 10)
            activities = self.activity_mgr.get_activities(limit=limit)

            if not activities:
                self.warning("Aucune activité trouvée")
                return True

            if hasattr(args, "json") and args.json:
                self.output(activities, json_mode=True)
            else:
                table_data = [
                    [
                        a.get("timestamp", "N/A"),
                        a.get("device", "N/A"),
                        a.get("type", "N/A"),
                        a.get("description", "N/A")[:40],
                    ]
                    for a in activities
                ]
                table = self.format_table(
                    table_data, ["Timestamp", "Appareil", "Type", "Description"]
                )
                print(table)

            self.success(f"✅ {len(activities)} activité(s) affichée(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


class ActivityGetCommand(BaseCommand):
    """Obtenir les détails d'une activité."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.activity_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Obtenir les détails d'une activité."""
        try:
            if not hasattr(args, "activity_id") or not args.activity_id:
                self.error("Paramètre requis: activity_id")
                return False

            self.info(f"📜 Récupération des détails de l'activité...")

            if not self.activity_mgr:
                self.activity_mgr = self.adapter.get_manager("ActivityManager")
                if not self.activity_mgr:
                    self.error("ActivityManager non disponible")
                    return False

            activity = self.activity_mgr.get_activity(args.activity_id)

            if not activity:
                self.error("Activité non trouvée")
                return False

            if hasattr(args, "json") and args.json:
                self.output(activity, json_mode=True)
            else:
                for key, value in activity.items():
                    print(f"  {key:.<30} {value}")

            self.success("✅ Détails de l'activité affichés")
            return True

        except Exception as e:
            self.logger.exception("Erreur get")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# REMINDER COMMANDS
# ============================================================================


class ReminderAddCommand(BaseCommand):
    """Créer un rappel."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.reminder_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Créer un rappel."""
        try:
            if not hasattr(args, "label") or not args.label:
                self.error("Paramètre requis: --label")
                return False

            if not hasattr(args, "time") or not args.time:
                self.error("Paramètre requis: --time")
                return False

            self.info(f"🔔 Création du rappel: {args.label}...")

            if not self.reminder_mgr:
                self.reminder_mgr = self.adapter.get_manager("ReminderManager")
                if not self.reminder_mgr:
                    self.error("ReminderManager non disponible")
                    return False

            result = self.reminder_mgr.create_reminder(args.label, args.time)

            if result:
                self.success(f"✅ Rappel '{args.label}' créé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur add")
            self.error(f"Erreur: {e}")
            return False


class ReminderListCommand(BaseCommand):
    """Lister les rappels."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.reminder_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister les rappels."""
        try:
            self.info("🔔 Récupération des rappels...")

            if not self.reminder_mgr:
                self.reminder_mgr = self.adapter.get_manager("ReminderManager")
                if not self.reminder_mgr:
                    self.error("ReminderManager non disponible")
                    return False

            reminders = self.reminder_mgr.get_reminders()

            if not reminders:
                self.warning("Aucun rappel trouvé")
                return True

            if hasattr(args, "json") and args.json:
                self.output(reminders, json_mode=True)
            else:
                table_data = [
                    [
                        r.get("label", "N/A"),
                        r.get("time", "N/A"),
                        "🔔 Actif" if r.get("enabled") else "🔇 Inactif",
                    ]
                    for r in reminders
                ]
                table = self.format_table(table_data, ["Label", "Heure", "État"])
                print(table)

            self.success(f"✅ {len(reminders)} rappel(s) trouvé(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


class ReminderDeleteCommand(BaseCommand):
    """Supprimer un rappel."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.reminder_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Supprimer un rappel."""
        try:
            if not hasattr(args, "reminder_id") or not args.reminder_id:
                self.error("Paramètre requis: reminder_id")
                return False

            self.info(f"🔔 Suppression du rappel...")

            if not self.reminder_mgr:
                self.reminder_mgr = self.adapter.get_manager("ReminderManager")
                if not self.reminder_mgr:
                    self.error("ReminderManager non disponible")
                    return False

            result = self.reminder_mgr.delete_reminder(args.reminder_id)

            if result:
                self.success(f"✅ Rappel supprimé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur delete")
            self.error(f"Erreur: {e}")
            return False
