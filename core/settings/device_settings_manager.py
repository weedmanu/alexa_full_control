"""
Gestionnaire des paramètres d'appareils - Thread-safe.
"""

import json
import re
import threading
from typing import Any, Dict, Optional, cast

from loguru import logger

from core.base_manager import BaseManager
from core.circuit_breaker import CircuitBreaker

from ..state_machine import AlexaStateMachine


class DeviceSettingsManager(BaseManager[Dict[str, Any]]):
    """Gestionnaire thread-safe des paramètres d'appareils.

    Utilise `http_client` (wrapper créé automatiquement à partir de `auth`
    si l'appelant passe encore un objet legacy). Cela permet la migration
    progressive vers `BaseManager`-style HTTP client.
    """

    def __init__(
        self,
        auth_or_http: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        api_service: Optional[Any] = None,
    ) -> None:
        # auth_or_http peut être soit l'ancien AuthClient, soit un http_client
        # compatible (ayant get/post/put/delete et attribut csrf)
        self.config = config
        state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()

        # Normaliser vers http_client (compatibilité legacy)
        try:
            from core.base_manager import create_http_client_from_auth

            # Si auth_or_http ressemble à un auth legacy, la fabrique retournera un wrapper
            http_client = (
                create_http_client_from_auth(auth_or_http) if hasattr(auth_or_http, "session") else auth_or_http
            )
        except Exception:
            http_client = getattr(auth_or_http, "session", auth_or_http)

        # Exposer également auth pour compatibilité code existant
        self.auth = getattr(auth_or_http, "auth", auth_or_http)
        # Optional centralized AlexaAPIService
        self._api_service: Optional[Any] = api_service

        # Appeler le constructeur parent pour initialiser les attributs de base
        super().__init__(http_client, config, state_machine)

        logger.info("DeviceSettingsManager initialisé")

    def get_device_settings(self, device_serial: str, device_type: str) -> Optional[Dict[Any, Any]]:
        """Récupère les paramètres d'un appareil."""
        if not self.state_machine.can_execute_commands:
            return None
        try:
            headers = {"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))}
            if self._api_service is not None:
                response = self._api_service.get(
                    f"/api/device-preferences/{device_serial}", headers=headers, timeout=10
                )
            else:
                response = self._api_call(
                    "get", r"/api/device-preferences/{device_serial}", headers=headers, timeout=10
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
            headers = {"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))}
            if self._api_service is not None:
                self.breaker.call(
                    self._api_service.put,
                    "/api/wake-word",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )
            else:
                self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/wake-word",
                    json=payload,
                    headers=headers,
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
            headers = {"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))}
            if self._api_service is not None:
                self.breaker.call(
                    self._api_service.put,
                    "/api/device-preferences/time-zone",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )
            else:
                self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/device-preferences/time-zone",
                    json=payload,
                    headers=headers,
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
            headers = {"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))}
            if self._api_service is not None:
                self.breaker.call(
                    self._api_service.put,
                    "/api/device-preferences/locale",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )
            else:
                self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/device-preferences/locale",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )
            logger.success(f"Langue: {locale}")
            return True
        except Exception as e:
            logger.error(f"Erreur langue: {e}")
            return False

    def set_volume(self, device_serial: str, device_type: str, volume: int, *, confirm: bool = False, timeout: int = 15) -> bool:
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

            headers = {"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))}
            if self._api_service is not None:
                self._api_service.post(r"/api/behaviors/preview", json=payload, headers=headers, timeout=10)
            else:
                self._api_call("post", r"/api/behaviors/preview", json=payload, headers=headers, timeout=10)

            # Invalidate cached allDeviceVolumes so subsequent reads are fresh
            try:
                cache_key = self._make_cache_key(r"/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes", {})
                if self.cache_service:
                    self.cache_service.invalidate(cache_key)
                    if getattr(self, '_debug_mode', False):
                        logger.debug(f"Invalidated cache: {cache_key}")
            except Exception:
                logger.debug("Impossible d'invalider le cache volumes")

            logger.success(f"Volume: {volume}%")

            if confirm:
                # poll up to timeout seconds for confirmation via direct auth.get (bypass cache)
                try:
                    import time

                    deadline = time.time() + int(timeout)
                    url = f"https://alexa.{self.auth.amazon_domain}/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes"
                    while time.time() < deadline:
                        try:
                            resp = self.auth.get(url, timeout=10)
                            js = resp.json() if resp is not None else None
                            observed = None
                            if isinstance(js, dict):
                                for v in js.get('volumes', []):
                                    dsn = v.get('dsn')
                                    if dsn is None:
                                        continue
                                    if str(dsn).strip().lower() == str(device_serial).strip().lower():
                                        observed = v.get('speakerVolume')
                                        break
                            if observed is not None and int(observed) == int(volume):
                                return True
                        except Exception:
                            pass
                        time.sleep(1)
                    # timed out
                    return False
                except Exception:
                    return False

            return True
        except Exception as e:
            logger.error(f"Erreur volume: {e}")
            return False

    def get_volume(self, device_serial: str, device_type: str) -> Optional[int]:
        """Récupère le volume actuel d'un appareil (0-100)."""
        if not self.state_machine.can_execute_commands:
            return None

        try:
            headers = {"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))}
            if self._api_service is not None:
                response = self._api_service.get(
                    r"/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes", headers=headers, timeout=10
                )
            else:
                response = self._api_call(
                    "get", r"/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes", headers=headers, timeout=10
                )
            data = response

            # Chercher le volume pour le device serial spécifié
            if data and "volumes" in data:
                # Helper to normalize ids: remove ALL whitespace/newlines and lowercase
                def _normalize_id(value: Any) -> str:
                    if value is None:
                        return ""
                    try:
                        s = str(value)
                    except Exception:
                        s = ""
                    # remove any whitespace (spaces, tabs, newlines) inside the id
                    return re.sub(r"\s+", "", s).lower()

                target = _normalize_id(device_serial)
                # Candidate volume keys in order of preference
                vol_keys = ("speakerVolume", "volume", "alertVolume")
                for volume_info in data["volumes"]:
                    dsn = volume_info.get("dsn")
                    if dsn is None:
                        continue
                    if _normalize_id(dsn) == target:
                        # return first available candidate
                        for k in vol_keys:
                            if k in volume_info and volume_info.get(k) is not None:
                                try:
                                    return cast(int | None, int(volume_info.get(k)))
                                except Exception:
                                    # fallback: return raw value
                                    return cast(int | None, volume_info.get(k))
                        # If none of the known keys present, attempt to find any numeric field
                        for k, v in volume_info.items():
                            if isinstance(v, int):
                                return cast(int | None, v)

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
            headers = {"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))}
            if self._api_service is not None:
                response = self._api_service.get(r"/api/bootstrap?version=0", headers=headers, timeout=10)
            else:
                response = self._api_call("get", r"/api/bootstrap?version=0", headers=headers, timeout=10)
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
