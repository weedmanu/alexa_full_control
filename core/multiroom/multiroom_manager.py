"""
MultiRoom Manager - Gestion des groupes d'appareils multiroom

Permet de grouper les appareils Alexa et d'exécuter des commandes
simultanément sur tous les appareils du groupe.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


class MultiRoomManager:
    """Gestionnaire des groupes multiroom."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialise le manager."""
        # Déterminer le répertoire de config
        if config_dir is None:
            config_dir = Path.home() / ".alexa"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.groups_file = self.config_dir / "multiroom_groups.json"
        self._groups: Dict[str, Dict[str, Any]] = {}

        # Charger les groupes existants
        self._load_groups()

    def _normalize_name(self, name: str) -> str:
        """Normalise le nom du groupe pour la clé."""
        return name.lower().replace(" ", "_").replace("-", "_")

    def _load_groups(self) -> None:
        """Charge les groupes depuis le fichier."""
        try:
            if self.groups_file.exists():
                with open(self.groups_file, "r") as f:
                    self._groups = json.load(f)
            else:
                self._groups = {}
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Erreur lors du chargement des groupes: {e}")
            self._groups = {}

    def save_groups(self) -> bool:
        """Sauvegarde les groupes dans le fichier."""
        try:
            with open(self.groups_file, "w") as f:
                json.dump(self._groups, f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Erreur lors de la sauvegarde des groupes: {e}")
            return False

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

        # Vérifier s'il existe déjà
        key = self._normalize_name(name)
        if key in self._groups:
            logger.warning(f"Groupe '{name}' existe déjà")
            return False

        # Créer le groupe
        self._groups[key] = {
            "name": name,
            "devices": list(set(devices)),  # Dédupliquer
            "created": datetime.now().isoformat(),
            "modified": None,
        }

        logger.info(f"Groupe '{name}' créé avec {len(devices)} appareils")

        # Sauvegarder
        return self.save_groups()

    def delete_group(self, name: str) -> bool:
        """Supprime un groupe.

        Args:
            name: Nom du groupe

        Returns:
            True si succès, False sinon
        """
        key = self._normalize_name(name)

        if key not in self._groups:
            logger.warning(f"Groupe '{name}' introuvable")
            return False

        del self._groups[key]
        logger.info(f"Groupe '{name}' supprimé")

        return self.save_groups()

    def get_group(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un groupe par son nom.

        Args:
            name: Nom du groupe

        Returns:
            Dict du groupe ou None
        """
        key = self._normalize_name(name)
        return self._groups.get(key)

    def get_groups(self) -> Dict[str, Dict[str, Any]]:
        """Récupère tous les groupes.

        Returns:
            Dict de tous les groupes
        """
        return self._groups.copy()

    def add_device_to_group(self, group_name: str, device_serial: str) -> bool:
        """Ajoute un appareil au groupe.

        Args:
            group_name: Nom du groupe
            device_serial: Serial de l'appareil

        Returns:
            True si succès, False sinon
        """
        key = self._normalize_name(group_name)

        if key not in self._groups:
            logger.warning(f"Groupe '{group_name}' introuvable")
            return False

        # Vérifier que l'appareil n'est pas déjà dans le groupe
        if device_serial in self._groups[key]["devices"]:
            logger.warning(
                f"Appareil '{device_serial}' est déjà dans le groupe '{group_name}'"
            )
            return False

        # Ajouter l'appareil
        self._groups[key]["devices"].append(device_serial)
        self._groups[key]["modified"] = datetime.now().isoformat()

        logger.info(
            f"Appareil '{device_serial}' ajouté au groupe '{group_name}'"
        )

        return self.save_groups()

    def remove_device_from_group(self, group_name: str, device_serial: str) -> bool:
        """Retire un appareil du groupe.

        Args:
            group_name: Nom du groupe
            device_serial: Serial de l'appareil

        Returns:
            True si succès, False sinon
        """
        key = self._normalize_name(group_name)

        if key not in self._groups:
            logger.warning(f"Groupe '{group_name}' introuvable")
            return False

        # Vérifier que l'appareil est dans le groupe
        if device_serial not in self._groups[key]["devices"]:
            logger.warning(
                f"Appareil '{device_serial}' n'est pas dans le groupe '{group_name}'"
            )
            return False

        # Retirer l'appareil
        self._groups[key]["devices"].remove(device_serial)
        self._groups[key]["modified"] = datetime.now().isoformat()

        logger.info(
            f"Appareil '{device_serial}' retiré du groupe '{group_name}'"
        )

        return self.save_groups()

    def rename_group(self, old_name: str, new_name: str) -> bool:
        """Renomme un groupe.

        Args:
            old_name: Ancien nom
            new_name: Nouveau nom

        Returns:
            True si succès, False sinon
        """
        old_key = self._normalize_name(old_name)
        new_key = self._normalize_name(new_name)

        if old_key not in self._groups:
            logger.warning(f"Groupe '{old_name}' introuvable")
            return False

        if new_key in self._groups:
            logger.warning(f"Groupe '{new_name}' existe déjà")
            return False

        # Renommer
        group = self._groups.pop(old_key)
        group["name"] = new_name
        group["modified"] = datetime.now().isoformat()
        self._groups[new_key] = group

        logger.info(f"Groupe renommé: '{old_name}' → '{new_name}'")

        return self.save_groups()

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

        return group.get("devices", [])

    def get_groups_sorted_by_creation(self) -> List[Dict[str, Any]]:
        """Retourne les groupes triés par date de création.

        Returns:
            Liste des groupes triés
        """
        groups = list(self._groups.values())
        groups.sort(key=lambda x: x.get("created", ""), reverse=True)
        return groups
