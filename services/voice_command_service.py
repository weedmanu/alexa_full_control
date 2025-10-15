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
    from core.circuit_breaker import CircuitBreaker  # type: ignore
    from core.state_machine import AlexaStateMachine  # type: ignore
else:
    CircuitBreaker = None
    AlexaStateMachine = None


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
            from core.circuit_breaker import CircuitBreaker as CB
            from core.state_machine import AlexaStateMachine as ASM

            self.state_machine = state_machine or ASM()
            self.breaker = CB(failure_threshold=3, timeout=30)
        except Exception:
            # If imports fail (import cycle), try to use names defined under TYPE_CHECKING
            # They may be None at runtime; guard their use accordingly.
            if state_machine is not None:
                self.state_machine = state_machine
            else:
                # Last resort: leave uninitialized (mypy will accept Any)
                self.state_machine = None

            try:
                self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)  # type: ignore[name-defined]
            except Exception:
                self.breaker = None

        self._lock: threading.RLock = threading.RLock()
        self._customer_id: Optional[str] = None

        logger.info(f"{SharedIcons.GEAR} VoiceCommandService initialisé")

    def speak(
        self, text: str, device_serial: Optional[str] = None, device_type: str = "ECHO"
    ) -> bool:
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
                    devices: List[Dict[str, Any]] = devices_data.get("devices", []) if isinstance(devices_data, dict) else []
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
                    logger.debug(
                        f"🔊 Device: {default_device['name']} (serial={dsn}, type={dtype})"
                    )

                # Construire le payload - FORMAT DEV EXACT
                sequence_json_content = cast(Dict[str, Any], {
                    "@type": "com.amazon.alexa.behaviors.model.Sequence",
                    "startNode": {
                        "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
                        "type": "Alexa.TextCommand",  # ← TextCommand pour EXÉCUTER
                        "skillId": "amzn1.ask.1p.tellalexa",  # ← ESSENTIEL !
                        "operationPayload": {
                            "deviceType": dtype,
                            "deviceSerialNumber": dsn,
                            "locale": "fr-FR",
                            "customerId": self._customer_id,
                            "text": text_clean,
                        },
                    },
                })

                # ← IMPORTANT : sequenceJson doit être une STRING (json.dumps) !
                payload = cast(Dict[str, Any], {
                    "behaviorId": "PREVIEW",
                    "sequenceJson": json.dumps(sequence_json_content),
                    "status": "ENABLED",
                })

                logger.debug(f"📤 Envoi commande vocale: '{text_clean}'")
                logger.debug(f"📦 Device: {dtype} / {dsn}")
                logger.debug("📋 Payload type: Alexa.TextCommand")
                logger.debug(f"📋 Payload text: '{text_clean}'")

                # Appel direct
                response = self.auth.session.post(
                    "https://alexa.amazon.fr/api/behaviors/preview",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": "https://alexa.amazon.fr/spa/index.html",
                        "Origin": "https://alexa.amazon.fr",
                        "csrf": getattr(self.auth, "csrf", ""),
                    },
                    json=payload,
                )

                response.raise_for_status()

                # Log de la réponse COMPLÈTE (si JSON)
                try:
                    response_data = response.json()
                    logger.debug(f"📥 Réponse API complète: status={getattr(response, 'status_code', 'unknown')}")
                    logger.debug(f"📥 Body: {json.dumps(response_data, indent=2)}")
                except Exception as e:
                    logger.debug(f"📥 Réponse API: status={getattr(response, 'status_code', 'unknown')}, no JSON body: {e}")

                logger.success(f"✅ Commande vocale envoyée: '{text_clean}'")
                return True

            except Exception as e:
                logger.error(f"❌ Erreur commande vocale: {e}")
                return False

    def speak_as_voice(
        self, text: str, device_serial: Optional[str] = None, device_type: str = "ECHO"
    ) -> bool:
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
                    logger.debug(
                        f"🔊 Device: {device_name} (serial={device_serial}, deviceType={dtype})"
                    )
                else:
                    default_device = self._get_default_echo_device()
                    if not default_device:
                        logger.error("❌ Aucun device Echo disponible")
                        return False
                    device_serial = default_device["serial"]
                    dtype = default_device["type"]
                    logger.debug(
                        f"🔊 Device: {default_device['name']} (serial={device_serial}, type={dtype})"
                    )

                # Construire le payload avec Alexa.Speak au lieu de TextCommand
                # Cela simule une VRAIE commande vocale (comme si on parlait au micro)
                sequence_json_content = {
                    "@type": "com.amazon.alexa.behaviors.model.Sequence",
                    "startNode": {
                        "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
                        "type": "Alexa.Speak",  # ← Alexa.Speak pour simuler la VOIX
                        "operationPayload": {
                            "deviceType": dtype,
                            "deviceSerialNumber": device_serial,
                            "locale": "fr-FR",
                            "customerId": self._customer_id,
                            "textToSpeak": f"Alexa, {text_clean}",  # ← Préfixer avec "Alexa,"
                        },
                    },
                }

                payload = {
                    "behaviorId": "PREVIEW",
                    "sequenceJson": json.dumps(sequence_json_content),
                    "status": "ENABLED",
                }

                logger.debug(f"📤 Envoi commande vocale simulée: 'Alexa, {text_clean}'")
                logger.debug(f"📦 Device: {dtype} / {device_serial}")

                response = self.auth.session.post(
                    "https://alexa.amazon.fr/api/behaviors/preview",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": "https://alexa.amazon.fr/spa/index.html",
                        "Origin": "https://alexa.amazon.fr",
                        "csrf": self.auth.csrf,
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

                logger.success(f"✅ Commande vocale simulée envoyée: 'Alexa, {text_clean}'")
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
            devices = (
                devices_data.get("devices", []) if isinstance(devices_data, dict) else devices_data
            )

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
                            "type": device.get(
                                "deviceType"
                            ),  # ← IMPORTANT: deviceType, PAS deviceFamily !
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
                self.auth.session.get,
                url,
                headers={"csrf": self.auth.csrf},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            customer_id = data.get("authentication", {}).get("customerId")
            if customer_id:
                logger.debug(f"✅ Customer ID: {customer_id}")
                return customer_id
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

    def set_brightness(
        self, light_name: str, brightness: int, device_serial: Optional[str] = None
    ) -> bool:
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

                from core.activity_manager import ActivityManager

                activity_mgr = ActivityManager(self.auth, self.config, self.state_machine)

                # Récupérer les activités depuis le timestamp d'envoi
                activities = activity_mgr.get_activities(limit=20, start_time=timestamp_before)

                if not activities:
                    logger.warning(
                        "⚠️ Aucune nouvelle activité trouvée après l'envoi de la commande"
                    )
                    logger.info("💡 Cela peut signifier que:")
                    logger.info("   - La commande n'a pas été exécutée par Alexa")
                    logger.info("   - Le délai d'attente est trop court")
                    logger.info("   - L'appareil Alexa n'est pas connecté")
                    return None

                logger.debug(f"📊 {len(activities)} nouvelle(s) activité(s) depuis l'envoi")

                # Chercher la réponse d'Alexa qui correspond à notre commande
                # Chercher des réponses qui semblent être des réponses à des questions sur les listes
                # et qui sont suffisamment récentes (moins de 30 secondes)
                import datetime as _datetime

                current_time = _datetime.datetime.now().timestamp() * 1000

                list_related_responses: List[Tuple[Dict[str, Any], str]] = []

                for idx, activity in enumerate(activities):
                    # Vérifier que c'est une interaction vocale avec réponse Alexa
                    if activity.get("type") == "voice":
                        alexa_response = activity.get("alexaResponse")
                        timestamp_str = activity.get("timestamp", "")

                        # Convertir le timestamp string en millisecondes
                        try:
                            if isinstance(timestamp_str, str) and timestamp_str:
                                # Le timestamp est au format ISO, le convertir en timestamp Unix
                                dt = _datetime.datetime.fromisoformat(
                                    timestamp_str.replace("Z", "+00:00")
                                )
                                timestamp = dt.timestamp() * 1000
                            else:
                                timestamp = float(timestamp_str) if timestamp_str else 0
                        except (ValueError, TypeError):
                            logger.debug(f"Impossible de convertir le timestamp: {timestamp_str}")
                            continue

                        # Vérifier que l'activité est récente (moins de 30 secondes)
                        if current_time - timestamp > 30000:  # 30 secondes en millisecondes
                            continue

                        customer_transcript = activity.get("utterance")
                        device_name = activity.get("deviceName", "N/A")

                        logger.info(f"\n🔍 Activité #{idx + 1} (depuis {timestamp_str}):")
                        logger.info(f"   Appareil: {device_name}")
                        logger.info(
                            f"   Votre commande: {customer_transcript if customer_transcript else '(TextCommand - non enregistré)'}"
                        )
                        logger.info(
                            f"   Réponse Alexa: {alexa_response[:150] if alexa_response else 'Aucune'}..."
                        )

                        # Collecter les réponses qui semblent liées aux listes
                        if alexa_response:
                            response_lower = alexa_response.lower()
                            # Mots-clés indiquant une réponse sur une liste
                            list_keywords = [
                                "liste",
                                "courses",
                                "achat",
                                "shopping",
                                "tâche",
                                "todo",
                                "faire",
                                "vide",
                                "rien",
                                "élément",
                                "article",
                                "pain",
                                "lait",
                                "œuf",
                                "farine",
                                "beurre",
                                "fromage",
                                "viande",
                                "légume",
                                "fruit",
                                "boisson",
                                "produit",
                                "marché",
                                "supermarché",
                            ]

                            # Si la réponse contient des mots-clés liés aux listes, la garder
                            if any(keyword in response_lower for keyword in list_keywords):
                                list_related_responses.append((activity, alexa_response))
                                logger.debug(
                                    "   📋 Réponse potentiellement liée à une liste détectée"
                                )

                # Si on a trouvé des réponses liées aux listes, prendre la plus récente
                if list_related_responses:
                    # Trier par timestamp (le plus récent en premier)
                    list_related_responses.sort(
                        key=lambda x: x[0].get("timestamp", ""), reverse=True
                    )
                    _, best_response = list_related_responses[0]
                    logger.success("✅ Réponse Alexa liée à une liste trouvée")
                    return best_response

                # Fallback: si on n'a pas de réponse liée aux listes, mais qu'on a des réponses récentes,
                # prendre la plus récente (elle pourrait être notre réponse même si elle ne contient pas de mots-clés)
                recent_responses: List[Dict[str, Any]] = []
                for activity in activities:
                    if activity.get("type") == "voice" and activity.get("alexaResponse"):
                        timestamp_str = activity.get("timestamp", "")
                        try:
                            if isinstance(timestamp_str, str) and timestamp_str:
                                dt = _datetime.datetime.fromisoformat(
                                    timestamp_str.replace("Z", "+00:00")
                                )
                                timestamp = dt.timestamp() * 1000
                            else:
                                timestamp = float(timestamp_str) if timestamp_str else 0
                        except (ValueError, TypeError):
                            continue

                        if current_time - timestamp <= 30000:  # 30 secondes
                            recent_responses.append(activity)

                if recent_responses:
                    # Trier par timestamp et prendre la plus récente
                    recent_responses.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                    best_recent = recent_responses[0]
                    logger.success(
                        "✅ Réponse Alexa récente trouvée (possible réponse à notre commande)"
                    )
                    return best_recent.get("alexaResponse")

                logger.warning(
                    f"⚠️ Aucune réponse récente trouvée dans les {len(activities)} activités"
                )
                return None

            except Exception as e:
                logger.exception(f"❌ Erreur lors de la récupération de la réponse: {e}")
                return None
