"""
JsonStorage: Gestionnaire centralisé pour load/save JSON thread-safe et atomique.

Fournit:
- Écriture atomique (pas de corruption)
- Backup automatique (.bak)
- Thread-safety avec RLock
- Validation JSON
- Inter-process locking (si portalocker disponible)
"""

import json
import os
import tempfile
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

try:
    import portalocker  # Inter-process locking
    portalocker_available = True
except ImportError:
    portalocker = None  # type: ignore
    portalocker_available = False


class JsonStorage:
    """
    Gestionnaire centralisé pour load/save JSON thread-safe et atomique.

    Fonctionnalités:
    - Écriture atomique (tmp + rename)
    - Backup automatique (.bak)
    - Thread-safety (RLock)
    - Inter-process locking (optionnel)
    - Validation JSON
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialise le stockage JSON.

        Args:
            base_dir: Répertoire de base (défaut: ~/.alexa/)
        """
        self.base_dir = base_dir or (Path.home() / ".alexa")
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Un verrou par fichier pour éviter les contentions inutiles
        self._locks: Dict[str, RLock] = {}

    def _get_lock(self, filename: str) -> RLock:
        """Retourne le verrou pour un fichier donné."""
        if filename not in self._locks:
            self._locks[filename] = RLock()
        return self._locks[filename]

    def load(self, filename: str, default: Any = None) -> Any:
        """
        Charge un fichier JSON de façon thread-safe.

        Args:
            filename: Nom du fichier (ex: "favorites.json")
            default: Valeur par défaut si fichier absent ou invalide

        Returns:
            Données JSON ou default
        """
        lock = self._get_lock(filename)
        with lock:
            file_path = self.base_dir / filename
            if not file_path.exists():
                return default

            try:
                with open(file_path, encoding='utf-8') as f:
                    if portalocker_available and portalocker is not None:
                        portalocker.lock(f, portalocker.LOCK_SH)  # Shared lock
                    data = json.load(f)
                return data
            except (json.JSONDecodeError, OSError) as e:
                from loguru import logger
                logger.error(f"Erreur lecture JSON {filename}: {e}")
                return default

    def save(self, filename: str, data: Any, backup: bool = True) -> bool:
        """
        Sauvegarde atomique d'un fichier JSON.

        Args:
            filename: Nom du fichier
            data: Données à sauvegarder
            backup: Créer un .bak avant écrasement

        Returns:
            True si succès, False sinon
        """
        lock = self._get_lock(filename)
        with lock:
            file_path = self.base_dir / filename

            # Backup de l'ancien fichier
            if backup and file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                try:
                    import shutil
                    shutil.copy2(file_path, backup_path)
                except OSError:
                    pass  # Best effort

            # Écriture atomique (tmp + rename)
            tmp_path = None
            try:
                # Ensure base dir exists (race conditions or tests may remove it)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                tmp_fd, tmp_path = tempfile.mkstemp(
                    dir=self.base_dir,
                    prefix=f"{filename}.",
                    suffix=".tmp"
                )
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                    if portalocker_available and portalocker is not None:
                        portalocker.lock(f, portalocker.LOCK_EX)  # Exclusive lock
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())  # Force écriture disque

                # Remplacement atomique
                os.replace(tmp_path, str(file_path))
                return True

            except (OSError, TypeError) as e:
                from loguru import logger
                logger.error(f"Erreur sauvegarde JSON {filename}: {e}")
                # Nettoyer fichier temporaire
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                return False

    def exists(self, filename: str) -> bool:
        """
        Vérifie si un fichier existe.

        Args:
            filename: Nom du fichier

        Returns:
            True si le fichier existe
        """
        file_path = self.base_dir / filename
        return file_path.exists()

    def delete(self, filename: str) -> bool:
        """
        Supprime un fichier.

        Args:
            filename: Nom du fichier

        Returns:
            True si supprimé avec succès
        """
        lock = self._get_lock(filename)
        with lock:
            file_path = self.base_dir / filename
            try:
                file_path.unlink(missing_ok=True)
                return True
            except OSError as e:
                from loguru import logger
                logger.error(f"Erreur suppression {filename}: {e}")
                return False

    def list_files(self, pattern: str = "*.json") -> list[str]:
        """
        Liste les fichiers correspondant à un pattern.

        Args:
            pattern: Pattern glob (défaut: "*.json")

        Returns:
            Liste des noms de fichiers
        """
        import glob
        pattern_path = self.base_dir / pattern
        files = glob.glob(str(pattern_path))
        return [Path(f).name for f in files]


# Instance globale singleton
_json_storage: Optional[JsonStorage] = None


def get_json_storage(base_dir: Optional[Path] = None) -> JsonStorage:
    """
    Factory pour JsonStorage.

    Comportement:
    - Si aucune instance n'existe, crée-en une pour `base_dir` (ou le défaut).
    - Si une instance existe et `base_dir` est fourni et diffère de celle en cache,
      réinitialise une nouvelle instance pour éviter la fuite de données entre
      contextes (utile pour les tests qui utilisent des répertoires temporaires).

    Args:
        base_dir: Répertoire de base (optionnel)

    Returns:
        Instance de JsonStorage pour le répertoire demandé
    """
    global _json_storage
    if _json_storage is None:
        _json_storage = JsonStorage(base_dir)
        return _json_storage

    # Si un base_dir différent est demandé, créer une nouvelle instance.
    if base_dir is not None and Path(base_dir) != _json_storage.base_dir:
        _json_storage = JsonStorage(base_dir)

    return _json_storage
