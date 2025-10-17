"""
Gestionnaire de lecture musicale avancée - API directe uniquement.

Utilise exclusivement l'API /api/np/command pour les contrôles musicaux,
sans fallback VoiceCommand. Plus rapide et direct que les commandes vocales.

Fonctionnalités:
- Contrôles de lecture (play, pause, next, prev, stop)
- Mode aléatoire (shuffle on/off)
- Mode répétition (ONE, ALL - OFF non supporté par API)
- Positionnement (seek)
- Historique de lecture

Note: Aucune fallback VoiceCommand - si l'API échoue, la commande échoue.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from core.base_manager import BaseManager, create_http_client_from_auth
from core.state_machine import AlexaStateMachine

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.music_schemas import MusicStatusResponse, QueueResponse
    HAS_MUSIC_PLAYBACK_DTO = True
except ImportError:
    HAS_MUSIC_PLAYBACK_DTO = False


class PlaybackManager(BaseManager[Dict[str, Any]]):
    """Gestionnaire de lecture musicale - API directe uniquement.

    Utilise exclusivement l'API /api/np/command pour tous les contrôles musicaux.
    Pas de fallback VoiceCommand - plus rapide mais moins tolérant aux erreurs.
    """

    def __init__(
        self,
        auth: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        api_service: Optional[Any] = None,
    ) -> None:
        if api_service is None:
            raise ValueError("api_service is mandatory in Phase 2")
        
        http_client = create_http_client_from_auth(auth)
        if state_machine is None:
            state_machine = AlexaStateMachine()
        super().__init__(
            http_client=http_client, config=config, state_machine=state_machine, cache_service=None, cache_ttl=300
        )
        self.auth = auth  # Keep for backward compatibility
        # Mandatory AlexaAPIService for centralized API calls
        self._api_service: Any = api_service

        # Initialiser VoiceCommandService pour les contrôles de lecture
        from services.voice_command_service import VoiceCommandService

        self.voice_service = VoiceCommandService(auth, config, self.state_machine)
        logger.info("PlaybackManager initialisé avec AlexaAPIService obligatoire et VoiceCommandService")

    def _send_np_command(self, command_data: Dict[str, Any], device_serial: str, device_type: str) -> bool:
        """Envoie une commande directe à /api/np/command (comme le script shell)."""
        try:
            with self._lock:
                self._api_service.post(
                    "/api/np/command",
                    payload={"deviceSerialNumber": device_serial, "deviceType": device_type, **command_data},
                )
                logger.debug(f"Commande NP réussie: {command_data}")
                return True
        except Exception as e:
            command_type = command_data.get("type", "Unknown")
            # Pour certaines commandes (ShuffleCommand, RepeatCommand), 400 est normal
            # si elles ne sont pas supportées dans le contexte actuel
            if "400" in str(e) and command_type in ["ShuffleCommand", "RepeatCommand"]:
                logger.info(f"⚠️  Commande {command_type} non supportée dans ce contexte (normal)")
                return False
            else:
                logger.warning(f"Échec commande NP {command_data}: {e}")
                return False

    def set_shuffle(self, device_serial: str, device_type: str, enabled: bool) -> bool:
        """Active/désactive le mode aléatoire."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            # Utiliser l'API directe comme le script shell
            command_data = {"type": "ShuffleCommand", "shuffle": "true" if enabled else "false"}
            return self._send_np_command(command_data, device_serial, device_type)

    def set_repeat(self, device_serial: str, device_type: str, mode: str) -> bool:
        """Définit le mode répétition (OFF, ONE, ALL)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            valid_modes = ["OFF", "ONE", "ALL"]
            mode = mode.upper()
            if mode not in valid_modes:
                logger.error(f"Mode invalide: {mode} ({', '.join(valid_modes)})")
                return False

            # Utiliser l'API directe comme le script shell
            # Pour OFF, on n'envoie pas la commande (pas supporté dans le script shell)
            if mode == "OFF":
                logger.warning("Mode OFF non supporté par l'API directe")
                return False

            repeat_value = True  # Le script shell utilise "repeat": true pour ONE et ALL
            command_data = {"type": "RepeatCommand", "repeat": repeat_value}
            return self._send_np_command(command_data, device_serial, device_type)

    def play(self, device_serial: str, device_type: str) -> bool:
        """Lance la lecture."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            # Utiliser l'API directe comme le script shell
            command_data = {"type": "PlayCommand"}
            return self._send_np_command(command_data, device_serial, device_type)

    def pause(self, device_serial: str, device_type: str) -> bool:
        """Met en pause la lecture."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            # Utiliser l'API directe comme le script shell
            command_data = {"type": "PauseCommand"}
            return self._send_np_command(command_data, device_serial, device_type)

    def next_track(self, device_serial: str, device_type: str) -> bool:
        """Passe à la piste suivante."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            # Utiliser l'API directe comme le script shell
            command_data = {"type": "NextCommand"}
            return self._send_np_command(command_data, device_serial, device_type)

    def previous_track(self, device_serial: str, device_type: str) -> bool:
        """Revient à la piste précédente."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            # Utiliser l'API directe comme le script shell
            command_data = {"type": "PreviousCommand"}
            return self._send_np_command(command_data, device_serial, device_type)

    def stop(self, device_serial: str, device_type: str) -> bool:
        """Arrête la lecture."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            # Utiliser l'API directe comme le script shell (stop = pause)
            command_data = {"type": "PauseCommand"}
            return self._send_np_command(command_data, device_serial, device_type)

    def seek_to(self, device_serial: str, device_type: str, position_ms: int) -> bool:
        """Se déplace à une position spécifique (en millisecondes)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload: Dict[str, Any] = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "mediaPosition": position_ms,
                }
                self._api_service.put("/api/np/command", payload=payload)
                logger.success(f"Position: {position_ms}ms")
                return True
            except Exception as e:
                logger.error(f"Erreur seek: {e}")
                return False

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère l'historique de lecture."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self._api_service.get("/api/media/history", params={"size": limit})
                if isinstance(response, dict):
                    return response.get("history", [])  # type: ignore
                return []
            except Exception as e:
                logger.error(f"Erreur historique: {e}")
                return []

    def get_music_status_typed(self, device_serial: str, device_type: str) -> Optional["MusicStatusResponse"]:
        """
        Phase 3.7: Typed DTO version of get_state returning MusicStatusResponse.
        
        Returns music status as MusicStatusResponse DTO with full type safety.
        Falls back gracefully if DTOs not available.
        
        Args:
            device_serial: Device serial number
            device_type: Device type
            
        Returns:
            MusicStatusResponse DTO or None if DTOs unavailable
        """
        if not HAS_MUSIC_PLAYBACK_DTO:
            logger.debug("DTO not available, falling back to legacy path")
            return None
        
        try:
            # Get state as dict
            state_dict = self.get_state(device_serial, device_type)
            if not state_dict:
                return None
            
            # Try to build MusicStatusResponse from player data
            player_data = state_dict.get("player", {})
            return MusicStatusResponse(
                isPlaying=player_data.get("isPlaying", False),
                volume=player_data.get("volume", 0),
                currentTrack=None,  # Optional field
                progress=player_data.get("progress", 0),
                duration=player_data.get("duration"),
                queueLength=player_data.get("queueLength"),
                queueIndex=player_data.get("queueIndex")
            )
        except Exception as e:
            logger.error(f"Error in get_music_status_typed: {e}")
            return None

    def play_artist(self, device_serial: str, artist_name: str) -> bool:
        """Joue de la musique d'un artiste spécifique."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            # Utiliser VoiceCommandService pour jouer un artiste
            command = f"joue {artist_name}"
            return self.voice_service.speak(command, device_serial)

    def get_state(
        self,
        device_serial: str,
        device_type: str,
        parent_id: Optional[str] = None,
        parent_type: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Récupère l'état complet de la lecture (comme le script shell).

        Interroge 3 endpoints pour avoir toutes les informations:
        1. /api/np/player - État du player (morceau, artiste, progression)
        2. /api/media/state - État média détaillé
        3. /api/np/queue - File d'attente complète

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type de l'appareil
            parent_id: ID du parent multiroom (optionnel)
            parent_type: Type du parent multiroom (optionnel)

        Returns:
            Dict avec les clés 'player', 'media', 'queue' ou None si erreur
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None

            try:
                # Construire params comme le script shell
                params: Dict[str, Any] = {"deviceSerialNumber": device_serial, "deviceType": device_type}

                # Ajouter parent si multiroom (comme le script shell)
                if parent_id:
                    params["lemurId"] = parent_id
                    if parent_type is not None:
                        params["lemurDeviceType"] = parent_type

                # 1. État du player (comme show_queue() du shell)
                logger.debug(f"Récupération état player pour {device_serial}")
                player_data = self._api_service.get("/api/np/player", params=params)

                # 2. État média
                logger.debug(f"Récupération état média pour {device_serial}")
                media_params: Dict[str, Any] = {"deviceSerialNumber": device_serial, "deviceType": device_type}
                media_data = self._api_service.get("/api/media/state", params=media_params)

                # 3. Queue complète
                logger.debug(f"Récupération queue pour {device_serial}")
                queue_data = self._api_service.get("/api/np/queue", params=media_params)

                # Combiner les 3 réponses (comme le script shell)
                result: Dict[str, Any] = {"player": player_data, "media": media_data, "queue": queue_data}

                logger.success(f"État complet récupéré pour {device_serial}")
                return result

            except Exception as e:
                logger.error(f"Erreur récupération état complet: {e}")
                logger.debug(f"Détails erreur: {type(e).__name__}: {str(e)}")
                return None
