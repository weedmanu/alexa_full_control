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
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/reminders",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
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
                    self.auth.session.get,
                    f"https://{self.config.alexa_domain}/api/reminders",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
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
                    self.auth.session.delete,
                    f"https://{self.config.alexa_domain}/api/reminders/{reminder_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "csrf": self.auth.csrf,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Rappel {reminder_id} supprimé")
                return True
            except Exception as e:
                logger.error(f"Erreur suppression rappel: {e}")
                return False
