"""
Contrôleur pour thermostats connectés - Thread-safe.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from core.base_manager import BaseManager
from services.cache_service import CacheService

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class ThermostatController(BaseManager[Dict[str, Any]]):
    """Contrôleur thread-safe pour thermostats connectés.

    Hérite de `BaseManager` pour réutiliser le cache et le client HTTP.
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
        self._thermostats_cache: Optional[List[Dict[str, Any]]] = None
        logger.info("ThermostatController initialisé")

    def get_all_thermostats(self) -> list[dict[str, Any]]:
        """Récupère tous les thermostats depuis le cache smart_home_all."""
        with self._lock:
            # 1. Cache mémoire (TTL 5min)
            if self._thermostats_cache:
                logger.debug("Thermostats depuis cache mémoire")
                return self._thermostats_cache

            # 2. Cache disque smart_home_all
            smart_home_data = self.cache_service.get("smart_home_all")
            if smart_home_data:
                thermostats = self._filter_thermostats(smart_home_data.get("devices", []))
                self._thermostats_cache = thermostats
                logger.debug(f"{len(thermostats)} thermostat(s) depuis cache smart_home_all")
                return thermostats

            logger.warning("Aucun cache smart_home_all disponible, synchronisation nécessaire")
            return []

    def _filter_thermostats(self, devices: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filtre les thermostats depuis la liste complète smart devices."""
        thermostats = []
        for device in devices:
            provider_data = device.get("providerData", {})
            category_type = provider_data.get("categoryType", "")
            device_type = provider_data.get("deviceType", "")

            # Filtre basé sur categoryType ou deviceType
            if "THERMOSTAT" in category_type.upper() or "THERMOSTAT" in device_type.upper():
                thermostats.append(device)

        return thermostats

    def set_temperature(self, entity_id: str, target_celsius: float) -> bool:
        """Définit la température cible en Celsius."""
        with self._lock:
            if not self._check_connection():
                return False
            if not 10.0 <= target_celsius <= 35.0:
                logger.error(f"Température invalide: {target_celsius}°C (10-35)")
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.ThermostatController",
                            "name": "SetTargetTemperature",
                            "messageId": f"temp-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {"targetSetpoint": {"value": target_celsius, "scale": "CELSIUS"}},
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
                logger.success(f"Température {target_celsius}°C pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur température: {e}")
                return False

    def set_mode(self, entity_id: str, mode: str) -> bool:
        """Définit le mode (HEAT, COOL, AUTO, ECO, OFF)."""
        with self._lock:
            if not self._check_connection():
                return False

            valid_modes = ["HEAT", "COOL", "AUTO", "ECO", "OFF"]
            mode = mode.upper()
            if mode not in valid_modes:
                logger.error(f"Mode invalide: {mode} ({', '.join(valid_modes)})")
                return False

            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.ThermostatController",
                            "name": "SetThermostatMode",
                            "messageId": f"mode-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {"thermostatMode": {"value": mode}},
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
                logger.success(f"Mode {mode} pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur mode thermostat: {e}")
                return False

    def adjust_temperature(self, entity_id: str, delta_celsius: float) -> bool:
        """Ajuste la température (+/- delta en Celsius)."""
        with self._lock:
            if not self._check_connection():
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.ThermostatController",
                            "name": "AdjustTargetTemperature",
                            "messageId": f"adjust-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {"targetSetpointDelta": {"value": delta_celsius, "scale": "CELSIUS"}},
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
                sign = "+" if delta_celsius > 0 else ""
                logger.success(f"Température {sign}{delta_celsius}°C pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur ajustement température: {e}")
                return False
