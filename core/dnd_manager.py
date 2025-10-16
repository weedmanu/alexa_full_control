"""
Gestionnaire DND (Do Not Disturb) Alexa - Thread-safe.
"""

import threading
from typing import Any, Dict, Optional

from loguru import logger

from .circuit_breaker import CircuitBreaker
from .state_machine import AlexaStateMachine


class DNDManager:
    """Gestionnaire thread-safe du mode Ne Pas Déranger."""

    def __init__(self, auth: Any, config: Any, state_machine: Optional[AlexaStateMachine] = None) -> None:
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
        logger.info("DNDManager initialisé")

    def get_dnd_status(self, device_serial: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut DND d'un appareil."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/dnd/status",
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                from typing import cast

                data = cast(Dict[str, Any], response.json())
                statuses = data.get("doNotDisturbDeviceStatusList", [])
                for status in statuses:
                    if status.get("deviceSerialNumber") == device_serial:
                        return cast(dict[str, Any] | None, status)
                return None
            except Exception as e:
                logger.error(f"Erreur récupération DND: {e}")
                return None

    def enable_dnd(self, device_serial: str, device_type: str) -> bool:
        """Active le mode DND."""
        return self._set_dnd(device_serial, device_type, enabled=True)

    def disable_dnd(self, device_serial: str, device_type: str) -> bool:
        """Désactive le mode DND."""
        return self._set_dnd(device_serial, device_type, enabled=False)

    def _set_dnd(self, device_serial: str, device_type: str, enabled: bool) -> bool:
        """Définit le statut DND."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "enabled": enabled,
                }
                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/dnd/status",
                    json=payload,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                action = "activé" if enabled else "désactivé"
                logger.success(f"DND {action} pour {device_serial}")
                return True
            except Exception as e:
                logger.error(f"Erreur configuration DND: {e}")
                return False

    def set_dnd_schedule(
        self,
        device_serial: str,
        device_type: str,
        start_hour: int,
        start_minute: int,
        end_hour: int,
        end_minute: int,
    ) -> bool:
        """Configure un horaire DND automatique."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                schedule = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "timeWindows": [
                        {
                            "startTime": f"{start_hour:02d}:{start_minute:02d}",
                            "endTime": f"{end_hour:02d}:{end_minute:02d}",
                        }
                    ],
                }
                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/dnd/device-status-list",
                    json=schedule,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Horaire DND configuré pour {device_serial}")
                return True
            except Exception as e:
                logger.error(f"Erreur configuration horaire DND: {e}")
                return False
