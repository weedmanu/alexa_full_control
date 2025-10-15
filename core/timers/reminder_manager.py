"""
Gestionnaire de rappels Alexa - Thread-safe avec state machine.
"""

import threading
from typing import Dict, List, Optional

from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine


class ReminderManager:
    """Gestionnaire thread-safe de rappels Alexa."""

    def __init__(self, auth, config, state_machine: Optional[AlexaStateMachine] = None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        logger.info("ReminderManager initialisé")
        # Normaliser vers http_client pour migration progressive
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth

    def _check_connection(self) -> bool:
        return self.state_machine.can_execute_commands

    def create_reminder(
        self,
        text: str,
        alarm_time: str,
        device_serial: str,
        device_type: str,
        recurring: Optional[str] = None,
    ) -> Optional[Dict]:
        """Crée un rappel."""
        with self._lock:
            if not self._check_connection():
                return None
            try:
                payload = {
                    "type": "Reminder",
                    "status": "ON",
                    "reminderLabel": text,
                    "alarmTime": alarm_time,
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "recurringPattern": recurring,
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/reminders",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Rappel '{text}' créé")
                return response.json()
            except Exception as e:
                logger.error(f"Erreur création rappel: {e}")
                return None

    def list_reminders(self) -> List[Dict]:
        """Liste tous les rappels."""
        with self._lock:
            if not self._check_connection():
                return []
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/reminders",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    timeout=10,
                )
                response.raise_for_status()
                return response.json().get("reminders", [])
            except Exception as e:
                logger.error(f"Erreur liste rappels: {e}")
                return []

    def delete_reminder(self, reminder_id: str) -> bool:
        """Supprime un rappel."""
        with self._lock:
            if not self._check_connection():
                return False
            try:
                response = self.breaker.call(
                    self.http_client.delete,
                    f"https://{self.config.alexa_domain}/api/reminders/{reminder_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Rappel {reminder_id} supprimé")
                return True
            except Exception as e:
                logger.error(f"Erreur suppression rappel: {e}")
                return False
