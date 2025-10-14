"""
Gestionnaire de bibliothèque musicale - Utilise VoiceCommandService.

Ce module gère la musique en utilisant VoiceCommandService au lieu
d'une bibliothèque locale qui n'existe pas.
"""

import threading
from typing import Any, Dict, List, Optional

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class LibraryManager:
    """
    Gestionnaire de bibliothèque musicale utilisant VoiceCommandService.

    Au lieu d'accéder à une bibliothèque locale inexistante, utilise
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
        Initialise le gestionnaire de bibliothèque.

        Args:
            auth: Service d'authentification
            config: Configuration
            state_machine: Machine à états (optionnel)
            voice_service: Service de commandes vocales (optionnel)
        """
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.voice_service = voice_service
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()

        logger.info("LibraryManager initialisé (VoiceCommand-based)")

    def search_music(
        self, query: str, search_type: str = "track", provider: str = "AMAZON_MUSIC"
    ) -> List[Dict[str, Any]]:
        """
        Recherche de musique (simulation - retourne un résultat fictif).

        Args:
            query: Terme de recherche
            search_type: Type de recherche (track, artist, album)
            provider: Service musical

        Returns:
            Liste de résultats (toujours un résultat fictif pour permettre la lecture)
        """
        with self._lock:
            logger.debug(f"Recherche simulée: '{query}' (type: {search_type})")

            # Retourne un résultat fictif pour permettre la lecture
            # VoiceCommandService gérera la recherche réelle
            return [
                {
                    "id": f"voice_command_{query.replace(' ', '_')}",
                    "title": query,
                    "artist": "Recherche vocale",
                    "type": search_type,
                    "provider": provider,
                }
            ]

    def play_track(
        self, device_serial: str, device_type: str, track_id: str, provider: str = "AMAZON_MUSIC"
    ) -> bool:
        """
        Joue une piste en utilisant VoiceCommandService.

        Args:
            device_serial: Serial de l'appareil
            device_type: Type d'appareil
            track_id: ID de la piste (ignoré, on utilise le nom)
            provider: Service musical (ignoré pour VoiceCommand)

        Returns:
            True si succès
        """
        with self._lock:
            if not self.voice_service:
                logger.error("VoiceCommandService non disponible")
                return False

            if not self.state_machine.can_execute_commands:
                logger.warning("État système ne permet pas l'exécution")
                return False

            try:
                # Extraire le nom de la chanson depuis l'ID fictif
                song_name = track_id.replace("voice_command_", "").replace("_", " ")

                logger.info(f"Jouer '{song_name}' via VoiceCommand")

                # Utiliser VoiceCommandService pour jouer la musique
                result = self.voice_service.speak(f"joue {song_name}", device_serial, device_type)

                if result:
                    logger.success(f"Musique '{song_name}' lancée")
                    return True
                else:
                    logger.error(f"Échec lancement musique '{song_name}'")
                    return False

            except Exception as e:
                logger.error(f"Erreur lors de la lecture: {e}")
                return False

    def get_playlists(self, provider: str = "AMAZON_MUSIC") -> List[Dict[str, Any]]:
        """
        Récupère les playlists (simulation).

        Args:
            provider: Service musical

        Returns:
            Liste vide (pas de playlists locales)
        """
        with self._lock:
            logger.debug(f"Récupération playlists {provider} (vide)")
            return []

    def play_playlist(
        self, device_serial: str, device_type: str, playlist_id: str, shuffle: bool = False
    ) -> bool:
        """
        Joue une playlist (non supporté).

        Args:
            device_serial: Serial de l'appareil
            device_type: Type d'appareil
            playlist_id: ID de la playlist
            shuffle: Mode aléatoire

        Returns:
            False (non supporté)
        """
        with self._lock:
            logger.warning("Lecture de playlist non supportée (pas de playlists locales)")
            return False
