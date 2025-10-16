"""
Commandes de gestion des appareils, routines et alarmes - Refactorisé.

Appareils: list, info
Routines: list, execute, create (using NEW RoutineManager)
Alarmes: add, list, delete

Chaque commande est une classe BaseCommand indépendante avec CommandAdapter DI.

Auteur: M@nu
Date: 16 octobre 2025
"""

import argparse
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.command_adapter import get_command_adapter
from data.device_family_mapping import get_device_display_name


# ============================================================================
# DEVICE LIST COMMAND
# ============================================================================


class DeviceListCommand(BaseCommand):
    """Lister tous les appareils Alexa."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.device_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister les appareils."""
        try:
            self.info("📱 Récupération des appareils...")

            if not self.device_mgr:
                self.device_mgr = self.adapter.get_manager("DeviceManager")
                if not self.device_mgr:
                    self.error("DeviceManager non disponible")
                    return False

            devices = self.device_mgr.get_devices()

            if not devices:
                self.warning("Aucun appareil trouvé")
                return True

            # Filtrer si demandé
            if hasattr(args, "filter") and args.filter:
                devices = [d for d in devices if args.filter.lower() in d.get("accountName", "").lower()]

            # Online only?
            if hasattr(args, "online_only") and args.online_only:
                devices = [d for d in devices if d.get("online")]

            # Affichage
            if hasattr(args, "json") and args.json:
                self.output(devices, json_mode=True)
            else:
                table_data = [
                    [
                        d.get("accountName", "N/A"),
                        get_device_display_name(
                            d.get("deviceFamily", "STANDARD"),
                            d.get("deviceType", "ECHO")
                        ),
                        "🟢 En ligne" if d.get("online") else "🔴 Hors ligne",
                    ]
                    for d in devices
                ]
                table = self.format_table(table_data, ["Appareil", "Type", "État"])
                print(table)

            self.success(f"✅ {len(devices)} appareil(s) trouvé(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# DEVICE INFO COMMAND
# ============================================================================


class DeviceInfoCommand(BaseCommand):
    """Informations détaillées sur un appareil."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.device_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Afficher infos détaillées d'un appareil."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            self.info(f"📱 Récupération des informations de '{args.device}'...")

            if not self.device_mgr:
                self.device_mgr = self.adapter.get_manager("DeviceManager")
                if not self.device_mgr:
                    self.error("DeviceManager non disponible")
                    return False

            devices = self.device_mgr.get_devices()
            device = next((d for d in devices if d.get("accountName") == args.device), None)

            if not device:
                self.error(f"Appareil '{args.device}' non trouvé")
                return False

            if hasattr(args, "json") and args.json:
                self.output(device, json_mode=True)
            else:
                # Format readable
                info_items = [
                    ("Nom", device.get("accountName", "N/A")),
                    ("Type", get_device_display_name(device.get("deviceFamily", "STANDARD"), device.get("deviceType", "ECHO"))),
                    ("Serial", device.get("serialNumber", "N/A")),
                    ("État", "🟢 En ligne" if device.get("online") else "🔴 Hors ligne"),
                    ("WiFi", device.get("wifiAddress", "N/A")),
                    ("Logiciel", device.get("softwareVersion", "N/A")),
                ]
                for label, value in info_items:
                    print(f"  {label:.<20} {value}")

            self.success(f"✅ Infos de '{args.device}' affichées")
            return True

        except Exception as e:
            self.logger.exception("Erreur info")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# ROUTINE LIST COMMAND
# ============================================================================


class RoutineListCommand(BaseCommand):
    """Lister les routines disponibles."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.routine_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister les routines."""
        try:
            self.info("🎯 Récupération des routines...")

            if not self.routine_mgr:
                self.routine_mgr = self.adapter.get_manager("RoutineManager")
                if not self.routine_mgr:
                    self.error("RoutineManager non disponible")
                    return False

            routines = self.routine_mgr.get_routines()

            if not routines:
                self.warning("Aucune routine trouvée")
                return True

            # Filtrer si demandé
            if hasattr(args, "filter") and args.filter:
                routines = self.routine_mgr.search(name=args.filter)

            if hasattr(args, "json") and args.json:
                self.output(routines, json_mode=True)
            else:
                table_data = [
                    [
                        r.get("name", "N/A"),
                        r.get("description", "N/A")[:50],
                        "🟢 Active" if r.get("enabled") else "🔴 Désactivée",
                    ]
                    for r in routines
                ]
                table = self.format_table(table_data, ["Routine", "Description", "État"])
                print(table)

            self.success(f"✅ {len(routines)} routine(s) trouvée(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# ROUTINE EXECUTE COMMAND
# ============================================================================


class RoutineExecuteCommand(BaseCommand):
    """Exécuter une routine."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.routine_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Exécuter une routine."""
        try:
            if not hasattr(args, "routine_id") or not args.routine_id:
                self.error("Paramètre requis: routine_id")
                return False

            self.info(f"🎯 Exécution de la routine '{args.routine_id}'...")

            if not self.routine_mgr:
                self.routine_mgr = self.adapter.get_manager("RoutineManager")
                if not self.routine_mgr:
                    self.error("RoutineManager non disponible")
                    return False

            result = self.routine_mgr.execute_routine(args.routine_id)

            if result:
                self.success(f"✅ Routine '{args.routine_id}' exécutée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur execute")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# ROUTINE CREATE COMMAND
# ============================================================================


class RoutineCreateCommand(BaseCommand):
    """Créer une nouvelle routine."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.routine_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Créer une routine."""
        try:
            if not hasattr(args, "name") or not args.name:
                self.error("Paramètre requis: --name")
                return False

            description = getattr(args, "description", "Routine créée via CLI")
            actions = getattr(args, "actions", [])

            self.info(f"🎯 Création de la routine '{args.name}'...")

            if not self.routine_mgr:
                self.routine_mgr = self.adapter.get_manager("RoutineManager")
                if not self.routine_mgr:
                    self.error("RoutineManager non disponible")
                    return False

            result = self.routine_mgr.create_routine(args.name, actions, description)

            if result:
                self.success(f"✅ Routine '{args.name}' créée avec succès")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur create")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# ALARM ADD COMMAND
# ============================================================================


class AlarmAddCommand(BaseCommand):
    """Ajouter une alarme."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.alarm_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Ajouter une alarme."""
        try:
            if not hasattr(args, "device") or not args.device:
                self.error("Paramètre requis: --device")
                return False

            if not hasattr(args, "time") or not args.time:
                self.error("Paramètre requis: --time (HH:MM)")
                return False

            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            label = getattr(args, "label", "")

            self.info(f"🔔 Création d'une alarme sur '{args.device}'...")

            if not self.alarm_mgr:
                self.alarm_mgr = self.adapter.get_manager("AlarmManager")
                if not self.alarm_mgr:
                    self.error("AlarmManager non disponible")
                    return False

            result = self.alarm_mgr.create_alarm(serial, device_type, args.time, label)

            if result:
                self.success(f"✅ Alarme créée sur '{args.device}' pour {args.time}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur add")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# ALARM LIST COMMAND
# ============================================================================


class AlarmListCommand(BaseCommand):
    """Lister les alarmes."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.alarm_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister les alarmes."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"🔔 Récupération des alarmes sur '{args.device}'...")

            if not self.alarm_mgr:
                self.alarm_mgr = self.adapter.get_manager("AlarmManager")
                if not self.alarm_mgr:
                    self.error("AlarmManager non disponible")
                    return False

            alarms = self.alarm_mgr.get_alarms(serial, device_type)

            if not alarms:
                self.warning("Aucune alarme trouvée")
                return True

            if hasattr(args, "json") and args.json:
                self.output(alarms, json_mode=True)
            else:
                table_data = [
                    [
                        a.get("time", "N/A"),
                        a.get("label", "N/A"),
                        "🔔 Active" if a.get("enabled") else "🔇 Désactivée",
                    ]
                    for a in alarms
                ]
                table = self.format_table(table_data, ["Heure", "Label", "État"])
                print(table)

            self.success(f"✅ {len(alarms)} alarme(s) trouvée(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# ALARM DELETE COMMAND
# ============================================================================


class AlarmDeleteCommand(BaseCommand):
    """Supprimer une alarme."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.alarm_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Supprimer une alarme."""
        try:
            if not hasattr(args, "alarm_id") or not args.alarm_id:
                self.error("Paramètre requis: alarm_id")
                return False

            self.info(f"🔔 Suppression de l'alarme '{args.alarm_id}'...")

            if not self.alarm_mgr:
                self.alarm_mgr = self.adapter.get_manager("AlarmManager")
                if not self.alarm_mgr:
                    self.error("AlarmManager non disponible")
                    return False

            result = self.alarm_mgr.delete_alarm(args.alarm_id)

            if result:
                self.success(f"✅ Alarme '{args.alarm_id}' supprimée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur delete")
            self.error(f"Erreur: {e}")
            return False
