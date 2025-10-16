"""
Commandes de contrÃ´le des appareils Smart Home gÃ©nÃ©riques.

Ce module gÃ¨re le contrÃ´le des appareils intelligents connectÃ©s:
- list: Lister tous les appareils
- info: Informations dÃ©taillÃ©es
- control: Allumer/Ã©teindre un appareil
- lock: Verrouiller une serrure
- unlock: DÃ©verrouiller une serrure
- status: Ã‰tat des appareils

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import json
from typing import Any, Dict, List

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter


# Constantes de description simplifiÃ©es
SMARTHOME_DESCRIPTION = "ContrÃ´ler les appareils Smart Home"
CONTROL_HELP = "ContrÃ´ler un appareil (on/off)"
INFO_HELP = "Informations dÃ©taillÃ©es sur un appareil"
LIST_HELP = "Lister tous les appareils"
LOCK_HELP = "Verrouiller une serrure"
STATUS_HELP = "Ã‰tat des appareils"
UNLOCK_HELP = "DÃ©verrouiller une serrure"


class SmartHomeCommand(BaseCommand):
    """
    Commande de contrÃ´le des appareils Smart Home.

    GÃ¨re list, info, control, lock, unlock, status.

    Actions:
        - list: Lister tous les appareils intelligents
        - info: Informations dÃ©taillÃ©es sur un appareil
        - control: Allumer/Ã©teindre un appareil
        - lock: Verrouiller une serrure connectÃ©e
        - unlock: DÃ©verrouiller une serrure
        - status: Ã‰tat actuel des appareils

    Example:
        >>> alexa smarthome list
        >>> alexa smarthome info --entity switch.cuisine
        >>> alexa smarthome control --entity plug.salon --action on
        >>> alexa smarthome lock --entity lock.entree
        >>> alexa smarthome unlock --entity lock.entree --code 1234
        >>> alexa smarthome status --entity switch.garage
    """

    # Types d'appareils supportÃ©s
    DEVICE_TYPES = {
        "switch": "ðŸ”Œ Interrupteur",
        "plug": "ðŸ”Œ Prise",
        "lock": "ðŸ”’ Serrure",
        "sensor": "ðŸ“¡ Capteur",
        "camera": "ðŸ“· CamÃ©ra",
        "fan": "ðŸ’¨ Ventilateur",
        "blind": "ðŸªŸ Store",
        "garage": "ðŸš— Garage",
        "valve": "ðŸš° Valve",
        "other": "ðŸ“¦ Autre",
    }

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes smarthome.

        Args:
            parser: Sous-parser pour la catÃ©gorie 'smarthome'
        """
        # Utiliser le formatter universel pour l'ordre exact demandÃ©
        parser.formatter_class = UniversalHelpFormatter

        # DÃ©finir un usage plus dÃ©taillÃ©
        parser.usage = "alexa [OPTIONS_GLOBALES] smarthome <ACTION> [OPTIONS_ACTION]"

        # Description rÃ©organisÃ©e : utiliser la constante partagÃ©e
        parser.description = SMARTHOME_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Lister les appareils",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        list_parser.add_argument("--filter", type=str, metavar="KEYWORD", help="Filtrer par nom ou type")
        list_parser.add_argument(
            "--type",
            type=str,
            choices=list(SmartHomeCommand.DEVICE_TYPES.keys()),
            help=f"Filtrer par type: {', '.join(SmartHomeCommand.DEVICE_TYPES.keys())}",
        )

        # Action: info
        info_parser = subparsers.add_parser(
            "info",
            help="Informations dÃ©taillÃ©es",
            description=INFO_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        info_parser.add_argument(
            "--entity",
            type=str,
            required=True,
            metavar="ENTITY_ID",
            help="ID de l'entitÃ© (ex: switch.salon, lock.entree)",
        )

        # Action: control
        control_parser = subparsers.add_parser(
            "control",
            help="Allumer/Ã©teindre",
            description=CONTROL_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        control_parser.add_argument("--entity", type=str, required=True, metavar="ENTITY_ID", help="ID de l'entitÃ©")
        control_parser.add_argument(
            "--operation",
            type=str,
            required=True,
            choices=["on", "off", "toggle"],
            help="OpÃ©ration: on, off ou toggle",
        )

        # Action: lock
        lock_parser = subparsers.add_parser(
            "lock",
            help="Verrouiller",
            description=LOCK_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        lock_parser.add_argument(
            "--entity",
            type=str,
            required=True,
            metavar="ENTITY_ID",
            help="ID de l'entitÃ© serrure (ex: lock.entree)",
        )
        lock_parser.add_argument("--code", type=str, metavar="CODE", help="Code de sÃ©curitÃ© (optionnel)")

        # Action: unlock
        unlock_parser = subparsers.add_parser(
            "unlock",
            help="DÃ©verrouiller",
            description=UNLOCK_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        unlock_parser.add_argument(
            "--entity", type=str, required=True, metavar="ENTITY_ID", help="ID de l'entitÃ© serrure"
        )
        unlock_parser.add_argument("--code", type=str, required=True, metavar="CODE", help="Code de sÃ©curitÃ©")

        # Action: status
        status_parser = subparsers.add_parser(
            "status",
            help="Ã‰tat actuel",
            description=STATUS_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        status_parser.add_argument("--entity", type=str, required=True, metavar="ENTITY_ID", help="ID de l'entitÃ©")

    def execute(self, args: argparse.Namespace) -> bool:
        """
        ExÃ©cute la commande smarthome.

        Args:
            args: Arguments parsÃ©s

        Returns:
            True si succÃ¨s, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "list":
            return self._list_devices(args)
        elif args.action == "info":
            return self._show_info(args)
        elif args.action == "control":
            return self._control_device(args)
        elif args.action == "lock":
            return self._lock_device(args)
        elif args.action == "unlock":
            return self._unlock_device(args)
        elif args.action == "status":
            return self._show_status(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _list_devices(self, args: argparse.Namespace) -> bool:
        """Lister les appareils."""
        try:
            self.info("ðŸ  RÃ©cupÃ©ration des appareils Smart Home...")

            ctx = self.require_context()
            device_ctrl = getattr(ctx, "device_ctrl", None)
            if not device_ctrl:
                self.error("DeviceController non disponible")
                return False

            # VÃ©rifier si les donnÃ©es smart home sont en cache
            devices = device_ctrl.get_smart_home_devices()

            # Si pas de donnÃ©es en cache, dÃ©clencher le chargement lazy
            sync_service = getattr(ctx, "sync_service", None)
            if not devices and sync_service:
                self.info("ðŸ”„ Chargement lazy des appareils Smart Home...")
                devices = sync_service.get_smart_home_devices()

            if devices:
                # Filtrer par type
                if hasattr(args, "type") and args.type:
                    devices = [d for d in devices if d.get("type", "").lower() == args.type.lower()]

                # Filtrer par nom
                if hasattr(args, "filter") and args.filter:
                    devices = [
                        d
                        for d in devices
                        if args.filter.lower() in d.get("name", "").lower()
                        or args.filter.lower() in d.get("type", "").lower()
                    ]

                if not devices:
                    self.warning("Aucun appareil trouvÃ© avec ces critÃ¨res")
                    return True

                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(devices, indent=2, ensure_ascii=False))
                else:
                    self._display_devices(devices)

                return True

            self.warning("Aucun appareil trouvÃ©")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la liste des appareils")
            self.error(f"Erreur: {e}")
            return False

    def _show_info(self, args: argparse.Namespace) -> bool:
        """Afficher les informations."""
        try:
            self.info(f"ðŸ“‹ Informations de '{args.entity}'...")

            ctx = self.require_context()
            device_ctrl = getattr(ctx, "device_ctrl", None)
            if not device_ctrl:
                self.error("DeviceController non disponible")
                return False

            info = self.call_with_breaker(device_ctrl.get_device_info, args.entity)

            if info:
                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(info, indent=2, ensure_ascii=False))
                else:
                    self._display_info(info)

                return True

            self.error(f"Appareil '{args.entity}' non trouvÃ©")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration des informations")
            self.error(f"Erreur: {e}")
            return False

    def _control_device(self, args: argparse.Namespace) -> bool:
        """ContrÃ´ler un appareil."""
        try:
            action_text = {
                "on": "ðŸŸ¢ Allumage",
                "off": "ðŸ”´ Extinction",
                "toggle": "ðŸ”„ Basculement",
            }.get(args.operation, args.operation)

            self.info(f"{action_text} de '{args.entity}'...")

            ctx = self.require_context()
            device_ctrl = getattr(ctx, "device_ctrl", None)
            if not device_ctrl:
                self.error("DeviceController non disponible")
                return False

            if args.operation == "on":
                result = self.call_with_breaker(device_ctrl.turn_on, args.entity)
            elif args.operation == "off":
                result = self.call_with_breaker(device_ctrl.turn_off, args.entity)
            else:  # toggle
                result = self.call_with_breaker(device_ctrl.toggle, args.entity)

            if result:
                self.success(f"âœ… {action_text} effectuÃ©")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors du contrÃ´le de l'appareil")
            self.error(f"Erreur: {e}")
            return False

    def _lock_device(self, args: argparse.Namespace) -> bool:
        """Verrouiller une serrure."""
        try:
            self.info(f"ðŸ”’ Verrouillage de '{args.entity}'...")

            ctx = self.require_context()
            device_ctrl = getattr(ctx, "device_ctrl", None)
            if not device_ctrl:
                self.error("DeviceController non disponible")
                return False

            code = getattr(args, "code", None)

            result = self.call_with_breaker(device_ctrl.lock, args.entity, code)

            if result:
                self.success("âœ… Serrure verrouillÃ©e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors du verrouillage")
            self.error(f"Erreur: {e}")
            return False

    def _unlock_device(self, args: argparse.Namespace) -> bool:
        """DÃ©verrouiller une serrure."""
        try:
            self.info(f"ðŸ”“ DÃ©verrouillage de '{args.entity}'...")

            ctx = self.require_context()
            device_ctrl = getattr(ctx, "device_ctrl", None)
            if not device_ctrl:
                self.error("DeviceController non disponible")
                return False

            if not args.code:
                self.error("Un code de sÃ©curitÃ© est requis pour dÃ©verrouiller")
                return False

            result = self.call_with_breaker(device_ctrl.unlock, args.entity, args.code)

            if result:
                self.success("âœ… Serrure dÃ©verrouillÃ©e")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors du dÃ©verrouillage")
            self.error(f"Erreur: {e}")
            return False

    def _show_status(self, args: argparse.Namespace) -> bool:
        """Afficher l'Ã©tat."""
        try:
            self.info(f"ðŸ“Š Ã‰tat de '{args.entity}'...")

            ctx = self.require_context()
            device_ctrl = getattr(ctx, "device_ctrl", None)
            if not device_ctrl:
                self.error("DeviceController non disponible")
                return False

            status = self.call_with_breaker(device_ctrl.get_status, args.entity)

            if status:
                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(status, indent=2, ensure_ascii=False))
                else:
                    self._display_status(status)

                return True

            self.error(f"Impossible de rÃ©cupÃ©rer l'Ã©tat de '{args.entity}'")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration de l'Ã©tat")
            self.error(f"Erreur: {e}")
            return False

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _display_devices(self, devices: List[Dict[str, Any]]) -> None:
        """Affiche les appareils."""
        print(f"\nðŸ  {len(devices)} appareil(s) Smart Home:\n")

        # Grouper par type
        from typing import Dict, List

        by_type: Dict[str, List[dict]] = {}
        for device in devices:
            device_type = self._determine_device_type(device)
            if device_type not in by_type:
                by_type[device_type] = []
            by_type[device_type].append(device)

        for device_type, devices_list in sorted(by_type.items()):
            type_icon = self._get_device_icon(device_type)
            type_name = self.DEVICE_TYPES.get(device_type, device_type.capitalize())

            print(f"{type_icon} {type_name} ({len(devices_list)}):")

            for device in devices_list:
                device_id = device.get("id", "N/A")
                name = device.get("displayName", "Unknown")
                description = device.get("description", "")
                availability = device.get("availability", "UNKNOWN")

                # DÃ©terminer l'Ã©tat basÃ© sur la disponibilitÃ©
                state_icon = "ðŸŸ¢" if availability == "AVAILABLE" else "ðŸ”´"
                state_text = "Disponible" if availability == "AVAILABLE" else "Indisponible"

                print(f"  {state_icon} {name}")
                if description and description != name:
                    print(f"     Description: {description}")
                print(f"     ID: {device_id}")
                print(f"     Ã‰tat: {state_text}")

                # Afficher les propriÃ©tÃ©s supportÃ©es si pertinentes
                supported_props = device.get("supportedProperties", [])
                if supported_props:
                    # Filtrer les propriÃ©tÃ©s importantes
                    important_props = [p for p in supported_props if not p.startswith("Alexa.Operation.")][
                        :3
                    ]  # Limiter Ã  3
                    if important_props:
                        print(f"     Actions: {', '.join(important_props)}")
                print()

    def _determine_device_type(self, device: Dict[str, Any]) -> str:
        """DÃ©termine le type d'appareil basÃ© sur ses propriÃ©tÃ©s."""
        provider_data = device.get("providerData", {})
        category = provider_data.get("categoryType", "").upper()
        device_type = provider_data.get("deviceType", "").upper()
        supported_props = device.get("supportedProperties", [])

        # VÃ©rifier les propriÃ©tÃ©s pour dÃ©terminer le type
        props_str = " ".join(supported_props).upper()

        # Logique de dÃ©termination du type
        if "LOCK" in category or "LOCK" in device_type:
            return "lock"
        elif "CAMERA" in device_type or "CAMERA" in category:
            return "camera"
        elif "THERMOSTAT" in category or "TEMPERATURE" in props_str:
            return "thermostat"
        elif "LIGHT" in category or "BRIGHTNESS" in props_str or "COLOR" in props_str:
            return "light"
        elif "PLUG" in category or "SWITCH" in category or "turnOn" in supported_props:
            return "plug"
        elif "FAN" in category or "SPEED" in props_str:
            return "fan"
        elif "BLIND" in category or "PERCENTAGE" in props_str:
            return "blind"
        elif "GARAGE" in category:
            return "garage"
        elif "VALVE" in category:
            return "valve"
        elif "SENSOR" in category or device_type == "SENSOR":
            return "sensor"
        elif category == "GROUP":
            return "group"
        else:
            return "other"

    def _display_info(self, info: Dict[str, Any]) -> None:
        """Affiche les informations dÃ©taillÃ©es."""
        print("\nðŸ“‹ Informations dÃ©taillÃ©es:\n")

        device_type = info.get("type", "unknown").lower()
        type_icon = self._get_device_icon(device_type)
        type_name = self.DEVICE_TYPES.get(device_type, device_type.capitalize())

        print(f"  Type: {type_icon} {type_name}")
        print(f"  Nom: {info.get('name', 'N/A')}")
        print(f"  ID: {info.get('entity_id', 'N/A')}")
        print(f"  Ã‰tat: {info.get('state', 'N/A')}")

        # Attributs supplÃ©mentaires
        if "friendly_name" in info:
            print(f"  Nom convivial: {info['friendly_name']}")

        if "manufacturer" in info:
            print(f"  Fabricant: {info['manufacturer']}")

        if "model" in info:
            print(f"  ModÃ¨le: {info['model']}")

        if "battery_level" in info:
            print(f"  Batterie: {info['battery_level']}%")

        if "last_updated" in info:
            print(f"  DerniÃ¨re mise Ã  jour: {info['last_updated']}")

    def _display_status(self, status: Dict[str, Any]) -> None:
        """Affiche l'Ã©tat."""
        print("\nðŸ“Š Ã‰tat actuel:\n")

        state = status.get("state", "unknown")
        state_icon = "ðŸŸ¢" if state == "on" else "âš«"

        print(f"  Ã‰tat: {state_icon} {state}")

        if "locked" in status:
            lock_icon = "ðŸ”’" if status["locked"] else "ðŸ”“"
            lock_text = "VerrouillÃ©" if status["locked"] else "DÃ©verrouillÃ©"
            print(f"  Verrouillage: {lock_icon} {lock_text}")

        if "position" in status:
            print(f"  Position: {status['position']}%")

        if "speed" in status:
            print(f"  Vitesse: {status['speed']}")

        if "temperature" in status:
            print(f"  TempÃ©rature: {status['temperature']}Â°C")

        if "humidity" in status:
            print(f"  HumiditÃ©: {status['humidity']}%")

    def _get_device_icon(self, device_type: str) -> str:
        """Retourne l'icÃ´ne pour un type d'appareil."""
        icons = {
            "switch": "ðŸ”Œ",
            "plug": "ðŸ”Œ",
            "lock": "ðŸ”’",
            "sensor": "ðŸ“¡",
            "camera": "ðŸ“·",
            "fan": "ðŸ’¨",
            "blind": "ðŸªŸ",
            "garage": "ðŸš—",
            "valve": "ðŸš°",
        }
        return icons.get(device_type.lower(), "ðŸ“¦")

