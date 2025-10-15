"""
Gestionnaire de listes (courses, tâches) - Thread-safe.
Utilise des commandes vocales (TextCommand) pour gérer les listes.
"""

import threading
from typing import Any, Dict, List, Optional

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class ListsManager:
    """Gestionnaire thread-safe des listes via commandes vocales."""

    def __init__(self, auth, config, state_machine=None, voice_service=None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        self._voice_service = voice_service
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth
        logger.info("ListManager initialisé (mode commandes vocales)")

    @property
    def voice_service(self):
        """Lazy loading du VoiceCommandService."""
        if self._voice_service is None:
            from services.voice_command_service import VoiceCommandService

            self._voice_service = VoiceCommandService(self.auth, self.config, self.state_machine)
        return self._voice_service

    def get_lists(self) -> List[Dict]:
        """
        Récupère toutes les listes via différents endpoints.

        Essaie plusieurs endpoints connus :
        1. /api/namedLists (endpoint standard mais peut être vide)
        2. /api/todos (pour les listes de tâches)
        3. /api/household/lists (endpoint alternatif)

        Note: Si tous échouent, utilisez les commandes vocales (add, remove, etc.).
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []

            # Liste des endpoints à tester
            endpoints = [
                ("/api/namedLists", "lists"),
                ("/api/todos", "values"),  # Retourne {"values": [...]}
                ("/api/household/lists", "lists"),
            ]

            for endpoint, key in endpoints:
                try:
                    logger.debug(f"🔍 Test endpoint: {endpoint}")
                    response = self.breaker.call(
                        self.http_client.get,
                        f"https://{self.config.alexa_domain}{endpoint}",
                        headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                        timeout=10,
                    )
                    response.raise_for_status()
                    data = response.json()
                    lists = data.get(key, [])

                    if lists:
                        logger.success(f"✅ Listes trouvées via {endpoint} ({len(lists)} liste(s))")
                        return lists
                    else:
                        logger.debug(f"⚠️ Endpoint {endpoint} retourne une liste vide")

                except Exception as e:
                    logger.debug(f"❌ Endpoint {endpoint} échoué: {e}")
                    continue

            # Tous les endpoints ont échoué
            logger.warning(
                "⚠️ Impossible de récupérer les listes via les API REST. "
                "Les commandes vocales (add, remove) fonctionneront quand même."
            )
            return []

    def get_list(self, list_name: str) -> Optional[Dict]:
        """Récupère une liste spécifique par nom ou type.

        Args:
            list_name: Nom de la liste ('shopping', 'todo', ou nom personnalisé)

        Returns:
            Dictionnaire de la liste ou None si non trouvée
        """
        lists = self.get_lists()

        # Recherche par type connu
        if list_name.lower() == "shopping":
            for lst in lists:
                if lst.get("type") == "SHOPPING_ITEM":
                    return lst
        elif list_name.lower() == "todo":
            for lst in lists:
                if lst.get("type") == "TASK":
                    return lst

        # Recherche par nom
        for lst in lists:
            if lst.get("name", "").lower() == list_name.lower():
                return lst

        return None

    def add_item(self, list_name: str, text: str, device_serial: Optional[str] = None) -> bool:
        """
        Ajoute un élément à une liste via commande vocale.

        Args:
            list_name: Nom de la liste ('shopping', 'todo', ou nom personnalisé)
            text: Texte de l'élément à ajouter
            device_serial: Serial du device Alexa (optionnel, utilise un Echo par défaut)

        Returns:
            True si succès
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                # Mapper les noms de liste vers les commandes françaises
                list_commands = {
                    "shopping": "liste de courses",
                    "todo": "liste de tâches",
                    "courses": "liste de courses",
                    "tâches": "liste de tâches",
                    "taches": "liste de tâches",
                }

                list_target = list_commands.get(list_name.lower(), f"liste {list_name}")

                # Construire la commande vocale
                command = f"ajoute {text} à ma {list_target}"

                logger.info(f"📝 Commande vocale: '{command}'")

                # Envoyer via VoiceCommandService avec device spécifique
                success = self.voice_service.speak(command, device_serial=device_serial)

                if success:
                    logger.success(f"Élément '{text}' ajouté à '{list_name}'")
                else:
                    logger.error(f"Échec ajout de '{text}'")

                return success

            except Exception as e:
                logger.error(f"Erreur ajout item: {e}")
                return False

    def remove_item(self, list_name: str, text: str, device_serial: Optional[str] = None) -> bool:
        """
        Supprime un élément d'une liste via commande vocale.

        Args:
            list_name: Nom de la liste ('shopping', 'todo', ou nom personnalisé)
            text: Texte de l'élément à supprimer
            device_serial: Serial du device Alexa (optionnel, utilise un Echo par défaut)

        Returns:
            True si succès
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                # Mapper les noms de liste
                list_commands = {
                    "shopping": "liste de courses",
                    "todo": "liste de tâches",
                    "courses": "liste de courses",
                    "tâches": "liste de tâches",
                    "taches": "liste de tâches",
                }

                list_target = list_commands.get(list_name.lower(), f"liste {list_name}")

                # Construire la commande vocale (utiliser "retire" au lieu de "supprime")
                command = f"retire {text} de ma {list_target}"

                logger.info(f"📝 Commande vocale: '{command}'")

                # Envoyer via VoiceCommandService avec device spécifique
                success = self.voice_service.speak(command, device_serial=device_serial)

                if success:
                    logger.success(f"Élément '{text}' supprimé de '{list_name}'")
                else:
                    logger.error(f"Échec suppression de '{text}'")

                return success

            except Exception as e:
                logger.error(f"Erreur suppression item: {e}")
                return False

    def complete_item(self, list_name: str, text: str, device_serial: Optional[str] = None) -> bool:
        """
        Marque un élément comme complété via commande vocale.

        Args:
            list_name: Nom de la liste ('shopping', 'todo', ou nom personnalisé)
            text: Texte de l'élément à marquer complété
            device_serial: Serial du device Alexa (optionnel, utilise un Echo par défaut)

        Returns:
            True si succès
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                # Mapper les noms de liste
                list_commands = {
                    "shopping": "liste de courses",
                    "todo": "liste de tâches",
                    "courses": "liste de courses",
                    "tâches": "liste de tâches",
                    "taches": "liste de tâches",
                }

                list_target = list_commands.get(list_name.lower(), f"liste {list_name}")

                # Construire la commande vocale
                command = f"marque {text} comme fait dans ma {list_target}"

                logger.info(f"📝 Commande vocale: '{command}'")

                # Envoyer via VoiceCommandService avec device spécifique
                success = self.voice_service.speak(command, device_serial=device_serial)

                if success:
                    logger.success(f"Élément '{text}' marqué complété dans '{list_name}'")
                else:
                    logger.error(f"Échec marquage de '{text}'")

                return success

            except Exception as e:
                logger.error(f"Erreur marquage item: {e}")
                return False

    def clear_list(self, list_name: str, completed_only: bool = False, device_serial: Optional[str] = None) -> bool:
        """
        Vide une liste via commande vocale.

        Args:
            list_name: Nom de la liste ('shopping', 'todo', ou nom personnalisé)
            completed_only: Si True, supprime uniquement les éléments complétés
            device_serial: Serial du device Alexa (optionnel, utilise un Echo par défaut)

        Returns:
            True si succès
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                # Mapper les noms de liste
                list_commands = {
                    "shopping": "liste de courses",
                    "todo": "liste de tâches",
                    "courses": "liste de courses",
                    "tâches": "liste de tâches",
                    "taches": "liste de tâches",
                }

                list_target = list_commands.get(list_name.lower(), f"liste {list_name}")

                # Construire la commande vocale
                if completed_only:
                    command = f"supprime les éléments terminés de ma {list_target}"
                else:
                    command = f"vide ma {list_target}"

                logger.info(f"📝 Commande vocale: '{command}'")

                # Envoyer via VoiceCommandService avec device spécifique
                success = self.voice_service.speak(command, device_serial=device_serial)

                if success:
                    logger.success(f"Liste '{list_name}' vidée")
                else:
                    logger.error(f"Échec vidage de '{list_name}'")

                return success

            except Exception as e:
                logger.error(f"Erreur vidage liste: {e}")
                return False

    def create_list(self, name: str, device_serial: Optional[str] = None) -> bool:
        """
        Crée une nouvelle liste via commande vocale.

        Args:
            name: Nom de la nouvelle liste
            device_serial: Serial du device Alexa (optionnel, utilise un Echo par défaut)

        Returns:
            True si succès
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                # Construire la commande vocale
                command = f"crée une liste {name}"

                logger.info(f"📝 Commande vocale: '{command}'")

                # Envoyer via VoiceCommandService avec device spécifique
                success = self.voice_service.speak(command, device_serial=device_serial)

                if success:
                    logger.success(f"Liste '{name}' créée")
                else:
                    logger.error(f"Échec création de '{name}'")

                return success

            except Exception as e:
                logger.error(f"Erreur création liste: {e}")
                return False

    def get_shopping_list(self) -> Optional[Dict[str, Any]]:
        """Raccourci pour la liste de courses."""
        lists = self.get_lists()
        for lst in lists:
            if lst.get("type") == "SHOPPING_ITEM":
                return lst
        return None

    def get_todo_list(self) -> Optional[Dict[str, Any]]:
        """Raccourci pour la liste de tâches."""
        lists = self.get_lists()
        for lst in lists:
            if lst.get("type") == "TASK":
                return lst
        return None
