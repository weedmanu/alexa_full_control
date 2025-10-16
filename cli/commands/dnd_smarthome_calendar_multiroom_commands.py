"""
Commandes restantes - Tier 3 (DND, SmartHome, Calendar, Multiroom) - Refactorisé.

DND: get, set, delete (Do Not Disturb)
SmartHome: get, list, control
Calendar: list, get
Multiroom: join, leave

Chaque commande est une classe BaseCommand indépendante avec CommandAdapter DI.

Auteur: M@nu
Date: 16 octobre 2025
"""

import argparse
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.command_adapter import get_command_adapter


# ============================================================================
# DND (DO NOT DISTURB) COMMANDS
# ============================================================================


class DNDGetCommand(BaseCommand):
    """Obtenir l'état du mode Ne pas déranger."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.dnd_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Obtenir l'état DND."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"🔇 Vérification du mode DND sur '{args.device}'...")

            if not self.dnd_mgr:
                self.dnd_mgr = self.adapter.get_manager("DNDManager")
                if not self.dnd_mgr:
                    self.error("DNDManager non disponible")
                    return False

            state = self.dnd_mgr.get_dnd(serial, device_type)

            if state is not None:
                status = "🔇 Activé" if state else "🔊 Désactivé"
                self.success(f"✅ DND: {status}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur get")
            self.error(f"Erreur: {e}")
            return False


class DNDSetCommand(BaseCommand):
    """Activer/désactiver le mode Ne pas déranger."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.dnd_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Définir l'état DND."""
        try:
            if not hasattr(args, "enabled") or args.enabled is None:
                self.error("Paramètre requis: --enabled (true/false)")
                return False

            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            enabled = args.enabled in [True, "true", "True", "1", "on"]
            status = "activation" if enabled else "désactivation"

            self.info(f"🔇 {status.capitalize()} du DND sur '{args.device}'...")

            if not self.dnd_mgr:
                self.dnd_mgr = self.adapter.get_manager("DNDManager")
                if not self.dnd_mgr:
                    self.error("DNDManager non disponible")
                    return False

            result = self.dnd_mgr.set_dnd(serial, device_type, enabled)

            if result:
                self.success(f"✅ DND {status}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur set")
            self.error(f"Erreur: {e}")
            return False


class DNDDeleteCommand(BaseCommand):
    """Réinitialiser le mode Ne pas déranger."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.dnd_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Réinitialiser le DND."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"🔇 Réinitialisation du DND sur '{args.device}'...")

            if not self.dnd_mgr:
                self.dnd_mgr = self.adapter.get_manager("DNDManager")
                if not self.dnd_mgr:
                    self.error("DNDManager non disponible")
                    return False

            result = self.dnd_mgr.delete_dnd(serial, device_type)

            if result:
                self.success(f"✅ DND réinitialisé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur delete")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# SMARTHOME COMMANDS
# ============================================================================


class SmartHomeGetCommand(BaseCommand):
    """Obtenir l'état d'un appareil domotique."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.smarthome_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Obtenir l'état d'un appareil domotique."""
        try:
            if not hasattr(args, "device_id") or not args.device_id:
                self.error("Paramètre requis: device_id")
                return False

            self.info(f"🏠 Récupération de l'état de l'appareil...")

            if not self.smarthome_mgr:
                self.smarthome_mgr = self.adapter.get_manager("SmartHomeManager")
                if not self.smarthome_mgr:
                    self.error("SmartHomeManager non disponible")
                    return False

            state = self.smarthome_mgr.get_device_state(args.device_id)

            if state:
                if hasattr(args, "json") and args.json:
                    self.output(state, json_mode=True)
                else:
                    for key, value in state.items():
                        print(f"  {key:.<20} {value}")
                self.success("✅ État de l'appareil affichéé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur get")
            self.error(f"Erreur: {e}")
            return False


