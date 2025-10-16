"""
Gestionnaire TuneIn (radio en ligne) - Thread-safe.
"""

import threading
from typing import Any, Dict, List, cast

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class TuneInManager:
    """Gestionnaire thread-safe pour TuneIn (radio)."""

    def __init__(self, auth_or_http: Any, config: Any, state_machine: Any = None) -> None:
        # Normalize to http_client wrapper when possible
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = (
                create_http_client_from_auth(auth_or_http) if hasattr(auth_or_http, "session") else auth_or_http
            )
        except Exception:
            self.http_client = getattr(auth_or_http, "session", auth_or_http)

        # Keep auth reference for backward compatibility
        self.auth = getattr(auth_or_http, "auth", auth_or_http)
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        logger.info("TuneInManager initialisé")

    def search_stations(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche des stations radio."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/tunein/search",
                    params={"query": query, "mediaOwnerCustomerId": getattr(self.auth, "customer_id", None)},
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                data = cast(Dict[str, Any], response.json())
                results = data.get("results", [])
                return cast(list[dict[str, Any]], results[:limit])
            except Exception as e:
                logger.error(f"Erreur recherche stations: {e}")
                return []

    def play_station(self, device_serial: str, device_type: str, station_id: str) -> bool:
        """Lance une station radio."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "guideId": station_id,
                    "contentType": "station",
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/tunein/queue-and-play",
                    json=payload,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Station {station_id} en lecture")
                return True
            except Exception as e:
                logger.error(f"Erreur lecture station: {e}")
                return False

    def get_favorites(self) -> List[Dict[str, Any]]:
        """Récupère les stations favorites."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/tunein/favorites",
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                data = cast(Dict[str, Any], response.json())
                return cast(list[dict[str, Any]], data.get("favorites", []))
            except Exception as e:
                logger.error(f"Erreur récupération favoris: {e}")
                return []

    def add_favorite(self, station_id: str) -> bool:
        """Ajoute une station aux favoris."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/tunein/favorites",
                    json={"guideId": station_id},
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Station {station_id} ajoutée aux favoris")
                return True
            except Exception as e:
                logger.error(f"Erreur ajout favori: {e}")
                return False
