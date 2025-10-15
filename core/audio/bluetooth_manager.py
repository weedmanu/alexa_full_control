"""
Gestionnaire Bluetooth - Thread-safe.
"""

import threading
from typing import Dict, List

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class BluetoothManager:
    """Gestionnaire thread-safe Bluetooth."""

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
        logger.info("BluetoothManager initialisé")

    def get_paired_devices(self, device_serial: str, device_type: str) -> List[Dict]:
        """Récupère les appareils Bluetooth appairés."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/bluetooth",
                    params={"deviceSerialNumber": device_serial, "deviceType": device_type},
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                return response.json().get("bluetoothStates", [])
            except Exception as e:
                logger.error(f"Erreur récupération Bluetooth: {e}")
                return []

    def connect_device(self, device_serial: str, device_type: str, bt_address: str) -> bool:
        """Connecte un appareil Bluetooth."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "bluetoothDeviceAddress": bt_address,
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/bluetooth/pair-sink/{device_type}/{device_serial}",
                    json=payload,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Appareil Bluetooth connecté: {bt_address}")
                return True
            except Exception as e:
                logger.error(f"Erreur connexion Bluetooth: {e}")
                return False

    def disconnect_device(self, device_serial: str, device_type: str) -> bool:
        """Déconnecte l'appareil Bluetooth actuel."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/bluetooth/disconnect-sink/{device_type}/{device_serial}",
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success("Appareil Bluetooth déconnecté")
                return True
            except Exception as e:
                logger.error(f"Erreur déconnexion Bluetooth: {e}")
                return False
