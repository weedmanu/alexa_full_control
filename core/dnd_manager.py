"""
Gestionnaire DND (Do Not Disturb) Alexa - Thread-safe.
"""

from typing import Any, Dict, Optional, cast

from loguru import logger

from .base_manager import BaseManager, create_http_client_from_auth
from .state_machine import AlexaStateMachine


class DNDManager(BaseManager[Dict[str, Any]]):
    """Gestionnaire thread-safe du mode Ne Pas Déranger."""

    def __init__(
        self,
        auth: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        api_service: Optional[Any] = None,
    ) -> None:
        # Créer le client HTTP depuis auth
        http_client = create_http_client_from_auth(auth)

        # Initialiser BaseManager
        super().__init__(
            http_client=http_client,
            config=config,
            state_machine=state_machine or AlexaStateMachine(),
        )

        # Attributs spécifiques à DNDManager
        self.auth = auth
        # Optional AlexaAPIService for future centralized API calls
        self._api_service: Optional[Any] = api_service

        logger.info("DNDManager initialisé")

    def get_dnd_status(self, device_serial: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut DND d'un appareil."""
        if not self._check_connection():
            return None
        try:
            # Prefer api_service if injected
            if getattr(self, "_api_service", None) is not None:
                try:
                    data = self._api_service.get("/api/dnd/status")
                except Exception:
                    data = self._api_call("get", "/api/dnd/status", timeout=10)
            else:
                data = self._api_call("get", "/api/dnd/status", timeout=10)
            if data is None:
                return None

            statuses = data.get("doNotDisturbDeviceStatusList", [])
            for status in statuses:
                if status.get("deviceSerialNumber") == device_serial:
                    return cast(Dict[str, Any], status)
            return None
        except Exception as e:
            self.logger.error(f"Erreur récupération DND: {e}")
            return None

    def enable_dnd(self, device_serial: str, device_type: str) -> bool:
        """Active le mode DND."""
        return self._set_dnd(device_serial, device_type, enabled=True)

    def disable_dnd(self, device_serial: str, device_type: str) -> bool:
        """Désactive le mode DND."""
        return self._set_dnd(device_serial, device_type, enabled=False)

    def _set_dnd(self, device_serial: str, device_type: str, enabled: bool) -> bool:
        """Définit le statut DND."""
        if not self._check_connection():
            return False
        try:
            payload = {
                "deviceSerialNumber": device_serial,
                "deviceType": device_type,
                "enabled": enabled,
            }
            # Prefer api_service
            if getattr(self, "_api_service", None) is not None:
                try:
                    result = self._api_service.put("/api/dnd/status", payload=payload)
                except Exception:
                    result = self._api_call("put", "/api/dnd/status", json=payload, timeout=10)
            else:
                result = self._api_call("put", "/api/dnd/status", json=payload, timeout=10)
            if result is not None:
                action = "activé" if enabled else "désactivé"
                self.logger.success(f"DND {action} pour {device_serial}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur configuration DND: {e}")
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
        if not self._check_connection():
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
            # Prefer api_service
            if getattr(self, "_api_service", None) is not None:
                try:
                    result = self._api_service.put("/api/dnd/device-status-list", payload=schedule)
                except Exception:
                    result = self._api_call("put", "/api/dnd/device-status-list", json=schedule, timeout=10)
            else:
                result = self._api_call("put", "/api/dnd/device-status-list", json=schedule, timeout=10)
            if result is not None:
                self.logger.success(f"Horaire DND configuré pour {device_serial}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur configuration horaire DND: {e}")
            return False
