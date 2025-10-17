"""
Tests unitaires pour JsonStorage.

Couvre:
- Load/save atomique
- Backup automatique
- Thread-safety
- Gestion d'erreurs
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.json_storage import JsonStorage


class TestJsonStorage:
    """Tests pour JsonStorage."""

    @pytest.fixture
    def temp_dir(self, tmp_path: Path) -> Path:
        """Répertoire temporaire pour les tests."""
        return tmp_path

    @pytest.fixture
    def storage(self, temp_dir: Path) -> JsonStorage:
        """Instance JsonStorage pour les tests."""
        return JsonStorage(base_dir=temp_dir)

    def test_load_nonexistent_file(self, storage: JsonStorage):
        """Test chargement fichier inexistant."""
        data = storage.load("nonexistent.json", default={"default": True})
        assert data == {"default": True}

    def test_save_and_load(self, storage: JsonStorage):
        """Test sauvegarde et chargement basique."""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        # Sauvegarde
        assert storage.save("test.json", test_data) is True

        # Chargement
        loaded = storage.load("test.json")
        assert loaded == test_data

    def test_atomic_write(self, storage: JsonStorage, temp_dir: Path):
        """Test que l'écriture est atomique (pas de fichiers temporaires laissés)."""
        test_data = {"test": "data"}

        # Sauvegarde
        assert storage.save("atomic.json", test_data) is True

        # Vérifier qu'aucun fichier temporaire n'est laissé
        temp_files = list(temp_dir.glob("atomic.json.*.tmp"))
        assert len(temp_files) == 0

        # Vérifier que le fichier final existe
        final_file = temp_dir / "atomic.json"
        assert final_file.exists()

    def test_backup_creation(self, storage: JsonStorage, temp_dir: Path):
        """Test création automatique de backup."""
        # Créer un fichier initial
        initial_data = {"version": 1}
        storage.save("backup.json", initial_data)

        # Modifier et sauvegarder
        new_data = {"version": 2}
        storage.save("backup.json", new_data)

        # Vérifier backup
        backup_file = temp_dir / "backup.json.bak"
        assert backup_file.exists()

        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        assert backup_data == initial_data

    def test_backup_disabled(self, storage: JsonStorage, temp_dir: Path):
        """Test désactivation du backup."""
        # Créer un fichier initial
        initial_data = {"version": 1}
        storage.save("nobackup.json", initial_data)

        # Modifier sans backup
        new_data = {"version": 2}
        storage.save("nobackup.json", new_data, backup=False)

        # Vérifier pas de backup
        backup_file = temp_dir / "nobackup.json.bak"
        assert not backup_file.exists()

    def test_corrupted_json_handling(self, storage: JsonStorage, temp_dir: Path):
        """Test gestion des fichiers JSON corrompus."""
        # Créer un fichier corrompu
        corrupted_file = temp_dir / "corrupted.json"
        corrupted_file.write_text("{invalid json", encoding='utf-8')

        # Tenter de charger
        data = storage.load("corrupted.json", default={"fallback": True})
        assert data == {"fallback": True}

    def test_thread_safety(self, storage: JsonStorage):
        """Test thread-safety basique."""
        import threading
        import time

        results = []
        errors = []

        def worker(worker_id: int):
            try:
                # Chaque worker fait plusieurs opérations
                for i in range(10):
                    data = {"worker": worker_id, "operation": i}
                    success = storage.save(f"thread_{worker_id}.json", data)
                    if success:
                        loaded = storage.load(f"thread_{worker_id}.json")
                        if loaded != data:
                            errors.append(f"Data mismatch worker {worker_id}")
                    else:
                        errors.append(f"Save failed worker {worker_id}")
                    time.sleep(0.001)  # Petit délai pour forcer l'entrelacement
                results.append(f"worker_{worker_id}_done")
            except Exception as e:
                errors.append(f"Exception worker {worker_id}: {e}")

        # Lancer plusieurs threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Attendre la fin
        for t in threads:
            t.join()

        # Vérifications
        assert len(results) == 5  # Tous les workers ont terminé
        assert len(errors) == 0  # Aucune erreur

    def test_exists_method(self, storage: JsonStorage):
        """Test méthode exists."""
        assert storage.exists("nonexistent.json") is False

        storage.save("exists.json", {"test": True})
        assert storage.exists("exists.json") is True

    def test_delete_method(self, storage: JsonStorage):
        """Test méthode delete."""
        # Créer puis supprimer
        storage.save("delete.json", {"test": True})
        assert storage.exists("delete.json") is True

        assert storage.delete("delete.json") is True
        assert storage.exists("delete.json") is False

        # Supprimer fichier inexistant
        assert storage.delete("nonexistent.json") is True  # Ne devrait pas échouer

    def test_list_files(self, storage: JsonStorage):
        """Test méthode list_files."""
        # Créer quelques fichiers
        storage.save("test1.json", {"id": 1})
        storage.save("test2.json", {"id": 2})
        storage.save("other.txt", {"not": "json"})  # Ne devrait pas être listé

        json_files = storage.list_files("*.json")
        assert "test1.json" in json_files
        assert "test2.json" in json_files
        assert "other.txt" not in json_files

    def test_unicode_support(self, storage: JsonStorage):
        """Test support Unicode."""
        unicode_data = {
            "french": "café",
            "chinese": "中文",
            "emoji": "🚀",
            "accented": "naïve résumé"
        }

        storage.save("unicode.json", unicode_data)
        loaded = storage.load("unicode.json")
        assert loaded == unicode_data

    @patch('utils.json_storage.os.fsync')
    def test_fsync_called(self, mock_fsync, storage: JsonStorage):
        """Test que fsync est appelé pour forcer l'écriture."""
        test_data = {"test": "fsync"}
        storage.save("fsync.json", test_data)

        # Vérifier que fsync a été appelé
        mock_fsync.assert_called()

    def test_save_failure_cleanup(self, storage: JsonStorage, temp_dir: Path):
        """Test nettoyage en cas d'échec de sauvegarde."""
        # Simuler une erreur pendant l'écriture
        with patch('json.dump', side_effect=OSError("Disk full")):
            result = storage.save("failure.json", {"test": "data"})
            assert result is False

        # Vérifier qu'aucun fichier temporaire n'est laissé
        temp_files = list(temp_dir.glob("failure.json.*.tmp"))
        assert len(temp_files) == 0