"""
Index optimisé pour recherches rapides de devices.

Optimisation Phase 2: Index HashMap O(1) au lieu de O(n).

Auteur: M@nu
Date: 7 octobre 2025
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from loguru import logger


@dataclass
class Device:
    """Représentation simplifiée d'un appareil Alexa."""

    serial_number: str
    account_name: str
    device_type: str
    device_family: str
    online: bool

    @classmethod
    def from_dict(cls, data: dict) -> "Device":
        """Crée un Device depuis un dict API."""
        return cls(
            serial_number=data.get("serialNumber", ""),
            account_name=data.get("accountName", ""),
            device_type=data.get("deviceType", ""),
            device_family=data.get("deviceFamily", ""),
            online=data.get("online", False),
        )


class DeviceIndex:
    """
    Index optimisé pour recherches rapides de devices.

    Performance:
    - Recherche par nom: O(1) au lieu de O(n)
    - Recherche par serial: O(1) au lieu de O(n)
    - Recherche par type: O(1) au lieu de O(n)
    - Recherche par famille: O(1) au lieu de O(n)

    Gain estimé: 90% réduction temps recherche (100 devices)

    Example:
        >>> index = DeviceIndex()
        >>> index.build_index(devices_list)
        >>> device = index.get_by_name("echo salon")  # Instantané !
        >>> devices_echo = index.get_by_family("ECHO")
    """

    def __init__(self):
        """Initialise les index vides."""
        self._by_serial: Dict[str, Device] = {}
        self._by_name: Dict[str, Device] = {}
        self._by_type: Dict[str, List[Device]] = {}
        self._by_family: Dict[str, List[Device]] = {}
        self._all_devices: List[Device] = []
        self._index_built = False

        logger.debug("DeviceIndex initialisé")

    def build_index(self, devices: List[Dict]) -> None:
        """
        Construit tous les index à partir d'une liste de devices.

        Args:
            devices: Liste de dictionnaires devices (format API)

        Example:
            >>> devices_data = [{"serialNumber": "ABC", "accountName": "Echo"}, ...]
            >>> index.build_index(devices_data)
        """
        # Réinitialiser
        self._by_serial.clear()
        self._by_name.clear()
        self._by_type.clear()
        self._by_family.clear()
        self._all_devices.clear()

        # Construire index
        for device_data in devices:
            device = Device.from_dict(device_data)
            self._all_devices.append(device)

            # Index par serial
            self._by_serial[device.serial_number] = device

            # Index par nom (insensible à la casse)
            name_key = device.account_name.lower().strip()
            self._by_name[name_key] = device

            # Index par type (multi-valeurs)
            if device.device_type not in self._by_type:
                self._by_type[device.device_type] = []
            self._by_type[device.device_type].append(device)

            # Index par famille (multi-valeurs)
            if device.device_family not in self._by_family:
                self._by_family[device.device_family] = []
            self._by_family[device.device_family].append(device)

        self._index_built = True

        logger.info(
            f"Index construit: {len(self._all_devices)} devices, "
            f"{len(self._by_type)} types, {len(self._by_family)} familles"
        )

    def get_by_serial(self, serial: str) -> Optional[Device]:
        """
        Recherche par numéro de série (O(1)).

        Args:
            serial: Numéro de série

        Returns:
            Device ou None
        """
        return self._by_serial.get(serial)

    def get_by_name(self, name: str) -> Optional[Device]:
        """
        Recherche par nom (O(1), insensible à la casse).

        Args:
            name: Nom de l'appareil (ex: "Echo Salon")

        Returns:
            Device ou None

        Example:
            >>> device = index.get_by_name("echo salon")  # Insensible casse
        """
        name_key = name.lower().strip()
        return self._by_name.get(name_key)

    def get_by_type(self, device_type: str) -> List[Device]:
        """
        Recherche tous les devices d'un type (O(1)).

        Args:
            device_type: Type d'appareil (ex: "A2IVLV5VM2W81")

        Returns:
            Liste de devices
        """
        return self._by_type.get(device_type, [])

    def get_by_family(self, family: str) -> List[Device]:
        """
        Recherche tous les devices d'une famille (O(1)).

        Args:
            family: Famille d'appareil (ex: "ECHO", "TABLET")

        Returns:
            Liste de devices

        Example:
            >>> echos = index.get_by_family("ECHO")
            >>> tablets = index.get_by_family("TABLET")
        """
        return self._by_family.get(family, [])

    def get_online_devices(self) -> List[Device]:
        """
        Retourne tous les appareils en ligne.

        Returns:
            Liste de devices en ligne
        """
        return [d for d in self._all_devices if d.online]

    def get_offline_devices(self) -> List[Device]:
        """
        Retourne tous les appareils hors ligne.

        Returns:
            Liste de devices hors ligne
        """
        return [d for d in self._all_devices if not d.online]

    def search(self, query: str) -> List[Device]:
        """
        Recherche flexible (nom partiel, serial partiel).

        Args:
            query: Texte à rechercher

        Returns:
            Liste de devices correspondants

        Example:
            >>> results = index.search("salon")  # Trouve "Echo Salon", etc.
        """
        query_lower = query.lower()
        results = []

        for device in self._all_devices:
            if (
                query_lower in device.account_name.lower()
                or query_lower in device.serial_number.lower()
                or query_lower in device.device_family.lower()
            ):
                results.append(device)

        return results

    def get_all(self) -> List[Device]:
        """Retourne tous les devices."""
        return self._all_devices.copy()

    def count(self) -> int:
        """Retourne le nombre total de devices."""
        return len(self._all_devices)

    def get_stats(self) -> dict:
        """
        Retourne des statistiques sur les devices.

        Returns:
            Dict avec statistiques
        """
        return {
            "total": len(self._all_devices),
            "online": len(self.get_online_devices()),
            "offline": len(self.get_offline_devices()),
            "types": len(self._by_type),
            "families": len(self._by_family),
            "families_detail": {family: len(devices) for family, devices in self._by_family.items()},
            "index_built": self._index_built,
        }

    def is_ready(self) -> bool:
        """Vérifie si l'index est construit."""
        return self._index_built


