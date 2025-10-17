"""
BasePersistenceManager: classe de base pour les managers de persistance JSON.

Fournit:
- Accès unifié à JsonStorage
- Thread-safety avec RLock
- Normalisation de noms commune
- Pattern cohérent pour load/save
"""

from abc import ABC
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

from utils.json_storage import get_json_storage
from utils.text_utils import normalize_name


class BasePersistenceManager(ABC):
    """
    Classe de base pour tous les managers qui font de la persistance JSON.

    Unifie:
    - Accès thread-safe au stockage JSON
    - Normalisation cohérente des noms
    - Pattern load/save standardisé
    """

    def __init__(
        self,
        storage_key: str,
        config_dir: Optional[Path] = None,
        lock: Optional[RLock] = None
    ) -> None:
        """
        Initialise le manager de persistance.

        Args:
            storage_key: Clé du fichier JSON (ex: "favorites.json")
            config_dir: Répertoire de stockage (défaut: ~/.alexa/)
            lock: Verrou personnalisé (défaut: nouveau RLock)
        """
        self.storage_key = storage_key
        self.storage = get_json_storage(config_dir)
        self._lock = lock or RLock()

        # Données en mémoire (chargées à l'initialisation)
        self._data: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Charge les données depuis le stockage JSON."""
        self._data = self.storage.load(self.storage_key, default={})

    def _save_data(self) -> bool:
        """Sauvegarde les données vers le stockage JSON."""
        return self.storage.save(self.storage_key, self._data)

    def _normalize_name(self, name: str) -> str:
        """
        Normalise un nom pour utilisation comme clé.

        Utilise la fonction centralisée de utils.text_utils.
        """
        return normalize_name(name)

    def _get_item_key(self, name: str) -> str:
        """
        Génère la clé normalisée pour un élément.

        Peut être overridé par les sous-classes pour une logique spécifique.
        """
        return self._normalize_name(name)

    def _validate_item(self, item: Dict[str, Any]) -> bool:
        """
        Valide la structure d'un élément.

        À implémenter par les sous-classes selon leurs besoins.
        """
        return isinstance(item, dict)

    def _create_item(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Crée un nouvel élément avec structure standard.

        À implémenter par les sous-classes.
        """
        raise NotImplementedError("Sous-classes doivent implémenter _create_item")

    def add_item(self, name: str, **kwargs: Any) -> bool:
        """
        Ajoute un élément de manière thread-safe.

        Args:
            name: Nom de l'élément
            **kwargs: Paramètres spécifiques à l'élément

        Returns:
            True si ajouté avec succès
        """
        with self._lock:
            key = self._get_item_key(name)

            if key in self._data:
                return False  # Élément existe déjà

            item = self._create_item(name, **kwargs)
            if not self._validate_item(item):
                return False

            self._data[key] = item
            return self._save_data()

    def update_item(self, name: str, **kwargs: Any) -> bool:
        """
        Met à jour un élément existant de manière thread-safe.

        Args:
            name: Nom de l'élément
            **kwargs: Nouvelles valeurs

        Returns:
            True si mis à jour avec succès
        """
        with self._lock:
            key = self._get_item_key(name)

            if key not in self._data:
                return False

            # Fusionner les nouvelles valeurs
            self._data[key].update(kwargs)

            if not self._validate_item(self._data[key]):
                return False

            return self._save_data()

    def remove_item(self, name: str) -> bool:
        """
        Supprime un élément de manière thread-safe.

        Args:
            name: Nom de l'élément à supprimer

        Returns:
            True si supprimé avec succès
        """
        with self._lock:
            key = self._get_item_key(name)

            if key not in self._data:
                return False

            del self._data[key]
            return self._save_data()

    def get_item(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un élément par son nom.

        Args:
            name: Nom de l'élément

        Returns:
            Élément ou None si inexistant
        """
        key = self._get_item_key(name)
        return self._data.get(key)

    def get_all_items(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère tous les éléments.

        Returns:
            Copie des données (pour éviter modifications externes)
        """
        return self._data.copy()

    def item_exists(self, name: str) -> bool:
        """
        Vérifie si un élément existe.

        Args:
            name: Nom de l'élément

        Returns:
            True si l'élément existe
        """
        key = self._get_item_key(name)
        return key in self._data

    def clear_all(self) -> bool:
        """
        Supprime tous les éléments (utiliser avec précaution).

        Returns:
            True si vidé avec succès
        """
        with self._lock:
            self._data.clear()
            return self._save_data()
