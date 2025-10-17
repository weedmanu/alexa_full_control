"""
MultiRoom Manager - Gestion des groupes d'appareils multiroom

Permet de grouper les appareils Alexa et d'exécuter des commandes
simultanément sur tous les appareils du groupe.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from core.base_persistence_manager import BasePersistenceManager


class MultiRoomManager(BasePersistenceManager):
    """Gestionnaire des groupes multiroom."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialise le manager."""
        super().__init__("multiroom_groups.json", config_dir)

    def _validate_item(self, item: Dict[str, Any]) -> bool:
        """
        Valide la structure d'un groupe multiroom.

        Args:
            item: Groupe à valider

        Returns:
            True si valide, False sinon
        """
        required_keys = {"name", "devices"}
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            return False

        devices = item.get("devices", [])
        return not (not isinstance(devices, list) or len(devices) < 2)

    def _create_item(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Crée un nouvel élément groupe.

        Args:
            name: Nom du groupe
            **kwargs: Doit contenir 'devices'

        Returns:
            Groupe créé
        """
        devices = kwargs.get("devices", [])
        return {
            "name": name,
            "devices": list(set(devices)),  # Dédupliquer
            "created": datetime.now().isoformat(),
            "modified": None,
        }

    def create_group(
        self,
        name: str,
        devices: List[str],
    ) -> bool:
        """Crée un nouveau groupe multiroom.

        Args:
            name: Nom du groupe
            devices: Liste des device serials

        Returns:
            True si succès, False sinon
        """
        # Validation
        if not name or not name.strip():
            logger.warning("Nom du groupe manquant")
            return False

        if not devices or len(devices) < 2:
            logger.warning("Au moins 2 appareils requis pour un groupe")
            return False

        # Utiliser BasePersistenceManager pour créer
        return self.add_item(name, devices=devices)

    def delete_group(self, name: str) -> bool:
        """Supprime un groupe.

        Args:
            name: Nom du groupe

        Returns:
            True si succès, False sinon
        """
        return self.remove_item(name)

    def get_group(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un groupe par son nom.

        Args:
            name: Nom du groupe

        Returns:
            Dict du groupe ou None
        """
        return self.get_item(name)

    def get_groups(self) -> Dict[str, Dict[str, Any]]:
        """Récupère tous les groupes.

        Returns:
            Dict de tous les groupes
        """
        return self.get_all_items()

    def add_device_to_group(self, group_name: str, device_serial: str) -> bool:
        """Ajoute un appareil au groupe.

        Args:
            group_name: Nom du groupe
            device_serial: Serial de l'appareil

        Returns:
            True si succès, False sinon
        """
        group = self.get_item(group_name)
        if not group:
            logger.warning(f"Groupe '{group_name}' introuvable")
            return False

        # Vérifier que l'appareil n'est pas déjà dans le groupe
        if device_serial in group["devices"]:
            logger.warning(f"Appareil '{device_serial}' est déjà dans le groupe '{group_name}'")
            return False

        # Ajouter l'appareil
        group["devices"].append(device_serial)
        group["modified"] = datetime.now().isoformat()

        return self.update_item(group_name, devices=group["devices"], modified=group["modified"])

    def remove_device_from_group(self, group_name: str, device_serial: str) -> bool:
        """Retire un appareil du groupe.

        Args:
            group_name: Nom du groupe
            device_serial: Serial de l'appareil

        Returns:
            True si succès, False sinon
        """
        group = self.get_item(group_name)
        if not group:
            logger.warning(f"Groupe '{group_name}' introuvable")
            return False

        # Vérifier que l'appareil est dans le groupe
        if device_serial not in group["devices"]:
            logger.warning(f"Appareil '{device_serial}' n'est pas dans le groupe '{group_name}'")
            return False

        # Retirer l'appareil
        group["devices"].remove(device_serial)
        group["modified"] = datetime.now().isoformat()

        return self.update_item(group_name, devices=group["devices"], modified=group["modified"])

    def rename_group(self, old_name: str, new_name: str) -> bool:
        """Renomme un groupe.

        Args:
            old_name: Ancien nom
            new_name: Nouveau nom

        Returns:
            True si succès, False sinon
        """
        # Récupérer l'ancien groupe
        old_group = self.get_item(old_name)
        if not old_group:
            logger.warning(f"Groupe '{old_name}' introuvable")
            return False

        # Vérifier que le nouveau nom n'existe pas
        if self.item_exists(new_name):
            logger.warning(f"Groupe '{new_name}' existe déjà")
            return False

        # Créer le nouveau groupe avec le nouveau nom
        old_group["name"] = new_name
        old_group["modified"] = datetime.now().isoformat()

        # Supprimer l'ancien et ajouter le nouveau
        if not self.remove_item(old_name):
            return False

        return self.add_item(new_name, devices=old_group["devices"])

    def get_group_devices(self, group_name: str) -> List[str]:
        """Récupère la liste des appareils d'un groupe.

        Args:
            group_name: Nom du groupe

        Returns:
            Liste des serials
        """
        group = self.get_group(group_name)
        if not group:
            return []

        from typing import List, cast

        devices = cast(List[str], group.get("devices", []))
        return devices

    def get_groups_sorted_by_creation(self) -> List[Dict[str, Any]]:
        """Retourne les groupes triés par date de création.

        Returns:
            Liste des groupes triés
        """
        groups = list(self.get_all_items().values())
        groups.sort(key=lambda x: x.get("created", ""), reverse=True)
        return groups

    def save_groups(self) -> bool:
        """Sauvegarde explicitement les groupes sur le stockage JSON.

        Cette méthode expose l'opération de sauvegarde pour les cas de test
        ou d'utilisation où l'on souhaite forcer l'écriture immédiatement.
        """
        return self._save_data()