class SmartDeviceIndex:
    """
    Index optimisé pour appareils smart home (lumières, thermostats, etc.).

    Similaire à DeviceIndex mais pour appareils smart home.
    """

    def __init__(self):
        """Initialise les index vides."""
        self._by_id: Dict[str, dict] = {}
        self._by_name: Dict[str, dict] = {}
        self._by_type: Dict[str, List[dict]] = {}
        self._all_devices: List[dict] = []

        logger.debug("SmartDeviceIndex initialisé")

    def build_index(self, devices: List[dict]) -> None:
        """
        Construit les index smart home.

        Args:
            devices: Liste de devices smart home
        """
        self._by_id.clear()
        self._by_name.clear()
        self._by_type.clear()
        self._all_devices.clear()

        for device in devices:
            self._all_devices.append(device)

            # Index par ID
            device_id = device.get("id") or device.get("entityId")
            if device_id:
                self._by_id[device_id] = device

            # Index par nom
            name = device.get("friendlyName") or device.get("name", "")
            if name:
                name_key = name.lower().strip()
                self._by_name[name_key] = device

            # Index par type
            device_type = device.get("entityType") or device.get("type", "UNKNOWN")
            if device_type not in self._by_type:
                self._by_type[device_type] = []
            self._by_type[device_type].append(device)

        logger.info(f"SmartDeviceIndex construit: {len(self._all_devices)} devices, {len(self._by_type)} types")

    def get_by_id(self, device_id: str) -> Optional[dict]:
        """Recherche par ID (O(1))."""
        return self._by_id.get(device_id)

    def get_by_name(self, name: str) -> Optional[dict]:
        """Recherche par nom (O(1), insensible casse)."""
        name_key = name.lower().strip()
        return self._by_name.get(name_key)

    def get_by_type(self, device_type: str) -> List[dict]:
        """Recherche par type (O(1))."""
        return self._by_type.get(device_type, [])

    def get_lights(self) -> List[dict]:
        """Retourne toutes les lumières."""
        return self.get_by_type("LIGHT")

    def get_thermostats(self) -> List[dict]:
        """Retourne tous les thermostats."""
        return self.get_by_type("THERMOSTAT")

    def get_switches(self) -> List[dict]:
        """Retourne tous les switches."""
        return self.get_by_type("SWITCH")

    def get_all(self) -> List[dict]:
        """Retourne tous les devices."""
        return self._all_devices.copy()

    def count(self) -> int:
        """Retourne le nombre total."""
        return len(self._all_devices)

    def get_stats(self) -> dict:
        """Statistiques smart devices."""
        return {
            "total": len(self._all_devices),
            "types": len(self._by_type),
            "types_detail": {device_type: len(devices) for device_type, devices in self._by_type.items()},
        }
