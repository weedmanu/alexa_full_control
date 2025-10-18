"""
Service de commandes vocales - Format dev exact.

Utilise /api/behaviors/preview avec type "Alexa.Speak" pour
simuler des commandes vocales comme "Alexa, allume buffet".
"""

import json
import threading

# Import retardé pour éviter cycle avec core.smart_home
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, cast

from loguru import logger

from utils.logger import SharedIcons

if TYPE_CHECKING:
    pass


class VoiceCommandService:
    """
    Service de commandes vocales - Architecture dev.

    Envoie des commandes textuelles qui sont interprétées comme
    des commandes vocales par Alexa (TTS + exécution).
    """

    def __init__(self, auth: Any, config: Any, state_machine: Optional[Any] = None):
        """
        Initialise le service.

        Args:
            auth: Service d'authentification
            config: Configuration
            state_machine: Machine à états (optionnel)
        """
        self.auth = auth
        self.config = config

        # Import au runtime pour éviter cycles
        # Best-effort typing: initialize attributes as Any so mypy can track assignments
        self.state_machine: Any
        self.breaker: Any

        # Try runtime imports to avoid import cycles; fall back to TYPE_CHECKING names
        try:
            from core.circuit_breaker import CircuitBreaker
            from core.state_machine import AlexaStateMachine

            # Use lowercase local names for runtime creation while keeping
            # the imported names CamelCase to satisfy linters.
            cb = CircuitBreaker
            asm = AlexaStateMachine

            self.state_machine = state_machine or asm()
            self.breaker = cb(failure_threshold=3, timeout=30)
        except Exception:
            # If imports fail (import cycle), try to use names defined under TYPE_CHECKING
            # They may be None at runtime; guard their use accordingly.
            if state_machine is not None:
                self.state_machine = state_machine
            else:
                # Last resort: leave uninitialized (mypy will accept Any)
                self.state_machine = None

            try:
                from core.circuit_breaker import CircuitBreaker

                self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
            except Exception:
                self.breaker = None

        self._lock: threading.RLock = threading.RLock()
        self._customer_id: Optional[str] = None

        # Compatibilité legacy: exposer un http_client minimal via BaseManager wrapper
        try:
            from core.base_manager import create_http_client_from_auth

            # Normalize http client: wrap legacy auth.session or accept modern http client
            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            # Fallback conservative: keep existing auth object as http client
            self.http_client = self.auth

        logger.info(f"{SharedIcons.GEAR} VoiceCommandService initialisé")

    def speak(
        self, text: str, device_serial: Optional[str] = None, device_type: str = "ECHO"
    ) -> bool:  # pylint: disable=unused-argument
        """
        Fait parler Alexa et exécute la commande vocale.

        Args:
            text: Texte à dire (ex: "Alexa, allume buffet")
            device_serial: Serial du device (si None, utilise ALEXA_CURRENT_DSN)
            device_type: Type de device (défaut: ECHO)

        Returns:
            True si succès, False sinon

        Exemples:
            >>> service.speak("Alexa, allume buffet")
            >>> service.speak("allume buffet", "G090LF11480501CV")
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                logger.warning("❌ État système ne permet pas l'exécution")
                return False

            try:
                # ← NE PAS préfixer avec "Alexa," pour TextCommand !
                # TextCommand envoie directement la commande, pas besoin du wake word
                text_clean = text.strip("\"'")
                if text_clean.lower().startswith("alexa"):
                    # Retirer "Alexa," si présent
                    text_clean = text_clean[6:].strip(",").strip()

                logger.debug(f"📝 Commande nettoyée: '{text_clean}'")

                # Récupérer customer_id si nécessaire
                if not self._customer_id:
                    self._customer_id = self._get_customer_id()
                    if not self._customer_id:
                        logger.error("❌ Customer ID non disponible")
                        return False

                # Device serial et type
                if device_serial:
                    # Récupérer le deviceType depuis le cache pour ce serial
                    dsn = device_serial
                    from services.cache_service import CacheService

                    cache = CacheService()
                    devices_data = cache.get("devices") or {}
                    devices = devices_data.get("devices", []) if isinstance(devices_data, dict) else []
                    dtype = None
                    device_name = None
                    for dev in devices:
                        if dev.get("serialNumber") == device_serial:
                            # IMPORTANT: utiliser deviceType (ex: A2UONLFQW0PADH) PAS deviceFamily !
                            dtype = dev.get("deviceType")
                            device_name = dev.get("accountName")
                            break
                    if not dtype:
                        logger.error(f"❌ Device {device_serial} introuvable dans le cache")
                        return False
                    logger.debug(f"🔊 Device: {device_name} (serial={dsn}, deviceType={dtype})")
                else:
                    # Récupérer un device Echo par défaut
                    default_device = self._get_default_echo_device()
                    if not default_device:
                        logger.error("❌ Aucun device Echo disponible")
                        return False
                    dsn = default_device["serial"]
                    dtype = default_device["type"]
                    logger.debug(f"🔊 Device: {default_device['name']} (serial={dsn}, type={dtype})")

                # Construire le payload - FORMAT DEV EXACT
                _sequence_json_content = {
                    "@type": "com.amazon.alexa.behaviors.model.Sequence",
                    "startNode": {
                        "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
                        "type": "Alexa.TextCommand",
                        "skillId": "amzn1.ask.1p.tellalexa",
                        "operationPayload": {
                            "deviceType": dtype,
                            "deviceSerialNumber": dsn,
                            "locale": "fr-FR",
                            "customerId": self._customer_id,
                            "text": text_clean,
                        },
                    },
                }

                # sequenceJson doit être une STRING (json.dumps)
                payload = {
                    "behaviorId": "PREVIEW",
                    "sequenceJson": json.dumps(_sequence_json_content),
                    "status": "ENABLED",
                }

                logger.debug(f"📤 Envoi commande vocale: '{text_clean}'")
                logger.debug(f"📦 Device: {dtype} / {dsn}")
                logger.debug("📋 Payload type: Alexa.TextCommand")
                logger.debug(f"📋 Payload text: '{text_clean}'")

                # Appel direct
                response = self.http_client.post(
                    "https://alexa.amazon.fr/api/behaviors/preview",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": "https://alexa.amazon.fr/spa/index.html",
                        "Origin": "https://alexa.amazon.fr",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    json=payload,
                )

                response.raise_for_status()

                # Log de la réponse COMPLÈTE (si JSON)
                try:
                    response_data = response.json()
                    status_val = getattr(response, "status_code", "unknown")
                    body_str = json.dumps(response_data, indent=2)
                    logger.debug(f"📥 Réponse API complète: status={status_val}")
                    logger.debug(f"📥 Body: {body_str}")
                except Exception as e:
                    status_val = getattr(response, "status_code", "unknown")
                    err_str = str(e)
                    logger.debug(f"📥 Réponse API: status={status_val}, no JSON body: {err_str}")

                logger.success(f"✅ Commande vocale envoyée: '{text_clean}'")
                return True

            except Exception as e:
                logger.error(f"❌ Erreur commande vocale: {e}")
                return False

    def speak_as_voice(
        self, text: str, device_serial: Optional[str] = None, device_type: str = "ECHO"
    ) -> bool:  # pylint: disable=unused-argument
        """
        Simule une commande vocale avec Alexa.Speak (comme si on parlait au micro).

        Différence avec speak():
        - speak() utilise TextCommand (traité comme texte)
        - speak_as_voice() utilise Alexa.Speak (traité comme voix)

        Args:
            text: Commande vocale (ex: "donne-moi la liste des choses à faire")
            device_serial: Serial du device (si None, utilise ALEXA_CURRENT_DSN)
            device_type: Type de device (défaut: ECHO)

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                logger.warning("❌ État système ne permet pas l'exécution")
                return False

            try:
                text_clean = text.strip("\"'")
                if text_clean.lower().startswith("alexa"):
                    text_clean = text_clean[6:].strip(",").strip()

                logger.debug(f"📝 Commande vocale simulée: '{text_clean}'")

                # Récupérer customer_id si nécessaire
                if not self._customer_id:
                    self._customer_id = self._get_customer_id()
                    if not self._customer_id:
                        logger.error("❌ Customer ID non disponible")
                        return False

                # Device serial et type
                if device_serial:
                    from services.cache_service import CacheService

                    cache = CacheService()
                    devices_data = cache.get("devices") or {}
                    devices = devices_data.get("devices", [])
                    dtype = None
                    device_name = None
                    for dev in devices:
                        if dev.get("serialNumber") == device_serial:
                            dtype = dev.get("deviceType")
                            device_name = dev.get("accountName")
                            break
                    if not dtype:
                        logger.error(f"❌ Device {device_serial} introuvable dans le cache")
                        return False
                    logger.debug(f"🔊 Device: {device_name} (serial={device_serial}, deviceType={dtype})")
                else:
                    default_device = self._get_default_echo_device()
                    if not default_device:
                        logger.error("❌ Aucun device Echo disponible")
                        return False
                    device_serial = default_device["serial"]
                    dtype = default_device["type"]
                    logger.debug(f"🔊 Device: {default_device['name']} (serial={device_serial}, type={dtype})")

                # Construire le payload avec Alexa.Speak au lieu de TextCommand
                # Cela simule une VRAIE commande vocale (comme si on parlait au micro)
                _sequence_json_content = {
                    "@type": "com.amazon.alexa.behaviors.model.Sequence",
                    "startNode": {
                        "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
                        "type": "Alexa.Speak",
                        "operationPayload": {
                            "deviceType": dtype,
                            "deviceSerialNumber": device_serial,
                            "locale": "fr-FR",
                            "customerId": self._customer_id,
                            "textToSpeak": text_clean,
                        },
                    },
                }

                payload = {
                    "behaviorId": "PREVIEW",
                    "sequenceJson": json.dumps(_sequence_json_content),
                    "status": "ENABLED",
                }

                logger.debug(f"📤 Envoi commande vocale simulée: '{text_clean}'")
                logger.debug(f"📦 Device: {dtype} / {device_serial}")

                response = self.http_client.post(
                    "https://alexa.amazon.fr/api/behaviors/preview",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": "https://alexa.amazon.fr/spa/index.html",
                        "Origin": "https://alexa.amazon.fr",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    json=payload,
                )

                response.raise_for_status()

                try:
                    response_data = response.json() if hasattr(response, "json") else {}
                    logger.debug(f"📥 Réponse API: status={response.status_code}")
                    logger.debug(f"📥 Body: {json.dumps(response_data, indent=2)}")
                except Exception as e:
                    logger.debug(f"📥 Réponse API: status={response.status_code}, no JSON body: {e}")

                logger.success(f"✅ Commande vocale simulée envoyée: '{text_clean}'")
                return True

            except Exception as e:
                logger.error(f"❌ Erreur commande vocale simulée: {e}")
                return False

    def _get_default_echo_device(self) -> Optional[Dict[str, Any]]:
        """
        Récupère un device Echo par défaut pour exécuter les commandes vocales.

        Returns:
            Dict avec {name, serial, type} ou None si aucun device disponible
        """
        try:
            # Récupérer la liste des devices depuis le cache
            from services.cache_service import CacheService

            cache = CacheService()
            devices_data = cache.get("devices")

            if not devices_data:
                logger.warning("⚠️ Aucun device en cache")
                return None

            # ← FIX: devices_data contient déjà {"devices": [...]}
            devices = devices_data.get("devices", []) if isinstance(devices_data, dict) else devices_data

            # Chercher un Echo (priorité: Salon Echo, sinon premier Echo disponible)
            echo_devices: List[Dict[str, Any]] = []
            for device in devices:
                device_family = device.get("deviceFamily", "")
                # KNIGHT, ROOK, etc. sont des familles Echo
                if device_family in ["KNIGHT", "ROOK", "VOX", "ECHO"]:
                    echo_devices.append(
                        {
                            "name": device.get("accountName", "Unknown"),
                            "serial": device.get("serialNumber", ""),
                            "type": device.get("deviceType"),  # ← IMPORTANT: deviceType, PAS deviceFamily !
                        }
                    )

            if not echo_devices:
                logger.error("❌ Aucun device Echo trouvé")
                return None

            # Priorité: "Salon Echo"
            for echo in echo_devices:
                if "salon" in echo["name"].lower():
                    return echo

            # Sinon, premier Echo disponible
            return echo_devices[0]

        except Exception as e:
            logger.error(f"❌ Erreur récupération device Echo: {e}")
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
                self.http_client.get,
                url,
                headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            customer_id = data.get("authentication", {}).get("customerId")
            if customer_id:
                logger.debug(f"✅ Customer ID: {customer_id}")
                return cast(str | None, customer_id)
            else:
                logger.warning("⚠️ Customer ID non trouvé dans bootstrap")
                return None

        except Exception as e:
            logger.error(f"❌ Erreur récupération customer ID: {e}")
            return None

    def turn_on_light(self, light_name: str, device_serial: Optional[str] = None) -> bool:
        """
        Allume une lumière.

        Args:
            light_name: Nom de la lumière (ex: "buffet", "salon")
            device_serial: Serial du device Alexa (optionnel)

        Returns:
            True si succès
        """
        return self.speak(f"allume {light_name}", device_serial)

    def turn_off_light(self, light_name: str, device_serial: Optional[str] = None) -> bool:
        """
        Éteint une lumière.

        Args:
            light_name: Nom de la lumière
            device_serial: Serial du device Alexa (optionnel)

        Returns:
            True si succès
        """
        return self.speak(f"éteins {light_name}", device_serial)

    def set_brightness(self, light_name: str, brightness: int, device_serial: Optional[str] = None) -> bool:
        """
        Définit la luminosité.

        Args:
            light_name: Nom de la lumière
            brightness: Luminosité 0-100
            device_serial: Serial du device Alexa (optionnel)

        Returns:
            True si succès
        """
        if not 0 <= brightness <= 100:
            logger.error(f"❌ Luminosité invalide: {brightness} (0-100)")
            return False
        return self.speak(f"mets {light_name} à {brightness} pourcent", device_serial)

    def set_color(self, light_name: str, color: str, device_serial: Optional[str] = None) -> bool:
        """
        Définit la couleur.

        Args:
            light_name: Nom de la lumière
            color: Nom de couleur (rouge, bleu, vert, etc.)
            device_serial: Serial du device Alexa (optionnel)

        Returns:
            True si succès
        """
        return self.speak(f"mets {light_name} en {color}", device_serial)

    def ask_and_get_response(
        self, question: str, device_serial: Optional[str] = None, wait_seconds: float = 2.0
    ) -> Optional[str]:
        """
        Pose une question vocale à Alexa et récupère la réponse.

        Utilise TextCommand pour poser la question, puis récupère
        la réponse d'Alexa via l'API Privacy (historique vocal).

        Args:
            question: Question à poser (ex: "lis ma liste de courses")
            device_serial: Serial du device (optionnel)
            wait_seconds: Temps d'attente avant de récupérer la réponse (défaut: 2s)

        Returns:
            Réponse vocale d'Alexa ou None si échec

        Exemples:
            >>> response = service.ask_and_get_response("lis ma liste de courses")
            >>> print(response)  # "Voici votre liste de courses : lait, pain, ..."
        """
        import time

        with self._lock:
            if not self.state_machine.can_execute_commands:
                logger.warning("❌ État système ne permet pas l'exécution")
                return None

            try:
                # 1. Enregistrer le timestamp avant l'envoi
                import datetime as _datetime

                timestamp_before = _datetime.datetime.now()

                # 2. Envoyer la commande vocale
                logger.info(f"📤 Envoi commande à Alexa: '{question}'")
                success = self.speak(question, device_serial)

                if not success:
                    logger.error("❌ Échec de l'envoi de la commande")
                    return None

                logger.success("✅ Commande envoyée avec succès")

                # 3. Attendre que Alexa traite et réponde
                logger.info(f"⏳ Attente de {wait_seconds}s pour que Alexa réponde...")
                for i in range(int(wait_seconds)):
                    time.sleep(1)
                    logger.debug(f"   {i + 1}/{int(wait_seconds)}s...")

                # Attendre le reste (décimales)
                remaining = wait_seconds - int(wait_seconds)
                if remaining > 0:
                    time.sleep(remaining)

                # 4. Récupérer la dernière réponse via l'API Privacy
                logger.info("🔍 Récupération de la réponse d'Alexa...")

                # ActivityManager removed - simplified response retrieval
                logger.warning("⚠️ ActivityManager supprimé - récupération de réponse simplifiée")
                return None

            except Exception as e:
                logger.exception(f"❌ Erreur lors de la récupération de la réponse: {e}")
                return None

    def play_sound(self, device_name: str, sound_id: str) -> bool:
        """
        Joue un son d'effet sur l'appareil.

        Args:
            device_name: Nom de l'appareil
            sound_id: ID du son (ex: amzn1.ask.skillId.airhorn)

        Returns:
            True si le son a été joué, False sinon
        """
        with self._lock:
            try:
                logger.debug(f"🔊 Jouant son {sound_id} sur {device_name}")

                # Récupérer customer_id
                if not self._customer_id:
                    self._customer_id = self._get_customer_id()
                    if not self._customer_id:
                        logger.error("❌ Customer ID non disponible")
                        return False

                # Récupérer le device depuis le cache
                from services.cache_service import CacheService

                cache = CacheService()
                devices_data = cache.get("devices") or {}
                devices = devices_data.get("devices", [])

                device_serial = None
                device_type = None
                for dev in devices:
                    if dev.get("accountName") == device_name:
                        device_serial = dev.get("serialNumber")
                        device_type = dev.get("deviceType")
                        break

                if not device_serial or not device_type:
                    logger.error(f"❌ Appareil '{device_name}' non trouvé")
                    return False

                logger.debug(f"🔊 Device trouvé: {device_name} (serial={device_serial})")

                return self.speak_as_voice(f"Sound: {sound_id}", device_serial, device_type)

            except Exception as e:
                logger.exception(f"❌ Erreur lors de la lecture du son: {e}")
                return False

    def execute_text_command(self, device_name: str, text: str) -> bool:
        """
        Exécute une commande texte (comme si elle était vocale).

        Args:
            device_name: Nom de l'appareil
            text: Commande texte à exécuter (ex: 'allume les lumières')

        Returns:
            True si la commande a été exécutée, False sinon
        """
        with self._lock:
            try:
                logger.debug(f"📝 Exécutant commande texte: '{text}' sur {device_name}")

                # Récupérer customer_id
                if not self._customer_id:
                    self._customer_id = self._get_customer_id()
                    if not self._customer_id:
                        logger.error("❌ Customer ID non disponible")
                        return False

                # Récupérer le device depuis le cache
                from services.cache_service import CacheService

                cache = CacheService()
                devices_data = cache.get("devices") or {}
                devices = devices_data.get("devices", [])

                device_serial = None
                device_type = None
                for dev in devices:
                    if dev.get("accountName") == device_name:
                        device_serial = dev.get("serialNumber")
                        device_type = dev.get("deviceType")
                        break

                if not device_serial or not device_type:
                    logger.error(f"❌ Appareil '{device_name}' non trouvé")
                    return False

                logger.debug(f"📝 Device trouvé: {device_name} (serial={device_serial})")

                # Construire le payload pour exécuter la commande texte
                sequence_json_content = {
                    "@type": "com.amazon.alexa.behaviors.model.Sequence",
                    "startNode": {
                        "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
                        "type": "Alexa.TextCommand",
                        "operationPayload": {
                            "deviceType": device_type,
                            "deviceSerialNumber": device_serial,
                            "locale": "fr-FR",
                            "customerId": self._customer_id,
                            "text": text,
                            "skillId": "amzn1.ask.1p.tellalexa",
                        },
                    },
                }

                payload = {
                    "behaviorId": "PREVIEW",
                    "sequenceJson": sequence_json_content,
                    "status": "ENABLED",
                }

                # Envoyer la commande
                result = self.auth.post_api(
                    "/api/behaviors/preview",
                    json=payload,
                    headers={"Origin": "https://alexa.amazon.fr"},
                )

                if result and result.status_code == 200:
                    logger.success(f"✅ Commande texte exécutée: '{text}'")
                    return True
                else:
                    logger.error(f"❌ Erreur lors de l'exécution: {result.status_code if result else 'No response'}")
                    return False

            except Exception as e:
                logger.exception(f"❌ Erreur lors de l'exécution du textcommand: {e}")
                return False
