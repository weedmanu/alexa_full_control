"""
Gestionnaire TuneIn (radio en ligne) - Thread-safe.
"""

from typing import Any, Dict, List, Optional, cast

from loguru import logger

from core.base_manager import BaseManager, create_http_client_from_auth
from core.state_machine import AlexaStateMachine

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.music_schemas import MusicSearchResponse
    HAS_MUSIC_TUNEIN_DTO = True
except ImportError:
    HAS_MUSIC_TUNEIN_DTO = False


class TuneInManager(BaseManager[Dict[str, Any]]):
    """Gestionnaire thread-safe pour TuneIn (radio)."""

    def __init__(self, auth_or_http: Any, config: Any, state_machine: Any = None, api_service: Any = None) -> None:
        if api_service is None:
            raise ValueError("api_service is mandatory in Phase 2")
        
        # Créer le client HTTP depuis auth
        http_client = create_http_client_from_auth(auth_or_http)

        # Initialiser BaseManager
        super().__init__(
            http_client=http_client,
            config=config,
            state_machine=state_machine or AlexaStateMachine(),
            cache_service=None,
            cache_ttl=300,
        )

        # Keep auth reference for backward compatibility
        self.auth = getattr(auth_or_http, "auth", auth_or_http)
        self._api_service: Any = api_service  # Mandatory AlexaAPIService
        logger.info("TuneInManager initialisé avec AlexaAPIService obligatoire")

    def search_stations(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche des stations radio."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                data = self._api_service.get(
                    "/api/tunein/search",
                    params={"query": query, "mediaOwnerCustomerId": getattr(self.auth, "customer_id", None)},
                )
                if isinstance(data, dict):
                    results = data.get("results", [])
                    return cast(list[dict[str, Any]], results[:limit])
                return []
            except Exception as e:
                logger.error(f"Erreur recherche stations: {e}")
                return []

    def search_stations_typed(self, query: str, limit: int = 20) -> Optional["MusicSearchResponse"]:
        """
        Phase 3.7: Typed DTO version of search_stations returning MusicSearchResponse.
        
        Returns station search results as MusicSearchResponse DTO with full type safety.
        Falls back gracefully if DTOs not available.
        
        Args:
            query: Search query
            limit: Limit of results
            
        Returns:
            MusicSearchResponse DTO or None if DTOs unavailable
        """
        if not HAS_MUSIC_TUNEIN_DTO:
            logger.debug("DTO not available, falling back to legacy path")
            return None
        
        try:
            results = self.search_stations(query, limit)
            return MusicSearchResponse(results=[], totalCount=len(results))
        except Exception as e:
            logger.error(f"Error in search_stations_typed: {e}")
            return None

    def play_station(self, device_serial: str, device_type: str, station_id: str) -> bool:
        """Lance une station radio."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload: Dict[str, Any] = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "guideId": station_id,
                    "contentType": "station",
                }
                self._api_service.post(
                    "/api/tunein/queue-and-play",
                    payload=payload,
                )
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
                data = self._api_service.get("/api/tunein/favorites")
                if isinstance(data, dict):
                    return cast(list[dict[str, Any]], data.get("favorites", []))
                return []
            except Exception as e:
                logger.error(f"Erreur récupération favoris: {e}")
                return []

    def add_favorite(self, station_id: str) -> bool:
        """Ajoute une station aux favoris."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                self._api_service.post(
                    "/api/tunein/favorites",
                    payload={"guideId": station_id},
                )
                logger.success(f"Station {station_id} ajoutée aux favoris")
                return True
            except Exception as e:
                logger.error(f"Erreur ajout favori: {e}")
                return False
