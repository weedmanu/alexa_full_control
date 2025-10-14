"""
Gestionnaire TuneIn (radio en ligne) - Thread-safe.
"""

import threading
from typing import Dict, List

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class TuneInManager:
    """Gestionnaire thread-safe pour TuneIn (radio)."""

    def __init__(self, auth, config, state_machine=None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        logger.info("TuneInManager initialisé")

    def search_stations(self, query: str, limit: int = 20) -> List[Dict]:
        """Recherche des stations radio."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self.breaker.call(
                    self.auth.session.get,
                    f"https://{self.config.alexa_domain}/api/tunein/search",
                    params={"query": query, "mediaOwnerCustomerId": self.auth.customer_id},
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                results = response.json().get("results", [])
                return results[:limit]
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
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/tunein/queue-and-play",
                    json=payload,
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Station {station_id} en lecture")
                return True
            except Exception as e:
                logger.error(f"Erreur lecture station: {e}")
                return False

    def get_favorites(self) -> List[Dict]:
        """Récupère les stations favorites."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self.breaker.call(
                    self.auth.session.get,
                    f"https://{self.config.alexa_domain}/api/tunein/favorites",
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                return response.json().get("favorites", [])
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
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/tunein/favorites",
                    json={"guideId": station_id},
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Station {station_id} ajoutée aux favoris")
                return True
            except Exception as e:
                logger.error(f"Erreur ajout favori: {e}")
                return False
