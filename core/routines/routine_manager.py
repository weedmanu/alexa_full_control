"""
Gestionnaire de routines Alexa - Thread-safe et robuste.

Ce module gère les routines Alexa (automation scenarios) avec:
- Récupération des routines (actives/désactivées)
- Exécution de routines
- Création/suppression/mise à jour routines
- Recherche et planification routines
- Cache automatique via CacheService
- Circuit breaker pour résilience
- Thread-safety complet

Now inherits from BaseManager to eliminate code duplication.
"""

import json
import re
import time
import uuid
from typing import Any, Dict, List, Optional

from loguru import logger

from core.base_manager import BaseManager, create_http_client_from_auth
from core.state_machine import AlexaStateMachine
from services.cache_service import CacheService


class RoutineManager(BaseManager[Dict[str, Any]]):
    """
    Gestionnaire thread-safe pour routines Alexa.

    Architecture:
        - Cache mémoire (TTL 5min) pour lectures fréquentes
        - Cache disque (TTL 1h) via CacheService
        - Circuit breaker pour protection API
        - State machine pour vérification état système

    Thread-safety:
        - RLock pour opérations atomiques (hérité de BaseManager)
        - Cache thread-safe via CacheService

    Methods:
        - get_routines(): Récupère les routines
        - execute(routine_id): Exécute une routine
        - execute_routine(): Alias complet pour execute()
        - create_routine(): Crée une nouvelle routine
        - delete_routine(): Supprime une routine
        - update_routine(): Met à jour une routine
        - get_routine(): Récupère détails d'une routine
        - list_actions(): Liste actions disponibles
        - set_enabled(): Active/désactive une routine
        - search(): Recherche routines par critères
        - schedule(): Planifie une routine
        - unschedule(): Supprime la planification
        - invalidate_cache(): Invalide tous les caches
        - get_stats(): Statistiques routines

    Example:
        >>> routine_mgr = RoutineManager(auth, config)
        >>> routines = routine_mgr.get_routines()
        >>> routine_mgr.execute("amzn1.alexa.routine.abc123")
        >>> routine_mgr.create_routine("My Routine", actions=[...])
    """

    def __init__(
        self,
        auth: Any,
        state_machine: AlexaStateMachine,
        api_service: Any,
        cache_service: Optional[CacheService] = None,
        cache_ttl: int = 300,
    ) -> None:
        """
        Initialise le gestionnaire de routines avec injection obligatoire.

        Args:
            auth: Instance AlexaAuth pour authentification
            state_machine: Machine à états pour gestion d'état
            api_service: Service API centralisé (MANDATORY, jamais None)
            cache_service: Service cache optionnel (créé si None)
            cache_ttl: Durée de vie du cache en secondes (défaut: 300)

        Raises:
            ValueError: Si api_service est None (injection obligatoire)
        """
        if api_service is None:
            raise ValueError("api_service is mandatory and cannot be None")

        # Créer le client HTTP depuis auth
        http_client = create_http_client_from_auth(auth)

        # Phase 2: Create minimal config for BaseManager (only needs amazon_domain)
        class _MinimalConfig:
            amazon_domain = "amazon.com"

        minimal_config = _MinimalConfig()

        # Initialiser BaseManager (hérite: breaker, _lock, cache_service, headers)
        super().__init__(
            http_client=http_client,
            config=minimal_config,  # Minimal config just for BaseManager initialization
            state_machine=state_machine,
            cache_service=cache_service,
            cache_ttl=cache_ttl,
        )

        # Attributs spécifiques à RoutineManager
        self.auth = auth
        # Phase 2: Mandatory API Service (no fallback)
        self._api_service = api_service

        self._routines_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: float = 0
        self._memory_cache_ttl: float = cache_ttl
        self._available_actions_cache: Optional[List[Dict[str, Any]]] = None
        self._actions_cache_timestamp: float = 0

        logger.info("✅ RoutineManager initialisé avec api_service obligatoire (cache 5min mémoire + 1h disque)")

    def get_routines(
        self,
        enabled_only: bool = False,
        disabled_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Récupère les routines depuis cache ou API.

        Args:
            enabled_only: Ne retourner que routines actives
            disabled_only: Ne retourner que routines désactivées
            limit: Nombre max de routines (None = toutes)

        Returns:
            Liste des routines avec metadata

        Thread-safety:
            ✅ Lock acquisition pour cache mémoire
            ✅ CacheService thread-safe pour cache disque
        """
        with self._lock:
            # 1. Cache mémoire (TTL 5min)
            if self._routines_cache and not self._is_cache_expired():
                logger.debug("Routines depuis cache mémoire")
                return self._filter_routines(self._routines_cache, enabled_only, disabled_only, limit)

            # 2. Cache disque (TTL 1h)
            cache_data = self.cache_service.get("routines")
            if cache_data:
                routines = cache_data.get("routines", [])
                if routines:
                    self._update_memory_cache(routines)
                    logger.debug(f"{len(routines)} routine(s) depuis cache disque")
                    return self._filter_routines(routines, enabled_only, disabled_only, limit)

            # 3. API Amazon (fallback + refresh cache)
            return self._refresh_routines(enabled_only, disabled_only, limit)

    def _refresh_routines(
        self,
        enabled_only: bool = False,
        disabled_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rafraîchit les routines depuis API Amazon.

        Args:
            enabled_only: Filtre routines actives
            disabled_only: Filtre routines désactivées
            limit: Limite nombre résultats

        Returns:
            Liste routines filtrées

        Raises:
            Aucune - retourne [] si erreur (logged)
        """
        try:
            if not self.state_machine.can_execute_commands:
                logger.warning("État système invalide, routines depuis cache uniquement")
                return []

            # Endpoint API routines (v2 automations)
            # Phase 2: Use api_service directly (mandatory, no fallback)
            response_data = self._api_service.get("/api/behaviors/v2/automations", timeout=15)

            if not response_data:
                logger.warning("⚠️  API returned empty response for routines")
                return []

            routines: List[Dict[str, Any]] = response_data if isinstance(response_data, list) else []

            # Sauvegarde cache double
            self._update_memory_cache(routines)
            self.cache_service.set("routines", {"routines": routines}, ttl_seconds=3600)

            logger.success(f"✅ {len(routines)} routine(s) récupérées depuis API")
            return self._filter_routines(routines, enabled_only, disabled_only, limit)

        except Exception as e:
            logger.error(f"❌ Erreur récupération routines: {e}")
            return []

    def execute_routine(
        self,
        automation_id: str,
        device_serial: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> bool:
        """
        Exécute une routine Alexa.

        Args:
            automation_id: ID de la routine (format: amzn1.alexa.routine.xxx)
            device_serial: Serial du device cible (optionnel, pour remplacer ALEXA_CURRENT_DSN)
            device_type: Type du device cible (optionnel, pour remplacer ALEXA_CURRENT_DEVICE_TYPE)

        Returns:
            True si succès, False sinon

        Thread-safety:
            ✅ Lock acquisition
            ✅ State machine thread-safe
            ✅ Circuit breaker thread-safe
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                logger.error("Impossible d'exécuter routine (état système invalide)")
                return False

            if not automation_id or not (
                automation_id.startswith("amzn1.alexa.routine") or automation_id.startswith("amzn1.alexa.automation")
            ):
                logger.error(f"ID routine invalide: {automation_id}")
                return False

            try:
                # 1. Récupérer les détails de la routine pour obtenir sa sequence
                routine_info = self.get_routine_info(automation_id)
                if not routine_info:
                    logger.error(f"❌ Routine {automation_id} introuvable")
                    return False

                # 2. Extraire la séquence
                sequence = routine_info.get("sequence")
                if not sequence:
                    logger.error("❌ Séquence routine introuvable")
                    return False

                # 3. Convertir en JSON string si nécessaire
                if isinstance(sequence, dict):
                    sequence_str = json.dumps(sequence, separators=(",", ":"))
                elif isinstance(sequence, str):
                    sequence_str = sequence
                else:
                    logger.error("❌ Format séquence invalide")
                    return False

                # 4. Remplacer les placeholders si device fourni
                if device_serial or device_type:
                    logger.debug(f"Remplacement device dans la séquence: serial={device_serial}, type={device_type}")

                    # Remplacer les placeholders standards
                    if device_serial:
                        sequence_str = sequence_str.replace("ALEXA_CURRENT_DSN", device_serial)
                        logger.debug(f"Placeholder ALEXA_CURRENT_DSN remplacé par {device_serial}")

                    if device_type:
                        sequence_str = sequence_str.replace("ALEXA_CURRENT_DEVICE_TYPE", device_type)
                        logger.debug(f"Placeholder ALEXA_CURRENT_DEVICE_TYPE remplacé par {device_type}")

                    # Pour les routines statiques sans placeholders, remplacer les deviceSerialNumber en dur
                    # Ceci permet de forcer l'exécution sur le device choisi
                    if device_serial and '"deviceSerialNumber"' in sequence_str:
                        # Remplacer tous les deviceSerialNumber dans la séquence
                        sequence_str = re.sub(
                            r'"deviceSerialNumber"\s*:\s*"[^"]*"',
                            f'"deviceSerialNumber":"{device_serial}"',
                            sequence_str,
                        )
                        logger.debug(f"deviceSerialNumber statiques remplacés par {device_serial}")

                    if device_type and '"deviceType"' in sequence_str:
                        # Remplacer tous les deviceType dans la séquence
                        sequence_str = re.sub(
                            r'"deviceType"\s*:\s*"[^"]*"',
                            f'"deviceType":"{device_type}"',
                            sequence_str,
                        )
                        logger.debug(f"deviceType statiques remplacés par {device_type}")

                # Remplacer ALEXA_CUSTOMER_ID si disponible
                if hasattr(self.auth, "customer_id") and self.auth.customer_id:
                    sequence_str = sequence_str.replace("ALEXA_CUSTOMER_ID", self.auth.customer_id)
                    logger.debug("Placeholder ALEXA_CUSTOMER_ID remplacé")

                # 5. Exécuter la routine
                payload: Dict[str, Any] = {
                    "behaviorId": automation_id,
                    "sequenceJson": sequence_str,
                    "status": "ENABLED",
                }

                # Phase 2: Use api_service directly (no fallback)
                _ = self._api_service.post("/api/behaviors/preview", json=payload, timeout=10)

                logger.success(f"✅ Routine exécutée: {automation_id}")
                return True

            except Exception as e:
                logger.error(f"❌ Erreur exécution routine {automation_id}: {e}")
                return False

    def execute(self, routine_id: str, device: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Exécute une routine (API alternative).

        Args:
            routine_id: ID de la routine
            device: Device cible (optionnel)
            **kwargs: Arguments supplémentaires

        Returns:
            Dictionnaire avec résultat exécution

        Raises:
            ValueError: Si routine non trouvée ou ID invalide
            TimeoutError: Si exécution timeout
        """
        if not routine_id:
            raise ValueError("Routine ID is required")

        if not self.get_routine_info(routine_id):
            raise ValueError(f"Routine not found: {routine_id}")

        try:
            result = self.execute_routine(routine_id, device_serial=device)
            return {
                "executed": result,
                "routine_id": routine_id,
                "status": "executed" if result else "failed",
            }
        except TimeoutError:
            raise TimeoutError(f"Execution timeout for routine {routine_id}")
        except Exception as e:
            raise ValueError(f"Failed to execute routine: {str(e)}")

    def get_routine_info(self, automation_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'une routine.

        Args:
            automation_id: ID de la routine

        Returns:
            Dictionnaire avec détails routine ou None
        """
        routines = self.get_routines()
        for routine in routines:
            if routine.get("automationId") == automation_id:
                return routine

        logger.warning(f"Routine {automation_id} introuvable")
        return None

    def get_routine(self, routine_id: str) -> Dict[str, Any]:
        """
        Récupère les détails complets d'une routine.

        Args:
            routine_id: ID de la routine

        Returns:
            Dictionnaire avec détails routine

        Raises:
            ValueError: Si routine non trouvée
        """
        routine = self.get_routine_info(routine_id)
        if not routine:
            raise ValueError(f"Routine not found: {routine_id}")
        return routine

    def create_routine(
        self,
        name: str,
        actions: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Crée une nouvelle routine.

        Args:
            name: Nom de la routine
            actions: Liste des actions (optionnel)
            description: Description (optionnel)
            **kwargs: Arguments supplémentaires

        Returns:
            Dictionnaire avec détails routine créée

        Raises:
            ValueError: Si paramètres invalides
        """
        if not name or not isinstance(name, str):
            raise ValueError("Name required and must be string")

        try:
            routine_id = f"amzn1.alexa.routine.{uuid.uuid4().hex[:12]}"

            payload: Dict[str, Any] = {
                "automationId": routine_id,
                "name": name,
                "status": "ENABLED",
                "sequence": actions or [],
            }

            if description:
                payload["description"] = description

            # Phase 2: Use api_service directly (no fallback)
            response = self._api_service.post(
                "/api/behaviors/v2/automations",
                json=payload,
                timeout=15,
            )

            # Invalider cache
            self.invalidate_cache()
            logger.success(f"✅ Routine créée: {routine_id}")
            result = {
                "routine_id": routine_id,
                "name": name,
                "created": True,
            }
            if response:
                result.update(response)
            return result

        except Exception as e:
            logger.error(f"❌ Erreur création routine: {e}")
            raise

    def delete_routine(self, routine_id: str) -> Dict[str, Any]:
        """
        Supprime une routine.

        Args:
            routine_id: ID de la routine

        Returns:
            Dictionnaire avec résultat suppression

        Raises:
            ValueError: Si routine non trouvée
            KeyError: Si erreur suppression
        """
        # Vérifier existence
        if not self.get_routine_info(routine_id):
            raise ValueError(f"Routine not found: {routine_id}")

        try:
            # Phase 2: Use api_service directly (no fallback)
            response = self._api_service.delete(
                f"/api/behaviors/v2/automations/{routine_id}",
                timeout=15,
            )

            # Invalider cache
            self.invalidate_cache()

            logger.success(f"✅ Routine supprimée: {routine_id}")
            result = {
                "routine_id": routine_id,
                "deleted": True,
            }
            if response:
                result.update(response)
            return result

        except Exception as e:
            logger.error(f"❌ Erreur suppression routine: {e}")
            raise KeyError(f"Failed to delete routine: {str(e)}")

    def update_routine(
        self,
        routine_id: str,
        name: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        enabled: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Met à jour une routine.

        Args:
            routine_id: ID de la routine
            name: Nouveau nom (optionnel)
            actions: Nouvelles actions (optionnel)
            enabled: Activer/désactiver (optionnel)
            **kwargs: Arguments supplémentaires

        Returns:
            Dictionnaire avec routine mise à jour
        """
        # Récupérer la routine actuelle
        routine = self.get_routine_info(routine_id)
        if not routine:
            raise ValueError(f"Routine not found: {routine_id}")

        try:
            payload: Dict[str, Any] = {}

            if name is not None:
                payload["name"] = name
            if actions is not None:
                payload["sequence"] = actions
            if enabled is not None:
                payload["status"] = "ENABLED" if enabled else "DISABLED"

            # Phase 2: Use api_service directly (no fallback)
            response = self._api_service.patch(
                f"/api/behaviors/v2/automations/{routine_id}",
                json=payload,
                timeout=15,
            )

            # Invalider cache
            self.invalidate_cache()

            updated_routine: Dict[str, Any] = {"routine_id": routine_id}
            updated_routine.update(routine)
            updated_routine.update(payload)
            if response:
                updated_routine.update(response)

            logger.success(f"✅ Routine mise à jour: {routine_id}")
            return updated_routine

        except Exception as e:
            logger.error(f"❌ Erreur mise à jour routine: {e}")
            raise

    def list_actions(self) -> List[Dict[str, Any]]:
        """
        Liste les actions disponibles pour les routines.

        Returns:
            Liste des actions disponibles
        """
        with self._lock:
            # Vérifier cache actions
            if self._available_actions_cache and not self._is_actions_cache_expired():
                logger.debug("Actions depuis cache mémoire")
                return self._available_actions_cache

        try:
            # Phase 2: Use api_service directly (no fallback)
            response = self._api_service.get(
                "/api/behaviors/v2/actions",
                timeout=15,
            )

            actions: list[Any] = response if isinstance(response, list) else []

            # Mettre en cache
            with self._lock:
                self._available_actions_cache = actions
                self._actions_cache_timestamp = time.time()

            logger.debug(f"✅ {len(actions)} action(s) disponible(s)")
            return actions

        except Exception as e:
            logger.error(f"❌ Erreur récupération actions: {e}")
            return []

    def set_enabled(self, routine_id: str, enabled: bool) -> Dict[str, Any]:
        """
        Active ou désactive une routine.

        Args:
            routine_id: ID de la routine
            enabled: True pour activer, False pour désactiver

        Returns:
            Dictionnaire avec résultat
        """
        return self.update_routine(routine_id, enabled=enabled)

    def search(
        self, name: Optional[str] = None, description: Optional[str] = None, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Recherche des routines par critères.

        Args:
            name: Rechercher par nom (optionnel)
            description: Rechercher par description (optionnel)
            **kwargs: Autres critères

        Returns:
            Liste des routines correspondantes
        """
        routines = self.get_routines()
        results = routines

        if name:
            results = [r for r in results if name.lower() in r.get("name", "").lower()]

        if description:
            results = [r for r in results if description.lower() in r.get("description", "").lower()]

        logger.debug(f"Recherche trouvé {len(results)} routine(s)")
        return results

    def schedule(
        self, routine_id: str, time_str: str, recurring: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Planifie une routine.

        Args:
            routine_id: ID de la routine
            time_str: Heure de planification (ex: "07:00")
            recurring: Type récurrence (ex: "daily") (optionnel)
            **kwargs: Arguments supplémentaires

        Returns:
            Dictionnaire avec détails planification

        Raises:
            ValueError: Si paramètres invalides
        """
        if not routine_id or not time_str:
            raise ValueError("routine_id and time_str are required")

        try:
            payload: Dict[str, Any] = {
                "automationId": routine_id,
                "scheduledTime": time_str,
            }

            if recurring:
                payload["recurring"] = recurring

            # Phase 2: Use api_service directly (no fallback)
            response = self._api_service.post(
                f"/api/behaviors/v2/automations/{routine_id}/schedule",
                json=payload,
                timeout=15,
            )

            logger.success(f"✅ Routine planifiée: {routine_id} à {time_str}")
            result = {
                "routine_id": routine_id,
                "scheduled_time": time_str,
                "scheduled": True,
                "recurring": recurring,
            }
            if response:
                result.update(response)
            return result

        except Exception as e:
            logger.error(f"❌ Erreur planification routine: {e}")
            raise

    def unschedule(self, routine_id: str) -> Dict[str, Any]:
        """
        Supprime la planification d'une routine.

        Args:
            routine_id: ID de la routine

        Returns:
            Dictionnaire avec résultat
        """
        try:
            # Phase 2: Use api_service directly (no fallback)
            response = self._api_service.delete(
                f"/api/behaviors/v2/automations/{routine_id}/schedule",
                timeout=15,
            )

            logger.success(f"✅ Planification supprimée: {routine_id}")
            result = {
                "routine_id": routine_id,
                "scheduled": False,
            }
            if response:
                result.update(response)
            return result

        except Exception as e:
            logger.error(f"❌ Erreur suppression planification: {e}")
            raise

    def invalidate_cache(self) -> None:
        """
        Invalide tous les caches (mémoire + disque).

        Utile après création/modification/suppression routine.
        """
        with self._lock:
            self._routines_cache = None
            self._cache_timestamp = 0
            self.cache_service.invalidate("routines")
            logger.debug("Cache routines invalidé")

    # === Méthodes privées ===

    def _filter_routines(
        self,
        routines: List[Dict[str, Any]],
        enabled_only: bool = False,
        disabled_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Filtre routines selon critères."""
        filtered = routines

        if enabled_only:
            filtered = [r for r in filtered if r.get("status") == "ENABLED"]
        elif disabled_only:
            filtered = [r for r in filtered if r.get("status") != "ENABLED"]

        if limit and limit > 0:
            filtered = filtered[:limit]

        return filtered

    def _update_memory_cache(self, routines: List[Dict[str, Any]]) -> None:
        """Met à jour le cache mémoire avec timestamp."""
        self._routines_cache = routines
        self._cache_timestamp = time.time()

    def _is_cache_expired(self) -> bool:
        """Vérifie si cache mémoire expiré."""
        return (time.time() - self._cache_timestamp) > self._memory_cache_ttl

    def _is_actions_cache_expired(self) -> bool:
        """Vérifie si cache actions expiré."""
        return (time.time() - self._actions_cache_timestamp) > self._memory_cache_ttl

    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère statistiques routines.

        Returns:
            Dict avec total, enabled, disabled, cache_status
        """
        routines = self.get_routines()
        enabled = [r for r in routines if r.get("status") == "ENABLED"]
        disabled = [r for r in routines if r.get("status") != "ENABLED"]

        return {
            "total": len(routines),
            "enabled": len(enabled),
            "disabled": len(disabled),
            "cache_status": "memory" if self._routines_cache else "disk/api",
        }
