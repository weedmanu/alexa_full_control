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

import threading
from typing import Dict, List, Optional

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class PlaybackManager:
    """Gestionnaire de lecture musicale - API directe uniquement.

    Utilise exclusivement l'API /api/np/command pour tous les contrôles musicaux.
    Pas de fallback VoiceCommand - plus rapide mais moins tolérant aux erreurs.
    """

    def __init__(self, auth, config, state_machine=None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()

        # Initialiser VoiceCommandService pour les contrôles de lecture
        from services.voice_command_service import VoiceCommandService

        self.voice_service = VoiceCommandService(auth, config, state_machine)
        # Normalize http_client for migration compatibility
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth

        logger.info("PlaybackManager initialisé avec VoiceCommandService")

    def _send_np_command(self, command_data: Dict, device_serial: str, device_type: str) -> bool:
        """Envoie une commande directe à /api/np/command (comme le script shell)."""
        try:
            # Headers complets comme le script shell - CRITIQUE pour éviter 403/404
            headers = {
                "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", None)),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) bash-script/1.0",
                "DNT": "1",
                "Connection": "keep-alive",
                "Referer": f"https://{self.config.alexa_domain}/spa/index.html",
                "Origin": f"https://{self.config.alexa_domain}",
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "application/json",
                "Accept-Language": "fr-FR,fr;q=0.9",
            }

            response = self.breaker.call(
                self.http_client.post,
                f"https://{self.config.alexa_domain}/api/np/command",
                params={"deviceSerialNumber": device_serial, "deviceType": device_type},
                json=command_data,
                headers={**headers, "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            response.raise_for_status()
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
                logger.warning(f"Échec commande NP {command_data}: {e} - fallback vers VoiceCommand")
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
                payload = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "mediaPosition": position_ms,
                }
                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/np/command",
                    json=payload,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Position: {position_ms}ms")
                return True
            except Exception as e:
                logger.error(f"Erreur seek: {e}")
                return False

    def get_history(self, limit: int = 50) -> List[Dict]:
        """Récupère l'historique de lecture."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/media/history",
                    params={"size": limit},
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                return response.json().get("history", [])
            except Exception as e:
                logger.error(f"Erreur historique: {e}")
                return []

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
    ) -> Optional[Dict]:
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
                params = {"deviceSerialNumber": device_serial, "deviceType": device_type}

                # Ajouter parent si multiroom (comme le script shell)
                if parent_id:
                    params["lemurId"] = parent_id
                    if parent_type is not None:
                        params["lemurDeviceType"] = parent_type

                # Headers complets comme le script shell - CRITIQUE pour éviter 403
                headers = {
                    "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", None)),
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Referer": f"https://{self.config.alexa_domain}/spa/index.html",
                    "Origin": f"https://{self.config.alexa_domain}",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Accept": "application/json",
                    "Accept-Language": "fr-FR,fr;q=0.9",
                }

                # 1. État du player (comme show_queue() du shell)
                logger.debug(f"Récupération état player pour {device_serial}")
                player_response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/np/player",
                    params=params,
                    headers={**headers, "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                player_response.raise_for_status()
                player_data = player_response.json()

                # 2. État média
                logger.debug(f"Récupération état média pour {device_serial}")
                media_params = {"deviceSerialNumber": device_serial, "deviceType": device_type}
                media_response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/media/state",
                    params=media_params,
                    headers={**headers, "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                media_response.raise_for_status()
                media_data = media_response.json()

                # 3. Queue complète
                logger.debug(f"Récupération queue pour {device_serial}")
                queue_response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/np/queue",
                    params=media_params,
                    headers={**headers, "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                queue_response.raise_for_status()
                queue_data = queue_response.json()

                # Combiner les 3 réponses (comme le script shell)
                result = {"player": player_data, "media": media_data, "queue": queue_data}

                logger.success(f"État complet récupéré pour {device_serial}")
                return result

            except Exception as e:
                logger.error(f"Erreur récupération état complet: {e}")
                logger.debug(f"Détails erreur: {type(e).__name__}: {str(e)}")
                return None
