"""
Gestionnaire des paramètres d'appareils - Thread-safe.
"""

import json
import threading
from typing import Any, Dict, Optional, cast

from core.base_manager import BaseManager, create_http_client_from_auth
from core.circuit_breaker import CircuitBreaker
from loguru import logger

from ..state_machine import AlexaStateMachine


class DeviceSettingsManager(BaseManager[Dict[str, Any]]):

    """Gestionnaire thread-safe des paramètres d'appareils.

    Utilise `http_client` (wrapper créé automatiquement à partir de `auth`
    si l'appelant passe encore un objet legacy). Cela permet la migration
    progressive vers `BaseManager`-style HTTP client.
    """

    def __init__(self, auth_or_http: Any, config: Any, state_machine: Optional[AlexaStateMachine] = None) -> None:
        # auth_or_http peut être soit l'ancien AuthClient, soit un http_client
        # compatible (ayant get/post/put/delete et attribut csrf)
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()

        # Normaliser vers http_client (compatibilité legacy)
        try:
            from core.base_manager import create_http_client_from_auth

            # Si auth_or_http ressemble à un auth legacy, la fabrique retournera un wrapper
            self.http_client = (
                create_http_client_from_auth(auth_or_http) if hasattr(auth_or_http, "session") else auth_or_http
            )
        except Exception:
            self.http_client = getattr(auth_or_http, "session", auth_or_http)

        # Exposer également auth pour compatibilité code existant
        self.auth = getattr(auth_or_http, "auth", auth_or_http)

        logger.info("DeviceSettingsManager initialisé")

    def get_device_settings(self, device_serial: str, device_type: str) -> Optional[Dict[Any, Any]]:
        """Récupère les paramètres d'un appareil."""
        if not self.state_machine.can_execute_commands:
            return None
        try:
            response = self._api_call("get", r"/api/device-preferences/{device_serial}",
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            return cast(Optional[Dict[Any, Any]], response)
        except Exception as e:
            logger.error(f"Erreur récupération paramètres: {e}")
            return None

    def set_wake_word(self, device_serial: str, device_type: str, wake_word: str) -> bool:
        """Définit le mot d'activation (ALEXA, AMAZON, ECHO, COMPUTER)."""
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
                self.http_client.put,
                f"https://{self.config.alexa_domain}/api/wake-word",
                json=payload,
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            logger.success(f"Mot d'activation: {wake_word}")
            return True
        except Exception as e:
            logger.error(f"Erreur mot d'activation: {e}")
            return False

    def set_timezone(self, device_serial: str, device_type: str, timezone: str) -> bool:
        """Définit le fuseau horaire (ex: Europe/Paris)."""
        if not self.state_machine.can_execute_commands:
            return False
        try:
            payload = {
                "deviceSerialNumber": device_serial,
                "deviceType": device_type,
                "timeZoneId": timezone,
            }
            response = self.breaker.call(
                self.http_client.put,
                f"https://{self.config.alexa_domain}/api/device-preferences/time-zone",
                json=payload,
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            logger.success(f"Fuseau horaire: {timezone}")
            return True
        except Exception as e:
            logger.error(f"Erreur fuseau horaire: {e}")
            return False

    def set_locale(self, device_serial: str, device_type: str, locale: str) -> bool:
        """Définit la langue/locale (ex: fr-FR, en-US)."""
        if not self.state_machine.can_execute_commands:
            return False
        try:
            payload = {
                "deviceSerialNumber": device_serial,
                "deviceType": device_type,
                "locale": locale,
            }
            response = self.breaker.call(
                self.http_client.put,
                f"https://{self.config.alexa_domain}/api/device-preferences/locale",
                json=payload,
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            logger.success(f"Langue: {locale}")
            return True
        except Exception as e:
            logger.error(f"Erreur langue: {e}")
            return False

    def set_volume(self, device_serial: str, device_type: str, volume: int) -> bool:
        """Définit le volume (0-100)."""
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

            response = self._api_call("post", r"/api/behaviors/preview",
                json=payload,
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            logger.success(f"Volume: {volume}%")
            return True
        except Exception as e:
            logger.error(f"Erreur volume: {e}")
            return False

    def get_volume(self, device_serial: str, device_type: str) -> Optional[int]:
        """Récupère le volume actuel d'un appareil (0-100)."""
        if not self.state_machine.can_execute_commands:
            return None

        try:
            response = self._api_call("get", r"/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes",
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            data = response

            # Chercher le volume pour le device serial spécifié
            if data and "volumes" in data:
                for volume_info in data["volumes"]:
                    if volume_info.get("dsn") == device_serial:
                        return cast(int | None, volume_info.get("speakerVolume"))

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
            response = self._api_call("get", r"/api/bootstrap?version=0",
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            data = response

            customer_id = data.get("authentication", {}).get("customerId") if data else None
            if customer_id:
                logger.debug(f"Customer ID: {customer_id}")
                return cast(str | None, customer_id)
            else:
                logger.warning("Customer ID non trouvé dans bootstrap")
                return None

        except Exception as e:
            logger.error(f"Erreur récupération customer ID: {e}")
        return None
