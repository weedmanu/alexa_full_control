"""
Contrôleur générique pour appareils Smart Home - Thread-safe.
"""

from typing import Any, Dict, List, Optional, cast

from loguru import logger

from core.base_manager import BaseManager
from services.cache_service import CacheService

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class SmartDeviceController(BaseManager[Dict[str, Any]]):
    """Contrôleur thread-safe pour appareils connectés (serrures, volets, etc.).

    Hérite de `BaseManager` pour utiliser `self.http_client`, cache et locks.
    """

    def __init__(
        self,
        http_client: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        cache_service: Optional[CacheService] = None,
    ) -> None:
        super().__init__(http_client, config, state_machine or AlexaStateMachine(), cache_service)
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._locks_cache: Optional[List[Dict[str, Any]]] = None
        self._plugs_cache: Optional[List[Dict[str, Any]]] = None
        self._all_devices_cache: Optional[List[Dict[str, Any]]] = None
        logger.info("SmartDeviceController initialisé")

    def get_smart_home_devices(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les appareils Smart Home (lazy loading).

        Utilise le SyncService pour charger les données à la demande.
        """
        with self._lock:
            if self._all_devices_cache:
                return self._all_devices_cache

            # Utiliser le cache directement (hérité de l'ancienne implémentation)
            smart_home_data = self.cache_service.get("smart_home_all")
            if smart_home_data:
                devices = smart_home_data.get("devices", [])
                self._all_devices_cache = devices
                logger.debug(f"{len(devices)} appareils Smart Home depuis cache")
                return cast(List[Dict[str, Any]], devices)

            logger.warning("Aucun cache smart_home_all trouvé")
            return []

    def get_all_locks(self) -> List[Dict[str, Any]]:
        """Récupère toutes les serrures depuis smart_home_all cache."""
        with self._lock:
            if self._locks_cache:
                return self._locks_cache

            smart_home_data = self.cache_service.get("smart_home_all")
            if smart_home_data:
                locks = self._filter_locks(smart_home_data.get("devices", []))
                self._locks_cache = locks
                logger.debug(f"{len(locks)} serrure(s) depuis cache")
                return locks

            logger.warning("Aucun cache smart_home_all")
            return []

    def get_all_plugs(self) -> List[Dict[str, Any]]:
        """Récupère toutes les prises depuis smart_home_all cache."""
        with self._lock:
            if self._plugs_cache:
                return self._plugs_cache

            smart_home_data = self.cache_service.get("smart_home_all")
            if smart_home_data:
                plugs = self._filter_plugs(smart_home_data.get("devices", []))
                self._plugs_cache = plugs
                logger.debug(f"{len(plugs)} prise(s) depuis cache")
                return plugs

            logger.warning("Aucun cache smart_home_all")
            return []

    def _filter_locks(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtre serrures."""
        locks: List[Dict[str, Any]] = []
        for device in devices:
            provider_data = device.get("providerData", {})
            category = provider_data.get("categoryType", "")
            dev_type = provider_data.get("deviceType", "")

            if "LOCK" in category.upper() or "LOCK" in dev_type.upper():
                locks.append(device)

        return locks

    def _filter_plugs(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtre prises/switches."""
        plugs: List[Dict[str, Any]] = []
        for device in devices:
            provider_data = device.get("providerData", {})
            category = provider_data.get("categoryType", "")
            dev_type = provider_data.get("deviceType", "")

            if (
                "PLUG" in category.upper()
                or "SWITCH" in category.upper()
                or "PLUG" in dev_type.upper()
                or "SWITCH" in dev_type.upper()
            ):
                plugs.append(device)

        return plugs

    def lock(self, entity_id: str) -> bool:
        """Verrouille une serrure connectée."""
        return self._lock_control(entity_id, "Lock")

    def unlock(self, entity_id: str) -> bool:
        """Déverrouille une serrure connectée."""
        return self._lock_control(entity_id, "Unlock")

    def _lock_control(self, entity_id: str, action: str) -> bool:
        """Contrôle une serrure."""
        with self._lock:
            if not self._check_connection():
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.LockController",
                            "name": action,
                            "messageId": f"lock-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {},
                    }
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/phoenix",
                    json=directive,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"{action} pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur {action}: {e}")
                return False

    def set_percentage(self, entity_id: str, percentage: int) -> bool:
        """Définit un pourcentage (volets, stores, etc.) 0-100."""
        with self._lock:
            if not self._check_connection():
                return False
            if not 0 <= percentage <= 100:
                logger.error(f"Pourcentage invalide: {percentage} (0-100)")
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.PercentageController",
                            "name": "SetPercentage",
                            "messageId": f"pct-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {"percentage": percentage},
                    }
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/phoenix",
                    json=directive,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Position {percentage}% pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur position: {e}")
                return False

    def get_device_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Récupère l'état d'un appareil."""
        with self._lock:
            if not self._check_connection():
                return None
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/phoenix/state/{entity_id}",
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                from typing import cast

                return cast(Dict[str, Any], response.json())
            except Exception as e:
                logger.error(f"Erreur état appareil: {e}")
                return None
