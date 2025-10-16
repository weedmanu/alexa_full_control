"""
Contrôleur pour lumières connectées - Thread-safe.
"""

import time
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from core.base_manager import BaseManager
from services.cache_service import CacheService
from services.voice_command_service import VoiceCommandService

from ..circuit_breaker import CircuitBreaker
from ..state_machine import AlexaStateMachine

# Couleurs prédéfinies (HSB)
COLOR_PRESETS = {
    "warm_white": (30, 0.3, 1.0),  # Blanc chaud
    "cool_white": (210, 0.15, 1.0),  # Blanc froid
    "red": (0, 1.0, 1.0),  # Rouge
    "green": (120, 1.0, 1.0),  # Vert
    "blue": (240, 1.0, 1.0),  # Bleu
    "yellow": (60, 1.0, 1.0),  # Jaune
    "purple": (280, 1.0, 1.0),  # Violet
    "pink": (330, 0.7, 1.0),  # Rose
}


class LightController(BaseManager[Dict[str, Any]]):
    """Contrôleur thread-safe pour lumières connectées.

    Hérite de BaseManager pour bénéficier du cache mémoire/disque,
    du verrou thread-safe et du client HTTP unifié `self.http_client`.
    """

    def __init__(
        self,
        http_client: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        cache_service: Optional[CacheService] = None,
    ) -> None:
        # Initialise BaseManager avec un TTL mémoire local de 300s
        super().__init__(http_client, config, state_machine or AlexaStateMachine(), cache_service, cache_ttl=300)

        # Circuit breaker spécifique au controller
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)

        # Cache local pour lights (mémoire)
        self._lights_cache: Optional[List[Dict[str, Any]]] = None
        # timestamp et ttl pour le cache en mémoire
        self._cache_timestamp: float = 0.0
        self._cache_ttl: int = 300

        # Assurer la présence du http_client pour la migration (compatibilité)
        try:
            from core.base_manager import create_http_client_from_auth

            # create_http_client_from_auth accepte soit un auth legacy, soit un http client
            self.http_client = create_http_client_from_auth(http_client)
        except Exception:
            # Fallback conservateur
            self.http_client = http_client

        # Voice Command Service: si un auth legacy est présent dans http_client,
        # on l'utilise pour conserver le comportement existant.
        raw_auth = (
            getattr(self.http_client, "_session", None)
            or getattr(self.http_client, "auth", None)
            or self.http_client
        )
        try:
            self._voice_service = VoiceCommandService(raw_auth, config, self.state_machine)
        except Exception:
            # Fallback safe
            self._voice_service = VoiceCommandService(self.http_client, config, self.state_machine)

        logger.info("LightController initialisé")

    def set_brightness(self, entity_id: str, brightness: int) -> bool:
        """Définit la luminosité (0-100)."""
        with self._lock:
            if not self._check_connection():
                return False
            if not 0 <= brightness <= 100:
                logger.error(f"Luminosité invalide: {brightness} (0-100)")
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.BrightnessController",
                            "name": "SetBrightness",
                            "messageId": f"brightness-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {"brightness": brightness},
                    }
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/phoenix",
                    json=directive,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Luminosité {brightness}% pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur luminosité: {e}")
                return False

    def set_color(self, entity_id: str, hue: float, saturation: float, brightness: float) -> bool:
        """Définit la couleur HSB (Hue 0-360, Saturation 0-1, Brightness 0-1)."""
        with self._lock:
            if not self._check_connection():
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.ColorController",
                            "name": "SetColor",
                            "messageId": f"color-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {
                            "color": {
                                "hue": hue,
                                "saturation": saturation,
                                "brightness": brightness,
                            }
                        },
                    }
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/phoenix",
                    json=directive,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Couleur définie pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur couleur: {e}")
                return False

    def set_color_temperature(self, entity_id: str, kelvin: int) -> bool:
        """Définit la température de couleur (2200-7000 Kelvin)."""
        with self._lock:
            if not self._check_connection():
                return False
            if not 2200 <= kelvin <= 7000:
                logger.error(f"Température invalide: {kelvin}K (2200-7000)")
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.ColorTemperatureController",
                            "name": "SetColorTemperature",
                            "messageId": f"temp-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {"colorTemperatureInKelvin": kelvin},
                    }
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/phoenix",
                    json=directive,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Température {kelvin}K pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur température: {e}")
                return False

    def turn_on(self, entity_id: str, device_serial: Optional[str] = None) -> bool:
        """Allume lumière (accepte nom friendly ou entity_id)."""
        light_name = self._resolve_name(entity_id)
        if not light_name:
            logger.error(f"❌ Lumière introuvable: {entity_id}")
            return False
        logger.info(f"💡 Allumage '{light_name}' via commande vocale")
        return self._voice_service.turn_on_light(light_name, device_serial)

    def turn_off(self, entity_id: str, device_serial: Optional[str] = None) -> bool:
        """Éteint lumière (accepte nom friendly ou entity_id)."""
        light_name = self._resolve_name(entity_id)
        if not light_name:
            logger.error(f"❌ Lumière introuvable: {entity_id}")
            return False
        logger.info(f"🌑 Extinction '{light_name}' via commande vocale")
        return self._voice_service.turn_off_light(light_name, device_serial)

    def _power_control(self, entity_id: str, action: str) -> bool:
        """Contrôle l'alimentation."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                directive = {
                    "directive": {
                        "header": {
                            "namespace": "Alexa.PowerController",
                            "name": action,
                            "messageId": f"power-{entity_id}",
                            "payloadVersion": "3",
                        },
                        "endpoint": {"endpointId": entity_id},
                        "payload": {},
                    }
                }
                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/phoenix",
                    json=directive,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"{action} pour {entity_id}")
                return True
            except Exception as e:
                logger.error(f"Erreur {action}: {e}")
                return False

    def _resolve_name(self, name_or_id: str) -> Optional[str]:
        """Résout entity_id ou nom -> friendly name."""
        lights = self.get_all_lights()

        # 1. Si c'est déjà un nom friendly
        name_lower = name_or_id.lower().strip()
        for light in lights:
            friendly = light.get("friendlyName", "").lower().strip()
            if friendly == name_lower:
                return light.get("friendlyName")

        # 2. Si c'est un entity_id
        for light in lights:
            if light.get("entityId") == name_or_id:
                return light.get("friendlyName")

        return None

    def get_all_lights(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Récupère toutes les lumières connectées (avec cache)."""
        with self._lock:
            # Vérifier cache mémoire
            current_time = time.time()
            if (
                not force_refresh
                and self._lights_cache is not None
                and (current_time - self._cache_timestamp < self._cache_ttl)
            ):
                logger.debug("📦 Lumières depuis cache mémoire")
                return self._lights_cache

            # Refresh depuis cache smart_home_all ou API
            return self._refresh_lights_cache()

    def _refresh_lights_cache(self) -> List[Dict[str, Any]]:
        """Rafraîchit le cache des lumières depuis l'API."""
        if not self._check_connection():
            return []

        # D'abord essayer de récupérer depuis le cache smart_home_all
        # (synchronisé au login par SyncService)
        cached_all = self.cache_service.get("smart_home_all")
        if cached_all is not None:
            all_devices = cached_all.get("devices", [])
            logger.debug(f"📦 Utilisation cache smart_home_all ({len(all_devices)} devices)")
        else:
            # Fallback: appel API direct
            try:
                logger.debug("🌐 Récupération smart devices depuis API (fallback)")
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "Origin": f"https://alexa.{self.config.amazon_domain}",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", "")),
                    },
                    timeout=10,
                )
                response.raise_for_status()
                all_devices = response.json()
            except Exception as e:
                logger.error(f"Erreur récupération smart home: {e}")
                return []

        # Filtrer uniquement les lumières
        lights = []
        for device in all_devices:
            # Nouveau format API: providerData.categoryType ou deviceType
            provider_data = device.get("providerData", {})
            category_type = provider_data.get("categoryType", "").upper()
            device_type = provider_data.get("deviceType", "").upper()
            icon_value = device.get("icon", {}).get("value", "").upper()

            # Vérifier si c'est une lumière
            is_light = (
                category_type == "LIGHT"
                or device_type == "LIGHT"
                or icon_value == "LIGHT"
                or "LIGHT" in category_type
                or "LIGHT" in device_type
            )

            if is_light:
                lights.append(
                    {
                        "entityId": device.get("id"),
                        "friendlyName": device.get("displayName", "Unknown"),
                        "description": device.get("description", ""),
                        "categoryType": category_type,
                        "deviceType": device_type,
                        "supportedOperations": device.get("supportedOperations", []),
                        "supportedProperties": device.get("supportedProperties", []),
                        "availability": device.get("availability", "UNKNOWN"),
                    }
                )

        # Sauvegarder UNIQUEMENT dans cache mémoire
        # Le cache disque smart_home_all est géré par SyncService
        self._lights_cache = lights
        self._cache_timestamp = time.time()

        logger.info(f"🔄 {len(lights)} lumière(s) filtrée(s)")
        return lights

    def invalidate_lights_cache(self) -> None:
        """Invalide le cache mémoire des lumières."""
        with self._lock:
            self._lights_cache = None
            self._cache_timestamp = 0.0
            logger.info("🗑️ Cache lumières (mémoire) invalidé")

    def set_color_rgb(self, entity_id: str, rgb: Tuple[int, int, int]) -> bool:
        """
        Définit la couleur à partir de valeurs RGB.

        Args:
            entity_id: ID de l'entité lumière
            rgb: Tuple (R, G, B) avec valeurs 0-255

        Returns:
            True si succès, False sinon
        """
        r, g, b = rgb
        if not all(0 <= val <= 255 for val in [r, g, b]):
            logger.error(f"Valeurs RGB invalides: {rgb} (0-255)")
            return False

        # Conversion RGB → HSB
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        delta = max_val - min_val

        # Brightness
        brightness = max_val

        # Saturation
        saturation = 0 if max_val == 0 else delta / max_val

        # Hue
        hue: float = 0.0
        if delta == 0:
            hue = 0.0
        elif max_val == r_norm:
            hue = 60.0 * (((g_norm - b_norm) / delta) % 6)
        elif max_val == g_norm:
            hue = 60.0 * (((b_norm - r_norm) / delta) + 2)
        else:
            hue = 60.0 * (((r_norm - g_norm) / delta) + 4)

        logger.debug(f"RGB {rgb} → HSB ({hue:.1f}, {saturation:.2f}, {brightness:.2f})")
        return self.set_color(entity_id, hue, saturation, brightness)

    def set_color_name(self, entity_id: str, color_name: str) -> bool:
        """
        Définit la couleur à partir d'un nom prédéfini.

        Args:
            entity_id: ID de l'entité lumière
            color_name: Nom de couleur parmi: warm_white, cool_white, red, green, blue, yellow, purple, pink

        Returns:
            True si succès, False sinon
        """
        color_name_lower = color_name.lower()
        if color_name_lower not in COLOR_PRESETS:
            logger.error(f"Couleur inconnue: {color_name}. Disponibles: {', '.join(COLOR_PRESETS.keys())}")
            return False

        hue, saturation, brightness = COLOR_PRESETS[color_name_lower]
        logger.debug(f"Couleur '{color_name}' → HSB ({hue}, {saturation}, {brightness})")
        return self.set_color(entity_id, hue, saturation, brightness)

    def toggle(self, entity_id: str) -> bool:
        """
        Bascule l'état de la lumière (on ↔ off).

        Args:
            entity_id: ID de l'entité lumière

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False
            try:
                # Récupérer l'état actuel
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/phoenix/state",
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.config, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                devices = response.json().get("deviceStates", [])

                # Trouver l'appareil
                current_state = None
                for device in devices:
                    if device.get("entityId") == entity_id:
                        capabilities = device.get("capabilityStates", [])
                        for cap in capabilities:
                            if cap.get("namespace") == "Alexa.PowerController":
                                current_state = cap.get("value")
                                break
                        break

                if current_state is None:
                    logger.warning(f"État inconnu pour {entity_id}, allumage par défaut")
                    return self.turn_on(entity_id)

                # Basculer
                if current_state == "ON":
                    logger.debug("État actuel: ON → Extinction")
                    return self.turn_off(entity_id)
                else:
                    logger.debug("État actuel: OFF → Allumage")
                    return self.turn_on(entity_id)

            except Exception as e:
                logger.error(f"Erreur toggle: {e}")
                return False
