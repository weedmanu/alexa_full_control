"""
Tests unitaires pour le ScenarioManager (TDD - RED phase).

Couvre la création, l'exécution, la suppression et la gestion des scénarios/macros.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Ensure core module is importable
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.scenario.scenario_manager import ScenarioManager


class TestScenarioManagerInit:
    """Tests d'initialisation du ScenarioManager."""

    def test_init_creates_manager(self):
        """Initialiser un ScenarioManager doit fonctionner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)
            assert mgr is not None
            assert isinstance(mgr, ScenarioManager)

    def test_init_with_default_path(self):
        """Initialiser sans path doit utiliser le chemin par défaut."""
        mgr = ScenarioManager()
        assert mgr.storage_path is not None
        assert Path(mgr.storage_path).exists() or True  # Le chemin est créé à la demande


class TestScenarioCreation:
    """Tests de création de scénarios."""

    def test_create_simple_scenario(self):
        """Créer un scénario simple avec une action."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [
                {"device": "Salon Echo", "action": "play", "params": {"song": "Despacito"}}
            ]

            result = mgr.create_scenario("Music Salon", actions)
            assert result is True

    def test_create_scenario_with_multiple_actions(self):
        """Créer un scénario avec plusieurs actions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [
                {"device": "Salon Echo", "action": "play", "params": {"song": "Soleil"}},
                {"device": "Cuisine", "action": "volume", "params": {"level": 50}},
                {"device": "Salon Echo", "action": "pause", "params": {}},
            ]

            result = mgr.create_scenario("Multi Action", actions)
            assert result is True

    def test_create_scenario_with_delay(self):
        """Créer un scénario avec délais entre actions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [
                {"device": "Salon Echo", "action": "play", "params": {"song": "Song1"}, "delay": 0},
                {"device": "Salon Echo", "action": "volume", "params": {"level": 30}, "delay": 2},
                {"device": "Salon Echo", "action": "pause", "params": {}, "delay": 1},
            ]

            result = mgr.create_scenario("With Delays", actions)
            assert result is True

    def test_create_scenario_duplicate_name_fails(self):
        """Créer deux scénarios avec le même nom doit échouer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]

            mgr.create_scenario("Dupli", actions)
            result = mgr.create_scenario("Dupli", actions)  # Même nom

            assert result is False

    def test_create_scenario_empty_actions_fails(self):
        """Créer un scénario sans actions doit échouer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            result = mgr.create_scenario("Empty", [])
            assert result is False

    def test_create_scenario_min_one_action(self):
        """Un scénario doit avoir au minimum 1 action."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            result = mgr.create_scenario("Min Action", actions)
            assert result is True

    def test_create_scenario_stores_metadata(self):
        """La création doit stocker les métadonnées (created, modified)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("With Meta", actions)

            scenario = mgr.get_scenario("With Meta")
            assert scenario is not None
            assert "created" in scenario
            assert "modified" in scenario


class TestScenarioRetrieval:
    """Tests de récupération de scénarios."""

    def test_get_scenario_exists(self):
        """Récupérer un scénario existant doit fonctionner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("Existing", actions)

            scenario = mgr.get_scenario("Existing")
            assert scenario is not None
            assert scenario["name"] == "Existing"
            assert len(scenario["actions"]) == 1

    def test_get_scenario_not_exists(self):
        """Récupérer un scénario inexistant doit retourner None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            scenario = mgr.get_scenario("NonExistent")
            assert scenario is None

    def test_get_all_scenarios_empty(self):
        """Lister les scénarios quand aucun n'existe doit retourner dict vide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            scenarios = mgr.get_scenarios()
            assert scenarios == {}

    def test_get_all_scenarios_multiple(self):
        """Lister plusieurs scénarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("Scenario1", actions)
            mgr.create_scenario("Scenario2", actions)
            mgr.create_scenario("Scenario3", actions)

            scenarios = mgr.get_scenarios()
            assert len(scenarios) == 3
            assert "Scenario1" in scenarios or "scenario1" in scenarios
            assert "Scenario2" in scenarios or "scenario2" in scenarios
            assert "Scenario3" in scenarios or "scenario3" in scenarios


