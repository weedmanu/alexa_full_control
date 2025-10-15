"""
Gestionnaire de routines Alexa - Thread-safe et robuste.

Ce module gère les routines Alexa (automation scenarios) avec:
- Récupération des routines (actives/désactivées)
- Exécution de routines
- Cache automatique via CacheService
- Circuit breaker pour résilience
- Thread-safety complet
"""

import threading
from typing import Any, Dict, List, Optional

from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine
from services.cache_service import CacheService


class RoutineManager:
    """
    Gestionnaire thread-safe pour routines Alexa.

    Architecture:
        - Cache mémoire (TTL 5min) pour lectures fréquentes
        - Cache disque (TTL 1h) via CacheService
        - Circuit breaker pour protection API
        - State machine pour vérification état système

    Thread-safety:
        - RLock pour opérations atomiques
        - Cache thread-safe via CacheService

    Example:
        >>> routine_mgr = RoutineManager(auth, config)
        >>> routines = routine_mgr.get_routines()
        >>> routine_mgr.execute_routine("amzn1.alexa.routine.abc123")
    """

    def __init__(
        self,
        auth,
        config,
        state_machine: Optional[AlexaStateMachine] = None,
        cache_service: Optional[CacheService] = None,
    ):
        """
        Initialise le gestionnaire de routines.

        Args:
            auth: Instance AlexaAuth pour authentification
            config: Configuration système (alexa_domain, etc.)
            state_machine: Machine d'état système (défaut: nouvelle instance)
            cache_service: Service cache (défaut: nouvelle instance)
        """
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.cache_service = cache_service or CacheService()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        self._routines_cache: Optional[List[Dict]] = None
        self._cache_timestamp: float = 0
        self._cache_ttl: int = 300  # 5 minutes mémoire

        logger.info("RoutineManager initialisé (cache 5min mémoire + 1h disque)")

    def get_routines(
        self,
        enabled_only: bool = False,
        disabled_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict]:
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
            if cache_data and isinstance(cache_data, dict):
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
    ) -> List[Dict]:
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
            url = f"https://{self.config.alexa_domain}/api/behaviors/v2/automations"

            # Use unified http_client when available; ensure non-None for mypy
            http_client: Any = getattr(self, "http_client", None) or self.auth
            response = self.breaker.call(
                http_client.get,
                url,
                headers={"csrf": getattr(http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=15,
            )
            response.raise_for_status()

            data = response.json()
            routines = data if isinstance(data, list) else []

            # Sauvegarde cache double
            self._update_memory_cache(routines)
            self.cache_service.set("routines", {"routines": routines}, ttl_seconds=3600)

            logger.success(f"{len(routines)} routine(s) récupérées depuis API")
            return self._filter_routines(routines, enabled_only, disabled_only, limit)

        except Exception as e:
            logger.error(f"Erreur récupération routines: {e}")
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
                    import json

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
                        import json
                        import re

                        # Remplacer tous les deviceSerialNumber dans la séquence
                        sequence_str = re.sub(
                            r'"deviceSerialNumber"\s*:\s*"[^"]*"',
                            f'"deviceSerialNumber":"{device_serial}"',
                            sequence_str,
                        )
                        logger.debug(f"deviceSerialNumber statiques remplacés par {device_serial}")

                    if device_type and '"deviceType"' in sequence_str:
                        import re

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
                url = f"https://{self.config.alexa_domain}/api/behaviors/preview"

                payload = {
                    "behaviorId": automation_id,
                    "sequenceJson": sequence_str,
                    "status": "ENABLED",
                }

                http_client: Any = getattr(self, "http_client", None) or self.auth
                response = self.breaker.call(
                    http_client.post,
                    url,
                    json=payload,
                    headers={"csrf": getattr(http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()

                logger.success(f"Routine exécutée: {automation_id}")
                return True

            except Exception as e:
                logger.error(f"Erreur exécution routine {automation_id}: {e}")
                return False

    def get_routine_info(self, automation_id: str) -> Optional[Dict]:
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
        routines: List[Dict],
        enabled_only: bool = False,
        disabled_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Filtre routines selon critères."""
        filtered = routines

        if enabled_only:
            filtered = [r for r in filtered if r.get("status") == "ENABLED"]
        elif disabled_only:
            filtered = [r for r in filtered if r.get("status") != "ENABLED"]

        if limit and limit > 0:
            filtered = filtered[:limit]

        return filtered

    def _update_memory_cache(self, routines: List[Dict]) -> None:
        """Met à jour le cache mémoire avec timestamp."""
        import time

        self._routines_cache = routines
        self._cache_timestamp = time.time()

    def _is_cache_expired(self) -> bool:
        """Vérifie si cache mémoire expiré."""
        import time

        return (time.time() - self._cache_timestamp) > self._cache_ttl

    def get_stats(self) -> Dict:
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
