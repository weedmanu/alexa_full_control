"""
Tests pour Multiroom Manager - TDD Approach

Permet de grouper les appareils et exécuter commandes sur le groupe.
"""

import json
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from core.multiroom.multiroom_manager import MultiRoomManager


class TestMultiRoomManager:
    """Tests pour MultiRoomManager."""

    @pytest.fixture
    def temp_config_dir(self):
        """Crée un répertoire temporaire."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def multiroom_manager(self, temp_config_dir):
        """Crée une instance MultiRoomManager."""
        manager = MultiRoomManager(config_dir=temp_config_dir)
        return manager

    # =====================================================================
    # Tests: CRÉER un groupe
    # =====================================================================

    def test_create_group_success(self, multiroom_manager):
        """Doit créer un groupe multiroom."""
        result = multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2", "serial3"],
        )

        assert result is True

    def test_create_group_duplicate_fails(self, multiroom_manager):
        """Doit échouer si le groupe existe déjà."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        # Essayer de créer le même groupe
        result = multiroom_manager.create_group(
            name="Living Room",
            devices=["serial3", "serial4"],
        )

        assert result is False

    def test_create_group_empty_name_fails(self, multiroom_manager):
        """Doit échouer si le nom est vide."""
        result = multiroom_manager.create_group(
            name="",
            devices=["serial1"],
        )

        assert result is False

    def test_create_group_no_devices_fails(self, multiroom_manager):
        """Doit échouer si pas d'appareils."""
        result = multiroom_manager.create_group(
            name="Living Room",
            devices=[],
        )

        assert result is False

    def test_create_group_single_device_fails(self, multiroom_manager):
        """Doit échouer si un seul appareil."""
        result = multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1"],
        )

        assert result is False

    # =====================================================================
    # Tests: RÉCUPÉRER groupes
    # =====================================================================

    def test_get_groups_empty(self, multiroom_manager):
        """Doit retourner liste vide si aucun groupe."""
        groups = multiroom_manager.get_groups()

        assert groups == {}

    def test_get_groups_single(self, multiroom_manager):
        """Doit retourner un groupe créé."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        groups = multiroom_manager.get_groups()

        assert len(groups) == 1
        assert "living_room" in groups

    def test_get_groups_multiple(self, multiroom_manager):
        """Doit retourner tous les groupes."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )
        multiroom_manager.create_group(
            name="Kitchen",
            devices=["serial3", "serial4"],
        )

        groups = multiroom_manager.get_groups()

        assert len(groups) == 2
        assert "living_room" in groups
        assert "kitchen" in groups

    def test_get_group_by_name(self, multiroom_manager):
        """Doit récupérer un groupe par son nom."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        group = multiroom_manager.get_group("Living Room")

        assert group is not None
        assert group["name"] == "Living Room"
        assert len(group["devices"]) == 2

    def test_get_group_not_found(self, multiroom_manager):
        """Doit retourner None si le groupe n'existe pas."""
        group = multiroom_manager.get_group("Non Existant")

        assert group is None

    # =====================================================================
    # Tests: SUPPRIMER un groupe
    # =====================================================================

    def test_delete_group_success(self, multiroom_manager):
        """Doit supprimer un groupe."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        result = multiroom_manager.delete_group("Living Room")

        assert result is True
        assert multiroom_manager.get_group("Living Room") is None

    def test_delete_group_not_found(self, multiroom_manager):
        """Doit échouer si le groupe n'existe pas."""
        result = multiroom_manager.delete_group("Non Existant")

        assert result is False

    # =====================================================================
    # Tests: AJOUTER device au groupe
    # =====================================================================

    def test_add_device_to_group_success(self, multiroom_manager):
        """Doit ajouter un appareil au groupe."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        result = multiroom_manager.add_device_to_group("Living Room", "serial3")

        assert result is True
        group = multiroom_manager.get_group("Living Room")
        assert len(group["devices"]) == 3
        assert "serial3" in group["devices"]

    def test_add_device_group_not_found(self, multiroom_manager):
        """Doit échouer si le groupe n'existe pas."""
        result = multiroom_manager.add_device_to_group("Non Existant", "serial1")

        assert result is False

    def test_add_device_already_in_group(self, multiroom_manager):
        """Doit échouer si l'appareil est déjà dans le groupe."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        result = multiroom_manager.add_device_to_group("Living Room", "serial1")

        assert result is False

    # =====================================================================
    # Tests: RETIRER device du groupe
    # =====================================================================

    def test_remove_device_from_group_success(self, multiroom_manager):
        """Doit retirer un appareil du groupe."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2", "serial3"],
        )

        result = multiroom_manager.remove_device_from_group("Living Room", "serial2")

        assert result is True
        group = multiroom_manager.get_group("Living Room")
        assert len(group["devices"]) == 2
        assert "serial2" not in group["devices"]

    def test_remove_device_group_not_found(self, multiroom_manager):
        """Doit échouer si le groupe n'existe pas."""
        result = multiroom_manager.remove_device_from_group("Non Existant", "serial1")

        assert result is False

    def test_remove_device_not_in_group(self, multiroom_manager):
        """Doit échouer si l'appareil n'est pas dans le groupe."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        result = multiroom_manager.remove_device_from_group("Living Room", "serial3")

        assert result is False

    # =====================================================================
    # Tests: PERSISTENCE
    # =====================================================================

    def test_save_and_load_groups(self, multiroom_manager, temp_config_dir):
        """Doit sauvegarder et recharger les groupes."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        # Sauvegarder
        multiroom_manager.save_groups()

        # Créer nouvelle instance
        new_manager = MultiRoomManager(config_dir=temp_config_dir)

        # Vérifier que le groupe a été chargé
        group = new_manager.get_group("Living Room")
        assert group is not None
        assert len(group["devices"]) == 2

    # =====================================================================
    # Tests: RENAME groupe
    # =====================================================================

    def test_rename_group_success(self, multiroom_manager):
        """Doit renommer un groupe."""
        multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        result = multiroom_manager.rename_group("Living Room", "Great Room")

        assert result is True
        assert multiroom_manager.get_group("Living Room") is None
        assert multiroom_manager.get_group("Great Room") is not None

    def test_rename_group_not_found(self, multiroom_manager):
        """Doit échouer si le groupe n'existe pas."""
        result = multiroom_manager.rename_group("Non Existant", "New Name")

        assert result is False

    # =====================================================================
    # Tests: INTEGRATION
    # =====================================================================

    def test_full_workflow(self, multiroom_manager):
        """Test un workflow complet."""
        # Créer groupe
        assert multiroom_manager.create_group(
            name="Living Room",
            devices=["serial1", "serial2"],
        )

        # Ajouter device
        assert multiroom_manager.add_device_to_group("Living Room", "serial3")

        # Vérifier contenu
        group = multiroom_manager.get_group("Living Room")
        assert len(group["devices"]) == 3

        # Retirer device
        assert multiroom_manager.remove_device_from_group("Living Room", "serial1")

        # Vérifier contenu mis à jour
        group = multiroom_manager.get_group("Living Room")
        assert len(group["devices"]) == 2

        # Renommer
        assert multiroom_manager.rename_group("Living Room", "Great Room")

        # Supprimer
        assert multiroom_manager.delete_group("Great Room")
        assert multiroom_manager.get_group("Great Room") is None
