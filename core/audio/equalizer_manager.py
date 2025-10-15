"""
Gestionnaire d'égaliseur audio - Thread-safe.
"""

import threading
from typing import Dict, Optional

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class EqualizerManager:
    """Gestionnaire thread-safe de l'égaliseur."""

    def __init__(self, auth, config, state_machine=None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth
        logger.info("EqualizerManager initialisé")

    def get_equalizer(self, device_serial: str, device_type: str) -> Optional[Dict]:
        """Récupère les paramètres d'égaliseur."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/equalizer/{device_serial}/{device_type}",
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Erreur récupération égaliseur: {e}")
                return None

    def set_equalizer(self, device_serial: str, device_type: str, bass: int, midrange: int, treble: int) -> bool:
        """Définit l'égaliseur (bass, midrange, treble: -6 à +6)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            # Validation des valeurs
            for name, value in [("bass", bass), ("midrange", midrange), ("treble", treble)]:
                if not -6 <= value <= 6:
                    logger.error(f"{name} invalide: {value} (-6 à +6)")
                    return False

            try:
                payload = {"bass": bass, "midrange": midrange, "treble": treble}
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/equalizer/{device_serial}/{device_type}",
                    json=payload,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Égaliseur configuré: bass={bass}, mid={midrange}, treble={treble}")
                return True
            except Exception as e:
                logger.error(f"Erreur configuration égaliseur: {e}")
                return False
