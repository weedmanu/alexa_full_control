"""
BasePersistenceManager: classe de base pour les managers de persistance JSON.

Fournit:
- Acc�s unifi� � JsonStorage
- Thread-safety avec RLock
- Normalisation de noms commune
- Pattern coh�rent pour load/save
"""

from abc import ABC, abstractmethod
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

from utils.json_storage import get_json_storage
from utils.text_utils import normalize_name


class BasePersistenceManager(ABC):
    """
    Classe de base pour tous les managers qui font de la persistance JSON.

    Unifie:
    - Acc�s thread-safe au stockage JSON
    - Normalisation coh�rente des noms
    - Pattern load/save standardis�
    """

    def __init__(self, storage_key: str, config_dir: Optional[Path] = None, lock: Optional[RLock] = None) -> None:
        """
        Initialise le manager de persistance.

        Args:
            storage_key: Cl� du fichier JSON (ex: "favorites.json")
            config_dir: R�pertoire de stockage (d�faut: ~/.alexa/)
            lock: Verrou personnalis� (d�faut: nouveau RLock)
        """
        self.storage_key = storage_key
        self.storage = get_json_storage(config_dir)
        self._lock = lock or RLock()

        # Donn�es en m�moire (charg�es � l'initialisation)
        self._data: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Charge les donn�es depuis le stockage JSON."""
        self._data = self.storage.load(self.storage_key, default={})

    def _save_data(self) -> bool:
        """Sauvegarde les donn�es vers le stockage JSON."""
        return self.storage.save(self.storage_key, self._data)

    def _normalize_name(self, name: str) -> str:
        """
        Normalise un nom pour utilisation comme cl�.

        Utilise la fonction centralis�e de utils.text_utils.
        """
        return normalize_name(name)

    def _get_item_key(self, name: str) -> str:
        """
        G�n�re la cl� normalis�e pour un �l�ment.

        Peut �tre overrid� par les sous-classes pour une logique sp�cifique.
        """
        return self._normalize_name(name)

    def _validate_item(self, item: Dict[str, Any]) -> bool:
        """
        Valide la structure d'un �l�ment.

        � impl�menter par les sous-classes selon leurs besoins.
        """
        return isinstance(item, dict)

    @abstractmethod
    def _create_item(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Cr�e un nouvel �l�ment avec structure standard.

        � impl�menter par les sous-classes.
        """
        raise NotImplementedError("Sous-classes doivent impl�menter _create_item")

    def add_item(self, name: str, **kwargs: Any) -> bool:
        """
        Ajoute un �l�ment de mani�re thread-safe.

        Args:
            name: Nom de l'�l�ment
            **kwargs: Param�tres sp�cifiques � l'�l�ment

        Returns:
            True si ajout� avec succ�s
        """
        with self._lock:
            key = self._get_item_key(name)

            if key in self._data:
                return False  # �l�ment existe d�j�

            item = self._create_item(name, **kwargs)
            if not self._validate_item(item):
                return False

            self._data[key] = item
            return self._save_data()

    def update_item(self, name: str, **kwargs: Any) -> bool:
        """
        Met � jour un �l�ment existant de mani�re thread-safe.

        Args:
            name: Nom de l'�l�ment
            **kwargs: Nouvelles valeurs

        Returns:
            True si mis � jour avec succ�s
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
        Supprime un �l�ment de mani�re thread-safe.

        Args:
            name: Nom de l'�l�ment � supprimer

        Returns:
            True si supprim� avec succ�s
        """
        with self._lock:
            key = self._get_item_key(name)

            if key not in self._data:
                return False

            del self._data[key]
            return self._save_data()

    def get_item(self, name: str) -> Optional[Dict[str, Any]]:
        """
        R�cup�re un �l�ment par son nom.

        Args:
            name: Nom de l'�l�ment

        Returns:
            �l�ment ou None si inexistant
        """
        key = self._get_item_key(name)
        return self._data.get(key)

    def get_all_items(self) -> Dict[str, Dict[str, Any]]:
        """
        R�cup�re tous les �l�ments.

        Returns:
            Copie des donn�es (pour �viter modifications externes)
        """
        return self._data.copy()

    def item_exists(self, name: str) -> bool:
        """
        V�rifie si un �l�ment existe.

        Args:
            name: Nom de l'�l�ment

        Returns:
            True si l'�l�ment existe
        """
        key = self._get_item_key(name)
        return key in self._data

    def clear_all(self) -> bool:
        """
        Supprime tous les �l�ments (utiliser avec pr�caution).

        Returns:
            True si vid� avec succ�s
        """
        with self._lock:
            self._data.clear()
            return self._save_data()




