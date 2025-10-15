"""
Commandes de gestion des appareils Alexa.

Ce module gère toutes les opérations liées aux appareils:
- list: Lister tous les appareils
- info: Informations détaillées sur un appareil

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import json
from typing import Any, Dict, List

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter
from cli.help_texts.device_help import (
    DEVICE_DESCRIPTION,
    INFO_HELP,
    LIST_HELP,
    VOLUME_HELP,
)
from data.device_family_mapping import get_device_display_name


class DeviceCommand(BaseCommand):
    """
    Commande de gestion des appareils Alexa.

    Gère list et info.

    Actions:
        - list: Lister tous les appareils Alexa
        - info: Informations sur un appareil spécifique

    Example:
        >>> python alexa.py device list
        >>> python alexa.py device info -d "Salon"
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes d'appareils.

        Args:
            parser: Sous-parser pour la catégorie 'device'
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description simplifiée (uniquement Usage)
        parser.description = DEVICE_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Lister tous les appareils Alexa",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        list_parser.add_argument(
            "--filter",
            type=str,
            metavar="PATTERN",
            help="Filtrer les appareils par nom (recherche partielle)",
        )
        list_parser.add_argument(
            "--online-only", action="store_true", help="Afficher uniquement les appareils en ligne"
        )
        list_parser.add_argument(
            "--refresh", action="store_true", help="Forcer la resynchronisation avant d'afficher"
        )
        list_parser.add_argument(
            "--json", action="store_true", help="Afficher les données au format JSON"
        )

        # Action: info
        info_parser = subparsers.add_parser(
            "info",
            help="Informations détaillées sur un appareil",
            description=INFO_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        info_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        info_parser.add_argument(
            "--json", action="store_true", help="Afficher les données au format JSON"
        )

        # Action: volume
        volume_parser = subparsers.add_parser(
            "volume",
            help="Gérer le volume d'un appareil",
            description=VOLUME_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        volume_subparsers = volume_parser.add_subparsers(
            dest="volume_action",
            description="Action à effectuer sur le volume",
            required=True,
        )

        # volume get
        volume_get_parser = volume_subparsers.add_parser(
            "get",
            help="Obtenir le volume actuel",
            description="Affiche le niveau de volume actuel d'un appareil.",
        )
        volume_get_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )

        # volume set
        volume_set_parser = volume_subparsers.add_parser(
            "set",
            help="Définir le volume",
            description="Définit le niveau de volume d'un appareil.",
        )
        volume_set_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        volume_set_parser.add_argument(
            "--level",
            type=int,
            required=True,
            metavar="VOLUME",
            help="Niveau de volume (0-100)",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande d'appareil.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        # Validation connexion (sauf pour certaines actions)
        # 'list' peut fonctionner en cache — combiner les conditions pour plus de clarté
        if args.action not in ["list"] and not self.validate_connection():
            return False

        if args.action == "list":
            return self._list_devices(args)
        elif args.action == "info":
            return self._device_info(args)
        elif args.action == "volume":
            return self._manage_volume(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _list_devices(self, args: argparse.Namespace) -> bool:
        """
        Liste tous les appareils.

        Args:
            args: Arguments (filter, online_only, refresh, json_output)

        Returns:
            True si succès
        """
        try:
            if not self.device_mgr:
                self.error("Gestionnaire d'appareils non disponible")
                return False

            # Si --refresh demandé, forcer la resynchronisation
            if hasattr(args, "refresh") and args.refresh:
                ctx = self.require_context()
                if not ctx.sync_service:
                    self.warning("SyncService non disponible, utilisation du cache existant")
                else:
                    self.info("🔄 Resynchronisation des appareils...")
                    try:
                        ctx.sync_service._sync_alexa_devices()
                        self.success("✅ Synchronisation terminée")
                    except Exception as e:
                        self.logger.exception("Erreur lors de la resynchronisation")
                        self.warning(f"Impossible de resynchroniser: {e}")
                        self.info("Utilisation du cache existant")

            # Récupérer les appareils
            devices = self.call_with_breaker(self.device_mgr.get_devices)

            if devices is None:
                self.error("Impossible de récupérer la liste des appareils")
                return False

            # Filtrage
            if args.filter:
                devices = [
                    d for d in devices if args.filter.lower() in d.get("accountName", "").lower()
                ]

            if args.online_only:
                devices = [d for d in devices if d.get("online", False)]

            if not devices:
                self.warning("Aucun appareil trouvé")
                return True

            # Affichage
            if hasattr(args, "json_output") and args.json_output:
                print(json.dumps(devices, indent=2, ensure_ascii=False))
            else:
                self._display_devices_table(devices)

            return True

        except Exception as e:
            self.logger.exception("Erreur lors du listage des appareils")
            self.error(f"Erreur: {e}")
            return False

    def _display_devices_table(self, devices: List[Dict[str, Any]]) -> None:
        """
        Affiche les appareils sous forme de tableau.

        Args:
            devices: Liste des appareils
        """
        self.info(f"📱 {len(devices)} appareil(s) trouvé(s):\n")

        # Préparer les données
        table_data = []
        for device in devices:
            name = device.get("accountName", "N/A")
            device_type = device.get("deviceType", "N/A")
            raw_family = device.get("deviceFamily", "N/A")
            family = get_device_display_name(raw_family, device_type)
            online = "🟢 En ligne" if device.get("online", False) else "🔴 Hors ligne"
            serial = device.get("serialNumber", "N/A")[:15] + "..."

            table_data.append([name, device_type, family, online, serial])

        # Afficher le tableau
        table = self.format_table(table_data, ["Nom", "Type", "Famille", "État", "Serial"])
        print(table)

    def _device_info(self, args: argparse.Namespace) -> bool:
        """
        Affiche les informations détaillées sur un appareil.

        Args:
            args: Arguments (device, json_output)

        Returns:
            True si succès
        """
        try:
            if not self.device_mgr:
                self.error("Gestionnaire d'appareils non disponible")
                return False

            # Récupérer tous les appareils
            devices = self.call_with_breaker(self.device_mgr.get_devices)

            if devices is None:
                self.error("Impossible de récupérer la liste des appareils")
                return False

            # Trouver l'appareil
            device = None
            for d in devices:
                if d.get("accountName") == args.device:
                    device = d
                    break

            if not device:
                self.error(f"Appareil '{args.device}' non trouvé")
                return False

            # Affichage
            if hasattr(args, "json_output") and args.json_output:
                print(json.dumps(device, indent=2, ensure_ascii=False))
            else:
                self._display_device_info(device)

            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération des infos appareil")
            self.error(f"Erreur: {e}")
            return False

    def _display_device_info(self, device: Dict[str, Any]) -> None:
        """
        Affiche les informations d'un appareil de manière formatée.

        Args:
            device: Données de l'appareil
        """
        self.info(f"📱 Informations sur '{device.get('accountName')}':\n")

        print(f"  Nom:                {device.get('accountName', 'N/A')}")
        print(f"  Type:               {device.get('deviceType', 'N/A')}")

        raw_family = device.get("deviceFamily", "N/A")
        device_type = device.get("deviceType", "N/A")
        display_family = get_device_display_name(raw_family, device_type)
        print(f"  Famille:            {display_family} ({raw_family})")

        print(f"  Serial:             {device.get('serialNumber', 'N/A')}")
        print(f"  Software Version:   {device.get('softwareVersion', 'N/A')}")

        online = "🟢 En ligne" if device.get("online", False) else "🔴 Hors ligne"
        print(f"  État:               {online}")

        # Capacités
        capabilities = device.get("capabilities", [])
        if capabilities:
            print(f"  Capacités:          {', '.join(capabilities)}")

        # Autres infos utiles
        if "deviceOwnerCustomerId" in device:
            print(f"  Customer ID:        {device['deviceOwnerCustomerId']}")

        if "registrationId" in device:
            print(f"  Registration ID:    {device['registrationId']}")

    def _manage_volume(self, args: argparse.Namespace) -> bool:
        """
        Gère les commandes de volume pour un appareil.

        Args:
            args: Arguments parsés pour la commande de volume

        Returns:
            True si succès, False sinon
        """
        try:
            if not self.device_mgr:
                self.error("Gestionnaire d'appareils non disponible")
                return False

            if args.volume_action == "get":
                return self._get_volume(args)
            elif args.volume_action == "set":
                return self._set_volume(args)
            else:
                self.error(f"Action de volume '{args.volume_action}' non reconnue")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la gestion du volume")
            self.error(f"Erreur: {e}")
            return False

    def _get_volume(self, args: argparse.Namespace) -> bool:
        """
        Obtient le volume actuel d'un appareil.

        Args:
            args: Arguments (device)

        Returns:
            True si succès
        """
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"🔊 Récupération volume de '{args.device}'...")

            ctx = self.require_context()
            if not ctx.settings_mgr:
                self.error("SettingsManager non disponible")
                return False

            volume = self.call_with_breaker(
                ctx.settings_mgr.get_volume, serial, device_type
            )

            if volume is not None:
                self.success(f"✅ Volume actuel: {volume}%")
                return True
            else:
                self.warning("Impossible de récupérer le volume")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération du volume")
            self.error(f"Erreur: {e}")
            return False

    def _set_volume(self, args: argparse.Namespace) -> bool:
        """
        Définit le volume d'un appareil.

        Args:
            args: Arguments (device, level)

        Returns:
            True si succès
        """
        try:
            # Validation niveau
            if not 0 <= args.level <= 100:
                self.error("Le volume doit être entre 0 et 100")
                return False

            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"🔊 Réglage volume '{args.device}' → {args.level}%...")

            ctx = self.require_context()
            if not ctx.settings_mgr:
                self.error("SettingsManager non disponible")
                return False

            result = self.call_with_breaker(
                ctx.settings_mgr.set_volume, serial, device_type, args.level
            )

            if result:
                self.success(f"✅ Volume défini à {args.level}%")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la définition du volume")
            self.error(f"Erreur: {e}")
            return False
