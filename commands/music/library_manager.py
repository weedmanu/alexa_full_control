"""
Gestionnaire de biblioth�que musicale - Utilise VoiceCommandService.

Ce module g�re la musique en utilisant VoiceCommandService au lieu
d'une biblioth�que locale qui n'existe pas.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from core.base_manager import BaseManager, create_http_client_from_auth
from core.state_machine import AlexaStateMachine

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.music_schemas import MusicLibraryResponse, MusicSearchResponse  # noqa: F401

    HAS_MUSIC_LIBRARY_DTO = True
except ImportError:
    HAS_MUSIC_LIBRARY_DTO = False


class LibraryManager(BaseManager[Dict[str, Any]]):
    """
    Gestionnaire de biblioth�que musicale utilisant VoiceCommandService.

    Au lieu d'acc�der � une biblioth�que locale inexistante, utilise
    VoiceCommandService pour jouer de la musique par nom.
    """

    def __init__(
        self,
        auth: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        voice_service: Optional[Any] = None,
    ):
        """
        Initialise le gestionnaire de biblioth�que.

        Args:
            auth: Service d'authentification
            config: Configuration
            state_machine: Machine � �tats (optionnel)
            voice_service: Service de commandes vocales (optionnel)
        """
        http_client = create_http_client_from_auth(auth)
        if state_machine is None:
            state_machine = AlexaStateMachine()
        super().__init__(
            http_client=http_client,
            config=config,
            state_machine=state_machine,
        )
        self.auth = auth
        self.voice_service = voice_service
        logger.info("LibraryManager initialis� (VoiceCommand-based)")

    def search_music(
        self, query: str, search_type: str = "track", provider: str = "AMAZON_MUSIC"
    ) -> List[Dict[str, Any]]:
        """
        Recherche de musique (simulation - retourne un r�sultat fictif).

        Args:
            query: Terme de recherche
            search_type: Type de recherche (track, artist, album)
            provider: Service musical

        Returns:
            Liste de r�sultats (toujours un r�sultat fictif pour permettre la lecture)
        """
        logger.debug(f"Recherche simul�e: '{query}' (type: {search_type})")

        # Retourne un r�sultat fictif pour permettre la lecture
        # VoiceCommandService g�rera la recherche r�elle
        return [
            {
                "id": f"voice_command_{query.replace(' ', '_')}",
                "title": query,
                "artist": "Recherche vocale",
                "type": search_type,
                "provider": provider,
            }
        ]

    def search_music_typed(self, query: str, search_type: str = "MUSIC") -> Optional["MusicSearchResponse"]:
        """
        Phase 3.7: Typed DTO version of search_music returning MusicSearchResponse.

        Returns search results as MusicSearchResponse DTO with full type safety.
        Falls back gracefully if DTOs not available.

        Args:
            query: Search query
            search_type: Type of search (MUSIC, PLAYLIST, ARTIST, etc)

        Returns:
            MusicSearchResponse DTO or None if DTOs unavailable
        """
        if not HAS_MUSIC_LIBRARY_DTO:
            logger.debug("DTO not available, falling back to legacy path")
            return None

        try:
            results = self.search_music(query, search_type)
            return MusicSearchResponse(results=[], totalCount=len(results))
        except Exception as e:
            logger.error(f"Error in search_music_typed: {e}")
            return None

    def play_track(self, device_serial: str, device_type: str, track_id: str, provider: str = "AMAZON_MUSIC") -> bool:
        """
        Joue une piste en utilisant VoiceCommandService.

        Args:
            device_serial: Serial de l'appareil
            device_type: Type d'appareil
            track_id: ID de la piste (ignor�, on utilise le nom)
            provider: Service musical (ignor� pour VoiceCommand)

        Returns:
            True si succ�s
        """
        if not self.voice_service:
            logger.error("VoiceCommandService non disponible")
            return False

        if not self.state_machine.can_execute_commands:
            logger.warning("�tat syst�me ne permet pas l'ex�cution")
            return False

        try:
            # Extraire le nom de la chanson depuis l'ID fictif
            song_name = track_id.replace("voice_command_", "").replace("_", " ")

            logger.info(f"Jouer '{song_name}' via VoiceCommand")

            # Utiliser VoiceCommandService pour jouer la musique
            result = self.voice_service.speak(f"joue {song_name}", device_serial, device_type)

            if result:
                logger.success(f"Musique '{song_name}' lanc�e")
                return True
            else:
                logger.error(f"�chec lancement musique '{song_name}'")
                return False

        except Exception as e:
            logger.error(f"Erreur lors de la lecture: {e}")
            return False

    def get_playlists(self, provider: str = "AMAZON_MUSIC") -> List[Dict[str, Any]]:
        """
        R�cup�re les playlists (simulation).

        Args:
            provider: Service musical

        Returns:
            Liste vide (pas de playlists locales)
        """
        logger.debug(f"R�cup�ration playlists {provider} (vide)")
        return []

    def play_playlist(self, device_serial: str, device_type: str, playlist_id: str, shuffle: bool = False) -> bool:
        """
        Joue une playlist (non support�).

        Args:
            device_serial: Serial de l'appareil
            device_type: Type d'appareil
            playlist_id: ID de la playlist
            shuffle: Mode al�atoire

        Returns:
            False (non support�)
        """
        # mark unused parameters to silence dead-code detectors
        _ = playlist_id
        _ = shuffle
        logger.warning("Lecture de playlist non support�e (pas de playlists locales)")
        return False




