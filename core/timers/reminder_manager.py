"""
Gestionnaire de rappels Alexa - Thread-safe avec state machine.
"""

import threading
from typing import Any, Dict, List, Optional, cast

from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine
from services.cache_service import CacheService

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.reminder_schemas import GetRemindersResponse, ReminderDTO

    HAS_REMINDER_DTO = True
except ImportError:
    HAS_REMINDER_DTO = False

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.reminder_schemas import GetRemindersResponse, ReminderDTO

    HAS_REMINDER_DTO = True
except ImportError:
    HAS_REMINDER_DTO = False


class ReminderManager:
    """Gestionnaire thread-safe de rappels Alexa."""

    def __init__(
        self,
        auth: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        cache_service: Optional[CacheService] = None,
    ) -> None:
        self.auth = auth
        self.config = config
        self.state_machine: AlexaStateMachine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        self.cache_service = cache_service or CacheService()
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
    ) -> Optional[Dict[str, Any]]:
        """Crée un rappel."""
        with self._lock:
            if not self._check_connection():
                return None
            try:
                payload: Dict[str, Any] = {
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
                return cast(dict[str, Any] | None, response.json())
            except Exception as e:
                logger.error(f"Erreur création rappel: {e}")
                return None

    def list_reminders(self) -> List[Dict[str, Any]]:
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
                return cast(list[dict[str, Any]], response.json().get("reminders", []))
            except Exception as e:
                logger.error(f"Erreur liste rappels: {e}")
                return []

    def get_reminders_typed(self) -> Optional["GetRemindersResponse"]:
        """
        Phase 3.7: Typed DTO version of list_reminders returning GetRemindersResponse.

        Returns reminders as GetRemindersResponse DTO with full type safety.
        Falls back gracefully if DTOs not available.

        Returns:
            GetRemindersResponse DTO or None if DTOs unavailable
        """
        if not HAS_REMINDER_DTO:
            logger.debug("DTO not available, falling back to legacy path")
            return None

        try:
            from datetime import datetime, timezone

            # Get reminders as dict list
            reminders_list = self.list_reminders()

            # Convert to ReminderDTO objects
            reminder_dtos = []
            for r in reminders_list:
                try:
                    # Map dict to ReminderDTO with camelCase aliases
                    reminder_dict = {
                        "reminderId": r.get("id") or r.get("reminderId", f"reminder_{len(reminder_dtos)}"),
                        "label": r.get("label", "Reminder"),
                        "triggerTime": r.get("triggerTime") or datetime.now(timezone.utc),
                        "enabled": r.get("enabled", True),
                        "description": r.get("description"),
                    }
                    reminder_dtos.append(ReminderDTO(**reminder_dict))
                except Exception as e:
                    logger.warning(f"Could not convert reminder to DTO: {e}, skipping")
                    continue

            response = GetRemindersResponse(reminders=reminder_dtos)
            logger.debug(f"Returning {len(reminder_dtos)} reminders as DTO")
            return response

        except Exception as e:
            logger.error(f"Error in get_reminders_typed: {e}")
            return None

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