class SmartHomeListCommand(BaseCommand):
    """Lister les appareils domotiques."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.smarthome_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister les appareils domotiques."""
        try:
            self.info("🏠 Récupération de la liste des appareils...")

            if not self.smarthome_mgr:
                self.smarthome_mgr = self.adapter.get_manager("SmartHomeManager")
                if not self.smarthome_mgr:
                    self.error("SmartHomeManager non disponible")
                    return False

            devices = self.smarthome_mgr.get_devices()

            if not devices:
                self.warning("Aucun appareil domotique trouvé")
                return True

            if hasattr(args, "json") and args.json:
                self.output(devices, json_mode=True)
            else:
                table_data = [
                    [
                        d.get("id", "N/A"),
                        d.get("name", "N/A"),
                        d.get("type", "N/A"),
                        "🟢 On" if d.get("state") else "🔴 Off",
                    ]
                    for d in devices
                ]
                table = self.format_table(table_data, ["ID", "Nom", "Type", "État"])
                print(table)

            self.success(f"✅ {len(devices)} appareil(s) trouvé(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


class SmartHomeControlCommand(BaseCommand):
    """Contrôler un appareil domotique."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.smarthome_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Contrôler un appareil domotique."""
        try:
            if not hasattr(args, "device_id") or not args.device_id:
                self.error("Paramètre requis: device_id")
                return False

            if not hasattr(args, "action") or not args.action:
                self.error("Paramètre requis: action (on/off/toggle)")
                return False

            self.info(f"🏠 Contrôle de l'appareil: {args.action}...")

            if not self.smarthome_mgr:
                self.smarthome_mgr = self.adapter.get_manager("SmartHomeManager")
                if not self.smarthome_mgr:
                    self.error("SmartHomeManager non disponible")
                    return False

            result = self.smarthome_mgr.control_device(args.device_id, args.action)

            if result:
                self.success(f"✅ Appareil contrôlé: {args.action}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur control")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# CALENDAR COMMANDS
# ============================================================================


class CalendarListCommand(BaseCommand):
    """Lister les calendriers."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.calendar_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister les calendriers."""
        try:
            self.info("📅 Récupération des calendriers...")

            if not self.calendar_mgr:
                self.calendar_mgr = self.adapter.get_manager("CalendarManager")
                if not self.calendar_mgr:
                    self.error("CalendarManager non disponible")
                    return False

            calendars = self.calendar_mgr.get_calendars()

            if not calendars:
                self.warning("Aucun calendrier trouvé")
                return True

            if hasattr(args, "json") and args.json:
                self.output(calendars, json_mode=True)
            else:
                table_data = [
                    [c.get("id", "N/A"), c.get("name", "N/A")]
                    for c in calendars
                ]
                table = self.format_table(table_data, ["ID", "Nom"])
                print(table)

            self.success(f"✅ {len(calendars)} calendrier(s) trouvé(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


class CalendarGetCommand(BaseCommand):
    """Obtenir les événements d'un calendrier."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.calendar_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Obtenir les événements du calendrier."""
        try:
            if not hasattr(args, "calendar_id") or not args.calendar_id:
                self.error("Paramètre requis: calendar_id")
                return False

            self.info(f"📅 Récupération des événements...")

            if not self.calendar_mgr:
                self.calendar_mgr = self.adapter.get_manager("CalendarManager")
                if not self.calendar_mgr:
                    self.error("CalendarManager non disponible")
                    return False

            events = self.calendar_mgr.get_events(args.calendar_id)

            if not events:
                self.warning("Aucun événement trouvé")
                return True

            if hasattr(args, "json") and args.json:
                self.output(events, json_mode=True)
            else:
                table_data = [
                    [
                        e.get("start", "N/A"),
                        e.get("title", "N/A"),
                        e.get("location", "N/A")[:30],
                    ]
                    for e in events
                ]
                table = self.format_table(table_data, ["Heure", "Titre", "Lieu"])
                print(table)

            self.success(f"✅ {len(events)} événement(s) trouvé(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur get")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# MULTIROOM COMMANDS
# ============================================================================


class MultiRoomJoinCommand(BaseCommand):
    """Joindre un groupe multiroom."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.multiroom_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Joindre un groupe multiroom."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            if not hasattr(args, "group_id") or not args.group_id:
                self.error("Paramètre requis: group_id")
                return False

            self.info(f"🎵 Ajout de '{args.device}' au groupe...")

            if not self.multiroom_mgr:
                self.multiroom_mgr = self.adapter.get_manager("MultiRoomManager")
                if not self.multiroom_mgr:
                    self.error("MultiRoomManager non disponible")
                    return False

            result = self.multiroom_mgr.join_group(serial, args.group_id)

            if result:
                self.success(f"✅ '{args.device}' a rejoint le groupe")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur join")
            self.error(f"Erreur: {e}")
            return False


class MultiRoomLeaveCommand(BaseCommand):
    """Quitter un groupe multiroom."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.multiroom_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Quitter un groupe multiroom."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"🎵 Suppression de '{args.device}' du groupe...")

            if not self.multiroom_mgr:
                self.multiroom_mgr = self.adapter.get_manager("MultiRoomManager")
                if not self.multiroom_mgr:
                    self.error("MultiRoomManager non disponible")
                    return False

            result = self.multiroom_mgr.leave_group(serial)

            if result:
                self.success(f"✅ '{args.device}' a quitté le groupe")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur leave")
            self.error(f"Erreur: {e}")
            return False