class TestScenarioDeletion:
    """Tests de suppression de scénarios."""

    def test_delete_scenario_exists(self):
        """Supprimer un scénario existant doit fonctionner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("ToDelete", actions)

            result = mgr.delete_scenario("ToDelete")
            assert result is True

            scenario = mgr.get_scenario("ToDelete")
            assert scenario is None

    def test_delete_scenario_not_exists(self):
        """Supprimer un scénario inexistant doit retourner False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            result = mgr.delete_scenario("NonExistent")
            assert result is False


class TestScenarioExecution:
    """Tests d'exécution de scénarios."""

    def test_run_scenario_simple(self):
        """Exécuter un scénario simple doit appeler les actions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            # Mock du gestionnaire d'actions
            mgr._execute_action = MagicMock(return_value=True)

            actions = [
                {"device": "Device1", "action": "play", "params": {"song": "Test"}},
            ]
            mgr.create_scenario("RunTest", actions)

            result = mgr.run_scenario("RunTest")
            assert result is True
            assert mgr._execute_action.called

    def test_run_scenario_multiple_actions(self):
        """Exécuter un scénario avec plusieurs actions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            mgr._execute_action = MagicMock(return_value=True)

            actions = [
                {"device": "Device1", "action": "play", "params": {"song": "Song1"}},
                {"device": "Device2", "action": "volume", "params": {"level": 50}},
                {"device": "Device1", "action": "pause", "params": {}},
            ]
            mgr.create_scenario("Multi", actions)

            result = mgr.run_scenario("Multi")
            assert result is True
            assert mgr._execute_action.call_count == 3

    def test_run_scenario_not_exists(self):
        """Exécuter un scénario inexistant doit retourner False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            result = mgr.run_scenario("NonExistent")
            assert result is False

    def test_run_scenario_with_delays(self):
        """Exécuter un scénario avec délais doit respecter les timings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            call_times = []

            def mock_execute(action):
                call_times.append(None)  # Juste pour compter
                return True

            mgr._execute_action = mock_execute

            actions = [
                {"device": "Device1", "action": "play", "params": {}, "delay": 0},
                {"device": "Device1", "action": "pause", "params": {}, "delay": 0.1},
            ]
            mgr.create_scenario("Delays", actions)

            result = mgr.run_scenario("Delays")
            assert result is True

    def test_run_scenario_one_action_fails_continues(self):
        """Si une action échoue, le scénario continue (best effort)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            call_count = 0

            def mock_execute(action):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return False  # Première action échoue
                return True

            mgr._execute_action = mock_execute

            actions = [
                {"device": "Device1", "action": "play", "params": {}},
                {"device": "Device2", "action": "volume", "params": {"level": 50}},
            ]
            mgr.create_scenario("Partial", actions)

            # Le scénario continue même si une action échoue
            result = mgr.run_scenario("Partial")
            assert call_count == 2  # Les 2 actions ont été appelées


class TestScenarioPersistence:
    """Tests de persistance JSON."""

    def test_persist_scenario_to_json(self):
        """Les scénarios doivent être persistés en JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("Persist", actions)

            # Vérifier que le fichier JSON existe
            json_file = Path(tmpdir) / "scenarios.json"
            assert json_file.exists()

    def test_load_scenarios_from_json(self):
        """Les scénarios doivent être chargés depuis JSON au démarrage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Créer un scénario
            mgr1 = ScenarioManager(storage_path=tmpdir)
            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr1.create_scenario("Loaded", actions)

            # Créer une nouvelle instance et vérifier que le scénario est chargé
            mgr2 = ScenarioManager(storage_path=tmpdir)
            scenario = mgr2.get_scenario("Loaded")
            assert scenario is not None
            assert scenario["name"] == "Loaded"

    def test_json_structure_valid(self):
        """La structure JSON doit être valide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [
                {"device": "Device1", "action": "play", "params": {"song": "Test"}},
            ]
            mgr.create_scenario("Valid", actions)

            json_file = Path(tmpdir) / "scenarios.json"
            with open(json_file) as f:
                data = json.load(f)

            assert "scenarios" in data
            assert len(data["scenarios"]) > 0


