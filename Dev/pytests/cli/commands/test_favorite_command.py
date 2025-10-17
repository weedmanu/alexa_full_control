"""
Tests pour la commande CLI Favorite - TDD Approach

Tests de l'interface utilisateur (CLI)
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cli.commands.favorite import FavoriteCommand


class TestFavoriteCommand:
    """Tests pour la commande Favorite."""

    @pytest.fixture
    def mock_adapter(self):
        """Crée un mock du CommandAdapter."""
        adapter = MagicMock()
        return adapter

    @pytest.fixture
    def favorite_command(self, mock_adapter):
        """Crée une instance FavoriteCommand avec mock."""
        with patch("cli.commands.favorite.get_command_adapter", return_value=mock_adapter):
            cmd = FavoriteCommand()
        return cmd

    # =====================================================================
    # Tests: ADD action
    # =====================================================================

    def test_add_favorite_success(self, favorite_command, mock_adapter):
        """Doit ajouter un favori avec succès."""
        mock_service = MagicMock()
        mock_service.add_favorite.return_value = True
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(
            action="add",
            name="BBC Radio 1",
            type="music.tunein",
            params='{"station": "bbc-radio-1"}',
        )

        result = favorite_command.execute(args)

        assert result is True
        mock_service.add_favorite.assert_called_once()

    def test_add_favorite_duplicate_fails(self, favorite_command, mock_adapter):
        """Doit échouer si le favori existe déjà."""
        mock_service = MagicMock()
        mock_service.add_favorite.return_value = False
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(
            action="add",
            name="BBC Radio 1",
            type="music.tunein",
            params='{"station": "bbc-radio-1"}',
        )

        result = favorite_command.execute(args)

        assert result is False

    def test_add_favorite_missing_name(self, favorite_command):
        """Doit échouer si le nom est manquant."""
        args = argparse.Namespace(
            action="add",
            name=None,
            type="music.tunein",
            params='{"station": "bbc-radio-1"}',
        )

        result = favorite_command.execute(args)

        assert result is False

    def test_add_favorite_invalid_json_params(self, favorite_command):
        """Doit échouer si les params JSON sont invalides."""
        args = argparse.Namespace(
            action="add",
            name="BBC Radio 1",
            type="music.tunein",
            params="{ invalid json }",
        )

        result = favorite_command.execute(args)

        assert result is False

    # =====================================================================
    # Tests: LIST action
    # =====================================================================

    def test_list_favorites_empty(self, favorite_command, mock_adapter):
        """Doit afficher liste vide si aucun favori."""
        mock_service = MagicMock()
        mock_service.get_favorites.return_value = {}
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="list", type_filter=None)

        result = favorite_command.execute(args)

        assert result is True

    def test_list_favorites_multiple(self, favorite_command, mock_adapter):
        """Doit lister tous les favoris."""
        mock_service = MagicMock()
        mock_service.get_favorites.return_value = {
            "bbc_radio_1": {
                "name": "BBC Radio 1",
                "type": "music.tunein",
                "params": {"station": "bbc-radio-1"},
            },
            "france_inter": {
                "name": "France Inter",
                "type": "music.tunein",
                "params": {"station": "france-inter"},
            },
        }
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="list", type_filter=None)

        result = favorite_command.execute(args)

        assert result is True

    def test_list_favorites_filter_by_type(self, favorite_command, mock_adapter):
        """Doit filtrer les favoris par type."""
        mock_service = MagicMock()
        mock_service.get_favorites_by_type.return_value = [
            {
                "name": "BBC Radio 1",
                "type": "music.tunein",
                "params": {"station": "bbc-radio-1"},
            }
        ]
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="list", type_filter="music.tunein")

        result = favorite_command.execute(args)

        assert result is True
        mock_service.get_favorites_by_type.assert_called_once_with("music.tunein")

    # =====================================================================
    # Tests: DELETE action
    # =====================================================================

    def test_delete_favorite_success(self, favorite_command, mock_adapter):
        """Doit supprimer un favori."""
        mock_service = MagicMock()
        mock_service.delete_favorite.return_value = True
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="delete", name="BBC Radio 1")

        result = favorite_command.execute(args)

        assert result is True
        mock_service.delete_favorite.assert_called_once_with("BBC Radio 1")

    def test_delete_favorite_not_found(self, favorite_command, mock_adapter):
        """Doit échouer si le favori n'existe pas."""
        mock_service = MagicMock()
        mock_service.delete_favorite.return_value = False
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="delete", name="Non Existant")

        result = favorite_command.execute(args)

        assert result is False

    # =====================================================================
    # Tests: PLAY action
    # =====================================================================

    def test_play_favorite_success(self, favorite_command, mock_adapter):
        """Doit jouer un favori sur un device."""
        mock_favorite_service = MagicMock()
        mock_favorite_service.get_favorite.return_value = {
            "name": "BBC Radio 1",
            "type": "music.tunein",
            "params": {"station": "bbc-radio-1"},
        }

        mock_music_service = MagicMock()
        mock_music_service.play_from_favorite.return_value = True

        def get_manager_side_effect(name):
            if name == "FavoriteManager":
                return mock_favorite_service
            elif name == "PlaybackManager":
                return mock_music_service
            return None

        mock_adapter.get_manager.side_effect = get_manager_side_effect

        args = argparse.Namespace(
            action="play",
            name="BBC Radio 1",
            device="Salon",
            volume=None,
        )

        result = favorite_command.execute(args)

        assert result is True
        mock_favorite_service.get_favorite.assert_called_once_with("BBC Radio 1")

    def test_play_favorite_not_found(self, favorite_command, mock_adapter):
        """Doit échouer si le favori n'existe pas."""
        mock_service = MagicMock()
        mock_service.get_favorite.return_value = None
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(
            action="play",
            name="Non Existant",
            device="Salon",
            volume=None,
        )

        result = favorite_command.execute(args)

        assert result is False

    def test_play_favorite_missing_device(self, favorite_command):
        """Doit échouer si le device est manquant."""
        args = argparse.Namespace(
            action="play",
            name="BBC Radio 1",
            device=None,
            volume=None,
        )

        result = favorite_command.execute(args)

        assert result is False

    # =====================================================================
    # Tests: SHOW action
    # =====================================================================

    def test_show_favorite_success(self, favorite_command, mock_adapter):
        """Doit afficher les détails d'un favori."""
        mock_service = MagicMock()
        mock_service.get_favorite.return_value = {
            "name": "BBC Radio 1",
            "type": "music.tunein",
            "params": {"station": "bbc-radio-1"},
            "created": "2025-10-17T10:30:00",
            "last_used": "2025-10-17T11:00:00",
        }
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="show", name="BBC Radio 1")

        result = favorite_command.execute(args)

        assert result is True

    def test_show_favorite_not_found(self, favorite_command, mock_adapter):
        """Doit échouer si le favori n'existe pas."""
        mock_service = MagicMock()
        mock_service.get_favorite.return_value = None
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="show", name="Non Existant")

        result = favorite_command.execute(args)

        assert result is False

    # =====================================================================
    # Tests: SEARCH action
    # =====================================================================

    def test_search_favorites(self, favorite_command, mock_adapter):
        """Doit chercher des favoris."""
        mock_service = MagicMock()
        mock_service.search_favorites.return_value = [
            {
                "name": "BBC Radio 1",
                "type": "music.tunein",
            },
            {
                "name": "BBC Radio 2",
                "type": "music.tunein",
            },
        ]
        mock_adapter.get_manager.return_value = mock_service

        args = argparse.Namespace(action="search", query="BBC")

        result = favorite_command.execute(args)

        assert result is True
        mock_service.search_favorites.assert_called_once_with("BBC")

    # =====================================================================
    # Tests: INTEGRATION
    # =====================================================================

    def test_command_without_action_fails(self, favorite_command):
        """Doit échouer si aucune action n'est fournie."""
        args = argparse.Namespace()

        result = favorite_command.execute(args)

        assert result is False
