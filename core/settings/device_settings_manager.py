"""
Gestionnaire des paramètres d'appareils - Thread-safe.
"""

import json
import threading
from typing import Dict, Optional

from loguru import logger

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine


class DeviceSettingsManager:
    """Gestionnaire thread-safe des paramètres d'appareils."""

    def __init__(self, auth, config, state_machine=None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        logger.info("DeviceSettingsManager initialisé")

    def get_device_settings(self, device_serial: str, device_type: str) -> Optional[Dict]:
        """Récupère les paramètres d'un appareil."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None
            try:
                response = self.breaker.call(
                    self.auth.session.get,
                    f"https://{self.config.alexa_domain}/api/device-preferences/{device_serial}",
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Erreur récupération paramètres: {e}")
                return None

    def set_wake_word(self, device_serial: str, device_type: str, wake_word: str) -> bool:
        """Définit le mot d'activation (ALEXA, AMAZON, ECHO, COMPUTER)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False

            valid_words = ["ALEXA", "AMAZON", "ECHO", "COMPUTER"]
            wake_word = wake_word.upper()
            if wake_word not in valid_words:
                logger.error(f"Mot invalide: {wake_word} ({', '.join(valid_words)})")
                return False

            try:
                payload = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "wakeWord": wake_word,
                }
                response = self.breaker.call(
                    self.auth.session.put,
                    f"https://{self.config.alexa_domain}/api/wake-word",
                    json=payload,
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Mot d'activation: {wake_word}")
                return True
            except Exception as e:
                logger.error(f"Erreur mot d'activation: {e}")
                return False

    def set_timezone(self, device_serial: str, device_type: str, timezone: str) -> bool:
        """Définit le fuseau horaire (ex: Europe/Paris)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "timeZoneId": timezone,
                }
                response = self.breaker.call(
                    self.auth.session.put,
                    f"https://{self.config.alexa_domain}/api/device-preferences/time-zone",
                    json=payload,
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Fuseau horaire: {timezone}")
                return True
            except Exception as e:
                logger.error(f"Erreur fuseau horaire: {e}")
                return False

    def set_locale(self, device_serial: str, device_type: str, locale: str) -> bool:
        """Définit la langue/locale (ex: fr-FR, en-US)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "locale": locale,
                }
                response = self.breaker.call(
                    self.auth.session.put,
                    f"https://{self.config.alexa_domain}/api/device-preferences/locale",
                    json=payload,
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Langue: {locale}")
                return True
            except Exception as e:
                logger.error(f"Erreur langue: {e}")
                return False

    def set_volume(self, device_serial: str, device_type: str, volume: int) -> bool:
        """Définit le volume (0-100)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            if not 0 <= volume <= 100:
                logger.error(f"Volume invalide: {volume} (0-100)")
                return False

            try:
                # Récupérer le customer ID depuis bootstrap
                customer_id = self._get_customer_id()
                if not customer_id:
                    logger.error("Impossible de récupérer le customer ID")
                    return False

                # Utiliser l'endpoint behaviors/preview comme dans le script shell
                sequence_json = {
                    "@type": "com.amazon.alexa.behaviors.model.Sequence",
                    "startNode": {
                        "@type": "com.amazon.alexa.behaviors.model.ParallelNode",
                        "nodesToExecute": [
                            {
                                "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
                                "type": "Alexa.DeviceControls.Volume",
                                "operationPayload": {
                                    "deviceType": device_type,
                                    "deviceSerialNumber": device_serial,
                                    "customerId": customer_id,
                                    "locale": self.config.tts_locale,
                                    "value": str(volume),
                                },
                            }
                        ],
                    },
                }

                payload = {
                    "behaviorId": "PREVIEW",
                    "sequenceJson": json.dumps(sequence_json),
                    "status": "ENABLED",
                }

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/behaviors/preview",
                    json=payload,
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Volume: {volume}%")
                return True
            except Exception as e:
                logger.error(f"Erreur volume: {e}")
                return False

    def get_volume(self, device_serial: str, device_type: str) -> Optional[int]:
        """Récupère le volume actuel d'un appareil (0-100)."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None

            try:
                response = self.breaker.call(
                    self.auth.session.get,
                    f"https://{self.config.alexa_domain}/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes",
                    headers={"csrf": self.auth.csrf},
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                # Chercher le volume pour le device serial spécifié
                if "volumes" in data:
                    for volume_info in data["volumes"]:
                        if volume_info.get("dsn") == device_serial:
                            return volume_info.get("speakerVolume")

                return None

            except Exception as e:
                logger.error(f"Erreur récupération volume: {e}")
                return None

    def _get_customer_id(self) -> Optional[str]:
        """
        Récupère le customer ID via /api/bootstrap.

        Returns:
            Customer ID ou None si erreur
        """
        try:
            url = f"https://{self.config.alexa_domain}/api/bootstrap?version=0"
            response = self.breaker.call(
                self.auth.session.get,
                url,
                headers={"csrf": self.auth.csrf},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            customer_id = data.get("authentication", {}).get("customerId")
            if customer_id:
                logger.debug(f"Customer ID: {customer_id}")
                return customer_id
            else:
                logger.warning("Customer ID non trouvé dans bootstrap")
                return None

        except Exception as e:
            logger.error(f"Erreur récupération customer ID: {e}")
            return None
