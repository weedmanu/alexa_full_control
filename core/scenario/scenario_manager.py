"""
Gestionnaire des scénarios/macros Alexa (TDD - GREEN phase).

Permet de créer, exécuter, lister et gérer des séquences de commandes.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from core.base_persistence_manager import BasePersistenceManager

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.base import ResponseDTO
    HAS_SCENARIO_DTO = True
except ImportError:
    HAS_SCENARIO_DTO = False


class ScenarioManager(BasePersistenceManager):
    """Gestionnaire des scénarios/macros pour Alexa."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        """
        Initialise le gestionnaire de scénarios.

        Args:
            storage_path: Chemin personnalisé de stockage (défaut: ~/.alexa/)
        """
        config_dir = Path(storage_path) if storage_path else None
        super().__init__("scenarios.json", config_dir)

    @property
    def storage_path(self) -> str:
        """Chemin de stockage pour compatibilité."""
        return str(self.storage.base_dir)

    def _load_data(self) -> None:
        """Charge les scénarios depuis le fichier JSON avec format spécial."""
        raw_data = self.storage.load(self.storage_key, default={"scenarios": []})
        self._data = {}

        if isinstance(raw_data, dict) and "scenarios" in raw_data:
            for scenario in raw_data["scenarios"]:
                if isinstance(scenario, dict) and "name" in scenario:
                    name = scenario["name"].lower()
                    self._data[name] = scenario

        logger.debug(f"Chargé {len(self._data)} scénarios depuis JSON")

    def _save_data(self) -> bool:
        """Sauvegarde les scénarios dans le fichier JSON avec format spécial."""
        data = {"scenarios": list(self._data.values())}
        return self.storage.save(self.storage_key, data)

    def _validate_item(self, item: Dict[str, Any]) -> bool:
        """
        Valide la structure d'un scénario.

        Args:
            item: Scénario à valider

        Returns:
            True si valide, False sinon
        """
        required_keys = {"name", "actions"}
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            return False

        # Valider les actions
        actions = item.get("actions", [])
        if not isinstance(actions, list):
            return False

        for action in actions:
            if not self._validate_action(action):
                return False

        return True

    def _create_item(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Crée un nouvel élément scénario.

        Args:
            name: Nom du scénario
            **kwargs: Doit contenir 'actions'

        Returns:
            Scénario créé
        """
        actions = kwargs.get("actions", [])
        return {
            "name": name,
            "actions": actions,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
        }

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

        # Utiliser BasePersistenceManager pour ajouter
        return self.add_item(name, actions=actions)

    def get_scenario(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un scénario par son nom.

        Args:
            name: Nom du scénario

        Returns:
            Dictionnaire du scénario ou None
        """
        return self.get_item(name)

    def get_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère tous les scénarios.

        Returns:
            Dictionnaire {normalized_name: scenario_data}
        """
        return self.get_all_items()

    def delete_scenario(self, name: str) -> bool:
        """
        Supprime un scénario.

        Args:
            name: Nom du scénario à supprimer

        Returns:
            True si suppression réussie, False sinon
        """
        return self.remove_item(name)

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
        # Récupérer l'ancien scénario
        old_scenario = self.get_item(old_name)
        if not old_scenario:
            logger.warning(f"Scénario '{old_name}' non trouvé")
            return False

        # Vérifier que le nouveau nom n'existe pas
        if self.item_exists(new_name):
            logger.warning(f"Scénario '{new_name}' existe déjà")
            return False

        # Créer le nouveau scénario avec le nouveau nom
        old_scenario["name"] = new_name
        old_scenario["modified"] = datetime.now().isoformat()

        # Supprimer l'ancien et ajouter le nouveau
        if not self.remove_item(old_name):
            return False

        return self.add_item(new_name, **{"actions": old_scenario["actions"]})

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

        # Mettre à jour via BasePersistenceManager
        return self.update_item(name, actions=new_actions, modified=datetime.now().isoformat())

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
            scenario for scenario in self.get_all_items().values() if query_lower in scenario.get("name", "").lower()
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
        return list(self.get_all_items().values())

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

        # Vérifier que le scénario n'existe pas déjà
        if self.item_exists(name):
            logger.warning(f"Scénario '{name}' existe déjà")
            return False

        # Créer le scénario
        return self.add_item(name, actions=actions)
