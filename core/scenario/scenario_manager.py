"""
Gestionnaire des scénarios/macros Alexa (TDD - GREEN phase).

Permet de créer, exécuter, lister et gérer des séquences de commandes.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


class ScenarioManager:
    """Gestionnaire des scénarios/macros pour Alexa."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        """
        Initialise le gestionnaire de scénarios.

        Args:
            storage_path: Chemin personnalisé de stockage (défaut: ~/.alexa/)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".alexa"

        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.json_file = self.storage_path / "scenarios.json"
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._load_scenarios()

    def _load_scenarios(self) -> None:
        """Charge les scénarios depuis le fichier JSON."""
        if self.json_file.exists():
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "scenarios" in data:
                        for scenario in data["scenarios"]:
                            name = scenario.get("name", "").lower()
                            self._scenarios[name] = scenario
                logger.debug(f"Chargé {len(self._scenarios)} scénarios depuis JSON")
            except Exception as e:
                logger.error(f"Erreur lors du chargement des scénarios: {e}")
                self._scenarios = {}
        else:
            self._scenarios = {}

    def _save_scenarios(self) -> None:
        """Sauvegarde les scénarios dans le fichier JSON."""
        try:
            data = {"scenarios": list(self._scenarios.values())}
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Scénarios sauvegardés ({len(self._scenarios)} scénarios)")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des scénarios: {e}")

    def _normalize_name(self, name: str) -> str:
        """Normalise le nom d'un scénario (lowercase)."""
        return name.lower().strip()

    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """
        Valide la structure d'une action.

        Args:
            action: Action à valider

        Returns:
            True si valide, False sinon
        """
        required_keys = {"device", "action", "params"}
        return isinstance(action, dict) and required_keys.issubset(action.keys())

    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Exécute une action d'un scénario (stub).

        Args:
            action: Action à exécuter

        Returns:
            True si succès, False sinon
        """
        # Cette méthode sera override par les tests/CLI
        logger.debug(f"Exécution action: {action.get('action')} sur {action.get('device')}")
        return True

    def create_scenario(self, name: str, actions: List[Dict[str, Any]]) -> bool:
        """
        Crée un nouveau scénario.

        Args:
            name: Nom du scénario
            actions: Liste des actions à exécuter

        Returns:
            True si création réussie, False sinon
        """
        # Validation
        if not name or not actions:
            logger.warning("Scénario: name et actions sont requis")
            return False

        if len(actions) == 0:
            logger.warning("Un scénario doit avoir au moins 1 action")
            return False

        # Vérifier que toutes les actions sont valides
        for action in actions:
            if not self._validate_action(action):
                logger.warning(f"Action invalide: {action}")
                return False

        # Vérifier les doublons
        normalized = self._normalize_name(name)
        if normalized in self._scenarios:
            logger.warning(f"Scénario '{name}' existe déjà")
            return False

        # Créer le scénario
        now = datetime.now().isoformat()
        scenario = {
            "name": name,
            "actions": actions,
            "created": now,
            "modified": now,
        }

        self._scenarios[normalized] = scenario
        self._save_scenarios()
        logger.info(f"Scénario '{name}' créé avec {len(actions)} action(s)")
        return True

    def get_scenario(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un scénario par son nom.

        Args:
            name: Nom du scénario

        Returns:
            Dictionnaire du scénario ou None
        """
        normalized = self._normalize_name(name)
        return self._scenarios.get(normalized)

    def get_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère tous les scénarios.

        Returns:
            Dictionnaire {normalized_name: scenario_data}
        """
        return self._scenarios

    def delete_scenario(self, name: str) -> bool:
        """
        Supprime un scénario.

        Args:
            name: Nom du scénario à supprimer

        Returns:
            True si suppression réussie, False sinon
        """
        normalized = self._normalize_name(name)
        if normalized not in self._scenarios:
            logger.warning(f"Scénario '{name}' non trouvé")
            return False

        del self._scenarios[normalized]
        self._save_scenarios()
        logger.info(f"Scénario '{name}' supprimé")
        return True

    def run_scenario(self, name: str, auth: Optional[Any] = None) -> bool:
        """
        Exécute un scénario.

        Args:
            name: Nom du scénario à exécuter
            auth: Authentification (optionnel)

        Returns:
            True si exécution complète, False si erreur critique
        """
        scenario = self.get_scenario(name)
        if not scenario:
            logger.warning(f"Scénario '{name}' non trouvé")
            return False

        actions = scenario.get("actions", [])
        if not actions:
            logger.warning(f"Scénario '{name}' a aucune action")
            return False

        logger.info(f"Exécution scénario '{name}' ({len(actions)} action(s))...")

        # Exécuter toutes les actions (best effort - continue même si une échoue)
        for i, action in enumerate(actions, 1):
            # Respecter les délais
            delay = action.get("delay", 0)
            if delay > 0:
                logger.debug(f"  Attente {delay}s avant action {i}")
                time.sleep(delay)

            # Exécuter l'action
            try:
                result = self._execute_action(action)
                status = "✅" if result else "⚠️"
                logger.debug(f"  {status} Action {i}: {action.get('action')} sur {action.get('device')}")
            except Exception as e:
                logger.warning(f"  ❌ Action {i} échouée: {e}")
                # Continue avec la prochaine action

        logger.info(f"Scénario '{name}' exécuté")
        return True

    def rename_scenario(self, old_name: str, new_name: str) -> bool:
        """
        Renomme un scénario.

        Args:
            old_name: Ancien nom
            new_name: Nouveau nom

        Returns:
            True si renommage réussi, False sinon
        """
        old_normalized = self._normalize_name(old_name)
        new_normalized = self._normalize_name(new_name)

        if old_normalized not in self._scenarios:
            logger.warning(f"Scénario '{old_name}' non trouvé")
            return False

        if new_normalized in self._scenarios and new_normalized != old_normalized:
            logger.warning(f"Scénario '{new_name}' existe déjà")
            return False

        scenario = self._scenarios[old_normalized]
        scenario["name"] = new_name
        scenario["modified"] = datetime.now().isoformat()

        del self._scenarios[old_normalized]
        self._scenarios[new_normalized] = scenario
        self._save_scenarios()

        logger.info(f"Scénario renommé '{old_name}' → '{new_name}'")
        return True

    def edit_scenario(self, name: str, new_actions: List[Dict[str, Any]]) -> bool:
        """
        Édite les actions d'un scénario.

        Args:
            name: Nom du scénario
            new_actions: Nouvelle liste d'actions

        Returns:
            True si édition réussie, False sinon
        """
        if not new_actions:
            logger.warning("Au moins 1 action est requise")
            return False

        # Valider toutes les actions
        for action in new_actions:
            if not self._validate_action(action):
                logger.warning(f"Action invalide: {action}")
                return False

        scenario = self.get_scenario(name)
        if not scenario:
            logger.warning(f"Scénario '{name}' non trouvé")
            return False

        normalized = self._normalize_name(name)
        scenario["actions"] = new_actions
        scenario["modified"] = datetime.now().isoformat()
        self._scenarios[normalized] = scenario
        self._save_scenarios()

        logger.info(f"Scénario '{name}' édité ({len(new_actions)} action(s))")
        return True

    def search_scenarios(self, query: str) -> List[Dict[str, Any]]:
        """
        Cherche des scénarios par nom.

        Args:
            query: Terme de recherche

        Returns:
            Liste des scénarios correspondants
        """
        query_lower = query.lower()
        results = [
            scenario
            for scenario in self._scenarios.values()
            if query_lower in scenario.get("name", "").lower()
        ]
        logger.debug(f"Recherche '{query}': {len(results)} résultat(s)")
        return results

    def export_scenario(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Exporte un scénario en dictionnaire.

        Args:
            name: Nom du scénario

        Returns:
            Dictionnaire du scénario ou None
        """
        scenario = self.get_scenario(name)
        if not scenario:
            logger.warning(f"Scénario '{name}' non trouvé")
            return None

        return scenario.copy()

    def export_all_scenarios(self) -> List[Dict[str, Any]]:
        """
        Exporte tous les scénarios.

        Returns:
            Liste de tous les scénarios
        """
        return list(self._scenarios.values())

    def import_scenario(self, scenario_dict: Dict[str, Any]) -> bool:
        """
        Importe un scénario depuis un dictionnaire.

        Args:
            scenario_dict: Dictionnaire représentant un scénario

        Returns:
            True si importation réussie, False sinon
        """
        if not isinstance(scenario_dict, dict):
            logger.warning("scenario_dict doit être un dictionnaire")
            return False

        name = scenario_dict.get("name")
        actions = scenario_dict.get("actions")

        if not name or not actions:
            logger.warning("Scenario doit avoir 'name' et 'actions'")
            return False

        # Vérifier le format des actions
        for action in actions:
            if not self._validate_action(action):
                logger.warning(f"Action invalide dans import: {action}")
                return False

        # Créer le scénario
        normalized = self._normalize_name(name)
        if normalized in self._scenarios:
            logger.warning(f"Scénario '{name}' existe déjà")
            return False

        scenario = {
            "name": name,
            "actions": actions,
            "created": scenario_dict.get("created", datetime.now().isoformat()),
            "modified": scenario_dict.get("modified", datetime.now().isoformat()),
        }

        self._scenarios[normalized] = scenario
        self._save_scenarios()
        logger.info(f"Scénario '{name}' importé")
        return True