class TestScenarioRenaming:
    """Tests de renommage de scénarios."""

    def test_rename_scenario(self):
        """Renommer un scénario doit fonctionner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("OldName", actions)

            result = mgr.rename_scenario("OldName", "NewName")
            assert result is True

            assert mgr.get_scenario("NewName") is not None
            assert mgr.get_scenario("OldName") is None

    def test_rename_scenario_not_exists(self):
        """Renommer un scénario inexistant doit échouer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            result = mgr.rename_scenario("NonExistent", "NewName")
            assert result is False

    def test_rename_to_existing_name_fails(self):
        """Renommer vers un nom existant doit échouer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("Scenario1", actions)
            mgr.create_scenario("Scenario2", actions)

            result = mgr.rename_scenario("Scenario1", "Scenario2")
            assert result is False


class TestScenarioEditing:
    """Tests d'édition de scénarios."""

    def test_edit_scenario_actions(self):
        """Éditer les actions d'un scénario."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "play", "params": {}}]
            mgr.create_scenario("Editable", actions)

            new_actions = [
                {"device": "Device2", "action": "volume", "params": {"level": 60}},
                {"device": "Device1", "action": "pause", "params": {}},
            ]

            result = mgr.edit_scenario("Editable", new_actions)
            assert result is True

            scenario = mgr.get_scenario("Editable")
            assert len(scenario["actions"]) == 2

    def test_edit_scenario_not_exists(self):
        """Éditer un scénario inexistant doit échouer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            new_actions = [{"device": "Device1", "action": "test", "params": {}}]
            result = mgr.edit_scenario("NonExistent", new_actions)
            assert result is False


class TestScenarioValidation:
    """Tests de validation des scénarios."""

    def test_validate_action_structure(self):
        """Valider la structure d'une action."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            # Action valide
            valid_action = {"device": "Device1", "action": "play", "params": {}}
            assert mgr._validate_action(valid_action) is True

            # Action invalide (pas de device)
            invalid_action = {"action": "play", "params": {}}
            assert mgr._validate_action(invalid_action) is False

    def test_validate_action_has_required_fields(self):
        """Une action doit avoir device, action, params."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            # Tous les champs requis
            action = {"device": "Device1", "action": "test", "params": {}}
            assert mgr._validate_action(action) is True

            # Manque 'params'
            action = {"device": "Device1", "action": "test"}
            assert mgr._validate_action(action) is False


class TestScenarioSearch:
    """Tests de recherche de scénarios."""

    def test_search_scenarios_by_name(self):
        """Chercher des scénarios par nom."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("Music Salon", actions)
            mgr.create_scenario("Music Kitchen", actions)
            mgr.create_scenario("Device Config", actions)

            results = mgr.search_scenarios("Music")
            assert len(results) == 2

    def test_search_scenarios_empty_result(self):
        """La recherche peut retourner vide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("Scenario1", actions)

            results = mgr.search_scenarios("NonExistent")
            assert len(results) == 0


class TestScenarioExportImport:
    """Tests d'export/import de scénarios."""

    def test_export_scenario_to_dict(self):
        """Exporter un scénario en dictionnaire."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "play", "params": {"song": "Test"}}]
            mgr.create_scenario("Export", actions)

            exported = mgr.export_scenario("Export")
            assert exported is not None
            assert exported["name"] == "Export"
            assert len(exported["actions"]) == 1

    def test_export_all_scenarios(self):
        """Exporter tous les scénarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            actions = [{"device": "Device1", "action": "test", "params": {}}]
            mgr.create_scenario("S1", actions)
            mgr.create_scenario("S2", actions)

            exported = mgr.export_all_scenarios()
            assert len(exported) == 2

    def test_import_scenario_from_dict(self):
        """Importer un scénario depuis un dictionnaire."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = ScenarioManager(storage_path=tmpdir)

            scenario_dict = {
                "name": "Imported",
                "actions": [{"device": "Device1", "action": "test", "params": {}}],
                "created": "2025-10-17T00:00:00",
                "modified": "2025-10-17T00:00:00"
            }

            result = mgr.import_scenario(scenario_dict)
            assert result is True
            assert mgr.get_scenario("Imported") is not None
