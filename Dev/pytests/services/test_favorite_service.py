"""
Tests pour le service Favorite - TDD Approach

Stratégie:
1. Écrire les tests d'abord
2. Les tests vont échouer (Red)
3. Implémenter le service (Green)
4. Refactoriser (Refactor)
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.favorite_service import FavoriteService


class TestFavoriteService:
    """Tests pour FavoriteService."""

    @pytest.fixture
    def temp_config_dir(self):
        """Crée un répertoire temporaire pour les favoris."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def favorite_service(self, temp_config_dir):
        """Crée une instance FavoriteService avec un répertoire temporaire."""
        service = FavoriteService(config_dir=temp_config_dir)
        return service

    # =====================================================================
    # Tests: AJOUTER un favori
    # =====================================================================

    def test_add_favorite_new(self, favorite_service):
        """Doit ajouter un nouveau favori."""
        result = favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        assert result is True

    def test_add_favorite_duplicate_fails(self, favorite_service):
        """Doit échouer si le favori existe déjà."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        # Essayer d'ajouter le même favori
        result = favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        assert result is False

    def test_add_favorite_empty_name_fails(self, favorite_service):
        """Doit échouer si le nom est vide."""
        result = favorite_service.add_favorite(
            name="",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        assert result is False

    def test_add_favorite_invalid_type_fails(self, favorite_service):
        """Doit échouer si le type est invalide."""
        result = favorite_service.add_favorite(
            name="Test",
            favorite_type="",
            params={},
        )

        assert result is False

    # =====================================================================
    # Tests: RÉCUPÉRER favoris
    # =====================================================================

    def test_get_favorites_empty(self, favorite_service):
        """Doit retourner liste vide si aucun favori."""
        favorites = favorite_service.get_favorites()

        assert favorites == {}

    def test_get_favorites_single(self, favorite_service):
        """Doit retourner un favori ajouté."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        favorites = favorite_service.get_favorites()

        assert len(favorites) == 1
        assert "bbc_radio_1" in favorites
        assert favorites["bbc_radio_1"]["name"] == "BBC Radio 1"
        assert favorites["bbc_radio_1"]["type"] == "music.tunein"

    def test_get_favorites_multiple(self, favorite_service):
        """Doit retourner tous les favoris."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )
        favorite_service.add_favorite(
            name="France Inter",
            favorite_type="music.tunein",
            params={"station": "france-inter"},
        )

        favorites = favorite_service.get_favorites()

        assert len(favorites) == 2
        assert "bbc_radio_1" in favorites
        assert "france_inter" in favorites

    def test_get_favorite_by_name(self, favorite_service):
        """Doit récupérer un favori par son nom."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        favorite = favorite_service.get_favorite("BBC Radio 1")

        assert favorite is not None
        assert favorite["name"] == "BBC Radio 1"

    def test_get_favorite_not_found(self, favorite_service):
        """Doit retourner None si le favori n'existe pas."""
        favorite = favorite_service.get_favorite("Non Existant")

        assert favorite is None

    # =====================================================================
    # Tests: SUPPRIMER un favori
    # =====================================================================

    def test_delete_favorite_success(self, favorite_service):
        """Doit supprimer un favori existant."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        result = favorite_service.delete_favorite("BBC Radio 1")

        assert result is True
        assert favorite_service.get_favorite("BBC Radio 1") is None

    def test_delete_favorite_not_found(self, favorite_service):
        """Doit échouer si le favori n'existe pas."""
        result = favorite_service.delete_favorite("Non Existant")

        assert result is False

    # =====================================================================
    # Tests: LISTER favoris par type
    # =====================================================================

    def test_get_favorites_by_type(self, favorite_service):
        """Doit filtrer les favoris par type."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )
        favorite_service.add_favorite(
            name="Scene Salon",
            favorite_type="scene",
            params={"scene_id": "scene-123"},
        )

        music_favorites = favorite_service.get_favorites_by_type("music.tunein")

        assert len(music_favorites) == 1
        assert music_favorites[0]["name"] == "BBC Radio 1"

    # =====================================================================
    # Tests: PERSISTENCE (Sauvegarde/Chargement)
    # =====================================================================

    def test_save_and_load_favorites(self, favorite_service, temp_config_dir):
        """Doit sauvegarder et recharger les favoris."""
        # Ajouter favoris
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        # Sauvegarder
        favorite_service.save_favorites()

        # Créer nouvelle instance (simule restart)
        new_service = FavoriteService(config_dir=temp_config_dir)

        # Vérifier que le favori a été chargé
        favorites = new_service.get_favorites()
        assert len(favorites) == 1
        assert "bbc_radio_1" in favorites

    def test_favorites_file_corrupted(self, favorite_service, temp_config_dir):
        """Doit gérer un fichier de favoris corrompu."""
        # Créer un fichier corrompu
        favorites_file = temp_config_dir / "favorites.json"
        favorites_file.write_text("{ invalid json }")

        # Créer nouvelle instance (doit ne pas crash)
        new_service = FavoriteService(config_dir=temp_config_dir)

        # Doit avoir des favoris vides
        favorites = new_service.get_favorites()
        assert favorites == {}

    # =====================================================================
    # Tests: RECHERCHE
    # =====================================================================

    def test_search_favorites_by_name(self, favorite_service):
        """Doit chercher des favoris par nom."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )
        favorite_service.add_favorite(
            name="BBC Radio 2",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-2"},
        )

        results = favorite_service.search_favorites("BBC")

        assert len(results) == 2

    def test_search_favorites_no_match(self, favorite_service):
        """Doit retourner liste vide si pas de match."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        results = favorite_service.search_favorites("France")

        assert len(results) == 0

    # =====================================================================
    # Tests: UPDATE/MODIFICATION
    # =====================================================================

    def test_update_favorite(self, favorite_service):
        """Doit pouvoir modifier un favori."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        result = favorite_service.update_favorite(
            name="BBC Radio 1",
            params={"station": "bbc-radio-1-hd"},
        )

        assert result is True
        favorite = favorite_service.get_favorite("BBC Radio 1")
        assert favorite["params"]["station"] == "bbc-radio-1-hd"

    def test_update_nonexistent_favorite(self, favorite_service):
        """Doit échouer si le favori n'existe pas."""
        result = favorite_service.update_favorite(
            name="Non Existant",
            params={},
        )

        assert result is False

    # =====================================================================
    # Tests: EXPORT/IMPORT
    # =====================================================================

    def test_export_favorites_json(self, favorite_service):
        """Doit pouvoir exporter les favoris en JSON."""
        favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        json_data = favorite_service.export_to_json()

        assert json_data is not None
        parsed = json.loads(json_data)
        assert "bbc_radio_1" in parsed

    def test_import_favorites_json(self, favorite_service):
        """Doit pouvoir importer des favoris depuis JSON."""
        json_data = json.dumps(
            {
                "bbc_radio_1": {
                    "name": "BBC Radio 1",
                    "type": "music.tunein",
                    "params": {"station": "bbc-radio-1"},
                }
            }
        )

        result = favorite_service.import_from_json(json_data)

        assert result is True
        favorite = favorite_service.get_favorite("BBC Radio 1")
        assert favorite is not None

    # =====================================================================
    # Tests: TOTAL USAGE (Intégration)
    # =====================================================================

    def test_full_workflow(self, favorite_service):
        """Test un workflow complet: add → get → update → delete."""
        # Ajouter
        assert favorite_service.add_favorite(
            name="BBC Radio 1",
            favorite_type="music.tunein",
            params={"station": "bbc-radio-1"},
        )

        # Récupérer
        favorite = favorite_service.get_favorite("BBC Radio 1")
        assert favorite is not None

        # Modifier
        assert favorite_service.update_favorite(
            name="BBC Radio 1",
            params={"station": "bbc-radio-1-hd"},
        )

        # Vérifier modification
        updated = favorite_service.get_favorite("BBC Radio 1")
        assert updated["params"]["station"] == "bbc-radio-1-hd"

        # Supprimer
        assert favorite_service.delete_favorite("BBC Radio 1")

        # Vérifier suppression
        assert favorite_service.get_favorite("BBC Radio 1") is None
