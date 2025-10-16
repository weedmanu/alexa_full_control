"""
Gestionnaire Bluetooth - Thread-safe.
"""

from typing import Any, Dict, List, Optional, cast

from loguru import logger

from core.base_manager import BaseManager, create_http_client_from_auth

from ..state_machine import AlexaStateMachine


class BluetoothManager(BaseManager[Dict[str, Any]]):

    """Gestionnaire thread-safe Bluetooth."""

    def __init__(self, auth: Any, config: Any, state_machine: Optional[AlexaStateMachine] = None) -> None:
        http_client = create_http_client_from_auth(auth)
        if state_machine is None:
            state_machine = AlexaStateMachine()
        super().__init__(
            http_client=http_client,
            config=config,
            state_machine=state_machine,
        )
        self.auth = auth
        logger.info("BluetoothManager initialisé")

    def get_paired_devices(self, device_serial: str, device_type: str) -> List[Dict[Any, Any]]:
        """Récupère les appareils Bluetooth appairés."""
        if not self.state_machine.can_execute_commands:
            return []
        try:
            response = self._api_call("get", r"/api/bluetooth",
                params={"deviceSerialNumber": device_serial, "deviceType": device_type},
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            return cast(List[Dict[Any, Any]], response.get("bluetoothStates", []) if response else [])
        except Exception as e:
            logger.error(f"Erreur récupération Bluetooth: {e}")
            return []

    def connect_device(self, device_serial: str, device_type: str, bt_address: str) -> bool:
        """Connecte un appareil Bluetooth."""
        if not self.state_machine.can_execute_commands:
            return False
        try:
            payload = {
                "deviceSerialNumber": device_serial,
                "deviceType": device_type,
                "bluetoothDeviceAddress": bt_address,
            }
            self._api_call("post", r"/api/bluetooth/pair-sink/{device_type}/{device_serial}",
                json=payload,
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            logger.success(f"Appareil Bluetooth connecté: {bt_address}")
            return True
        except Exception as e:
            logger.error(f"Erreur connexion Bluetooth: {e}")
            return False

    def disconnect_device(self, device_serial: str, device_type: str) -> bool:
        """Déconnecte l'appareil Bluetooth actuel."""
        if not self.state_machine.can_execute_commands:
            return False
        try:
            self._api_call("post", r"/api/bluetooth/disconnect-sink/{device_type}/{device_serial}",
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            logger.success("Appareil Bluetooth déconnecté")
            return True
        except Exception as e:
            logger.error(f"Erreur déconnexion Bluetooth: {e}")
            return False
