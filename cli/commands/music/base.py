"""
Classe de base pour les sous-commandes musicales.

Auteur: M@nu
Date: 8 octobre 2025
"""

from typing import Optional, Tuple

from loguru import logger


class MusicSubCommand:
    """
    Classe de base pour toutes les sous-commandes musicales.

    Cette classe n'hérite PAS de BaseCommand car elle ne représente pas
    une commande complète mais un sous-module fonctionnel.
    """

    def __init__(self):
        """Initialise la sous-commande."""
        self.context = None
        self.logger = logger

    def get_device_serial(self, device_name: str) -> Optional[str]:
        """
        Récupère le serial d'un appareil par son nom.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Serial de l'appareil ou None
        """
        if self.context is None or self.context.device_mgr is None:
            return None

        devices = self.context.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                return device.get("serialNumber")

        return None

    def error(self, message: str):
        """Affiche un message d'erreur."""
        self.logger.error(message)

    def success(self, message: str):
        """Affiche un message de succès."""
        self.logger.success(message)

    def info(self, message: str):
        """Affiche un message d'information."""
        self.logger.info(message)

    def get_device_info(self, device_name: str) -> Optional[Tuple[str, str]]:
        """
        Récupère le serial et le type d'un appareil.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Tuple (serial, device_type) ou None si non trouvé
        """
        serial = self.get_device_serial(device_name)
        if not serial:
            return None

        device_type = self._get_device_type(device_name)
        return (serial, device_type)

    def _get_device_type(self, device_name: str) -> str:
        """Récupère le type d'appareil."""
        if self.context is None or self.context.device_mgr is None:
            return "ECHO"

        devices = self.context.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                return device.get("deviceType", "ECHO")

        return "ECHO"

    def _get_parent_multiroom(self, device_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Récupère l'appareil parent multiroom si applicable.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Tuple (parent_id, parent_type) ou (None, None)
        """
        if self.context is None or self.context.device_mgr is None:
            return (None, None)

        devices = self.context.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                clusters = device.get("parentClusters", [])
                if clusters:
                    parent_id = clusters[0]
                    # Trouver le type du parent
                    for parent_dev in devices:
                        if parent_dev.get("serialNumber") == parent_id:
                            return (parent_id, parent_dev.get("deviceType"))
                break

        return (None, None)

    def get_media_owner_id(self) -> str:
        """Récupère le media owner customer ID."""
        if self.context and hasattr(self.context, "auth"):
            return getattr(self.context.auth, "customer_id", "")
        return ""
