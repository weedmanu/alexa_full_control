"""
Gestionnaire d'activités et historique vocal Alexa - Thread-safe.
"""

import re
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.base import ResponseDTO  # noqa: F401

    HAS_ACTIVITY_DTO = True
except ImportError:
    HAS_ACTIVITY_DTO = False


class ActivityManager:
    """Gestionnaire thread-safe de l'historique d'activités."""

    def __init__(self, auth: Any, config: Any, state_machine: Optional[AlexaStateMachine] = None) -> None:
        self.auth = auth
        self.config = config
        self.state_machine: AlexaStateMachine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth
        logger.info("ActivityManager initialisé")

    def get_customer_history_records(self, limit: int = 50, start_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Récupère l'historique vocal complet via l'API Privacy ou cache local.

        Args:
            limit: Nombre maximum d'enregistrements à récupérer
            start_time: Timestamp de début (optionnel)

        Returns:
            Liste des enregistrements de l'historique vocal
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []

            # Essayer d'abord l'API Privacy
            try:
                privacy_csrf = self.get_privacy_csrf()
                if privacy_csrf:
                    records = self._fetch_privacy_api_records(limit, start_time, privacy_csrf)
                    if records:
                        # Sauvegarder dans le cache local pour usage futur
                        self._save_activities_to_cache(records)
                        return records
            except Exception as e:
                logger.debug(f"API Privacy indisponible: {e}")

            # Fallback: utiliser le cache local
            logger.info("🔄 Utilisation du cache local d'activités")
            return self._get_activities_from_cache(limit, start_time)

    def _fetch_privacy_api_records(
        self, limit: int, start_time: Optional[int], privacy_csrf: str
    ) -> List[Dict[str, Any]]:
        """Récupère les enregistrements via l'API Privacy Amazon."""
        # Préparer les paramètres de l'API
        end_time = int(datetime.now().timestamp() * 1000)  # Maintenant
        start_time_param = start_time if start_time else 0  # Depuis le début ou timestamp fourni

        # URL de l'API Privacy
        privacy_url = f"https://www.{self.config.amazon_domain}/alexa-privacy/apd/rvh/customer-history-records-v2/"
        params = {"startTime": start_time_param, "endTime": end_time, "pageType": "VOICE_HISTORY"}

        logger.debug(f"Appel API Privacy: {privacy_url} avec startTime={start_time_param}")

        # Headers requis pour l'API Privacy
        headers = {
            "csrf": self.auth.csrf or "",
            "anti-csrftoken-a2z": privacy_csrf,
            "Content-Type": "application/json",
        }

        # Body de la requête
        body = {"previousRequestToken": None}  # Pour pagination (None = première page)

        # Appel à l'API Privacy avec le Circuit Breaker
        response = self.breaker.call(
            self.http_client.post,
            privacy_url,
            params=params,
            headers={**headers, "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
            json=body,
            timeout=15,
        )

        response.raise_for_status()
        data = cast(Dict[str, Any], response.json())

        # Extraire les enregistrements
        records = data.get("customerHistoryRecords", [])
        logger.debug(f"✅ Récupéré {len(records)} enregistrements de l'historique vocal")

        # Limiter le nombre de résultats si demandé
        if limit and len(records) > limit:
            records = records[:limit]

        return cast(list[dict[str, Any]], records)

    def _save_activities_to_cache(self, records: List[Dict[str, Any]]) -> None:
        """Sauvegarde les activités dans le cache local."""
        try:
            # Utiliser le cache service pour persister les données
            cache_key = "activities"
            cache_data = {
                "records": records,
                "last_updated": datetime.now().isoformat(),
                "source": "privacy_api",
            }

            # Sauvegarder avec TTL de 24h (puisque c'est de l'historique)
            # Nous n'avons pas accès direct au cache_service ici, utilisons une approche simple
            self._save_to_local_cache(cache_key, cache_data)

        except Exception as e:
            logger.debug(f"Erreur sauvegarde cache activités: {e}")

    # Note: the real file-based implementation of _save_to_local_cache is defined later in this file.

    def _get_activities_from_cache(self, limit: int, start_time: Optional[int]) -> List[Dict[str, Any]]:
        """Récupère les activités depuis le cache local."""
        try:
            cache_data = self._load_from_local_cache("activities")
            if not cache_data or "records" not in cache_data:
                logger.debug("Aucune donnée d'activité en cache local")
                return self._get_mock_activities(limit)

            records = cache_data["records"]

            # Filtrer par start_time si fourni
            if start_time:
                start_timestamp = start_time / 1000  # Convertir en secondes
                records = [r for r in records if r.get("timestamp", 0) >= start_timestamp]

            # Limiter le nombre de résultats
            if limit and len(records) > limit:
                records = records[:limit]

            logger.debug(f"✅ Récupéré {len(records)} activités depuis le cache local")
            return cast(list[dict[str, Any]], records)

        except Exception as e:
            logger.debug(f"Erreur lecture cache activités: {e}")
            return self._get_mock_activities(limit)

    def _get_mock_activities(self, limit: int) -> List[Dict[str, Any]]:
        """Retourne des données d'activité simulées pour le développement."""
        logger.info("🎭 Génération d'activités simulées pour démonstration")

        mock_activities = [
            {
                "recordKey": "mock-001",
                "timestamp": int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000),
                "device": {
                    "deviceName": "Salon Echo",
                    "serialNumber": "MOCKSERIAL001",
                    "deviceType": "A2UONLFQW0PADH",
                },
                "voiceHistoryRecordItems": [
                    {
                        "recordItemType": "CUSTOMER_TRANSCRIPT",
                        "transcriptText": "Alexa, quelle heure est-il ?",
                    },
                    {"recordItemType": "ALEXA_RESPONSE", "transcriptText": "Il est 17 heures 30"},
                ],
                "activityStatus": "SUCCESS",
            },
            {
                "recordKey": "mock-002",
                "timestamp": int((datetime.now() - timedelta(minutes=15)).timestamp() * 1000),
                "device": {
                    "deviceName": "Cuisine Echo Dot",
                    "serialNumber": "MOCKSERIAL002",
                    "deviceType": "A2UONLFQW0PADH",
                },
                "voiceHistoryRecordItems": [
                    {
                        "recordItemType": "CUSTOMER_TRANSCRIPT",
                        "transcriptText": "Alexa, joue de la musique",
                    },
                    {
                        "recordItemType": "ALEXA_RESPONSE",
                        "transcriptText": "Je lance votre playlist préférée",
                    },
                ],
                "activityStatus": "SUCCESS",
            },
            {
                "recordKey": "mock-003",
                "timestamp": int((datetime.now() - timedelta(hours=1)).timestamp() * 1000),
                "device": {
                    "deviceName": "Chambre Echo Show",
                    "serialNumber": "MOCKSERIAL003",
                    "deviceType": "A2UONLFQW0PADH",
                },
                "voiceHistoryRecordItems": [
                    {
                        "recordItemType": "CUSTOMER_TRANSCRIPT",
                        "transcriptText": "Alexa, règle un timer de 10 minutes",
                    },
                    {
                        "recordItemType": "ALEXA_RESPONSE",
                        "transcriptText": "Timer de 10 minutes programmé",
                    },
                ],
                "activityStatus": "SUCCESS",
            },
        ]

        # Limiter selon la demande
        if limit and len(mock_activities) > limit:
            mock_activities = mock_activities[:limit]

        return mock_activities

    def _save_to_local_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Sauvegarde des données dans un cache local simple."""
        try:
            import json
            from pathlib import Path

            cache_dir = Path("data/cache")
            cache_dir.mkdir(parents=True, exist_ok=True)

            cache_file = cache_dir / f"{key}_local.json"
            cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.debug(f"💾 Données sauvegardées dans cache local: {key}")

        except Exception as e:
            logger.debug(f"Erreur sauvegarde cache local {key}: {e}")

    def _load_from_local_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Charge des données depuis le cache local."""
        try:
            import json
            from pathlib import Path

            cache_file = Path("data/cache") / f"{key}_local.json"
            if cache_file.exists():
                return cast(Dict[str, Any], json.loads(cache_file.read_text(encoding="utf-8")))
        except Exception as e:
            logger.debug(f"Erreur lecture cache local {key}: {e}")
        return None

    def get_privacy_csrf(self) -> Optional[str]:
        """
        Récupère le token CSRF pour l'API Privacy.

        L'API Privacy nécessite un token CSRF spécifique qui peut être différent
        de celui utilisé pour l'API Alexa normale.

        Returns:
            Token CSRF pour l'API Privacy ou None si non disponible
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None

            # Essayer d'abord d'utiliser le token CSRF standard des cookies
            # L'API Privacy pourrait accepter le même token que les autres APIs
            if self.auth.csrf:
                logger.debug(f"Utilisation du token CSRF standard des cookies: {self.auth.csrf[:20]}...")
                return cast(str | None, self.auth.csrf)

            # Fallback: essayer d'extraire depuis la page HTML (peut ne plus fonctionner)
            try:
                # Faire une requête à la page Privacy pour obtenir le token CSRF correct
                # D'après la documentation, il faut accéder à /alexa-privacy/apd/activity
                privacy_url = f"https://www.{self.config.amazon_domain}/alexa-privacy/apd/activity?ref=activityHistory"

                logger.debug("Tentative d'extraction du token CSRF depuis la page HTML...")

                response = self.breaker.call(
                    self.http_client.get,
                    privacy_url,
                    timeout=10,
                )
                response.raise_for_status()

                # Extraire le token CSRF de la réponse HTML
                html_content = response.text
                csrf_token = self._extract_csrf_from_html(html_content)

                if csrf_token:
                    logger.debug(f"✅ Token CSRF Privacy trouvé dans HTML: {csrf_token[:20]}...")
                    return csrf_token
                else:
                    logger.warning("Token CSRF Privacy non trouvé dans la réponse HTML")

            except Exception as e:
                logger.error(f"Erreur récupération token CSRF Privacy depuis HTML: {e}")

            logger.error("❌ Aucun token CSRF disponible pour l'API Privacy")
            return None

    def _extract_csrf_from_html(self, html_content: str) -> Optional[str]:
        """
        Extrait le token CSRF de la réponse HTML de la page Privacy.

        Args:
            html_content: Contenu HTML de la page

        Returns:
            Token CSRF ou None si non trouvé
        """

        # Chercher le token CSRF dans les meta tags ou les inputs hidden
        patterns = [
            r'name="csrf"[^>]*value="([^"]+)"',
            r'<meta[^>]*name="csrf"[^>]*content="([^"]+)"',
            # Support key without quotes: csrf: 'token'
            r'csrf\s*:\s*["\']([^"\']+)["\']',
            # Privacy specific token, support unquoted key as well
            r'anti-csrftoken-a2z\s*:\s*["\']([^"\']+)["\']',
            # Support quoted key forms: 'anti-csrftoken-a2z': 'token'
            r'["\']anti-csrftoken-a2z["\']\s*:\s*["\']([^"\']+)["\']',
            r'csrf["\']\s*:\s*["\']([^"\']+)["\']',
            r'csrfToken\s*:\s*["\']([^"\']+)["\']',
            r'_csrf\s*:\s*["\']([^"\']+)["\']',
        ]

        logger.debug(f"Recherche du token CSRF dans {len(html_content)} caractères de HTML")

        # Log des premiers 2000 caractères pour déboguer
        logger.debug(f"Début du HTML: {html_content[:2000]}...")

        for pattern in patterns:
            logger.debug(f"Testing pattern: {pattern}")
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                csrf_token = match.group(1)
                logger.debug(f"Token CSRF trouvé avec pattern: {pattern}")
                logger.debug(f"Token CSRF: {csrf_token[:20]}...")
                return csrf_token

        # Chercher tous les tokens CSRF possibles
        all_csrf_patterns = [
            r'csrf[^"]*"([^"]*)"',
            r'anti-csrftoken[^"]*"([^"]*)"',
            r'csrf-token[^"]*"([^"]*)"',
            r'_csrf[^"]*"([^"]*)"',
        ]

        logger.debug("Recherche étendue de tous les tokens CSRF...")
        for pattern in all_csrf_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                logger.debug(f"Pattern {pattern} trouvé {len(matches)} matches: {matches[:3]}")

        logger.debug("Aucun token CSRF trouvé dans le HTML")
        return None

    def get_activities(self, limit: int = 50, start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des activités via l'API Privacy.

        Cette méthode utilise maintenant l'API Privacy au lieu de l'ancienne
        API /api/activities qui est dépréciée et retourne toujours vide.

        Args:
            limit: Nombre maximum d'activités à récupérer
            start_time: Timestamp de début (optionnel)

        Returns:
            Liste des activités formatées
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []

            try:
                # Convertir start_time en timestamp Unix si fourni
                start_timestamp = None
                if start_time:
                    start_timestamp = int(start_time.timestamp() * 1000)

                # Récupérer les enregistrements via l'API Privacy
                records = self.get_customer_history_records(limit, start_timestamp)

                if not records:
                    return []

                # Convertir les enregistrements Privacy au format d'activité standard
                activities = []
                for record in records:
                    activity = self._convert_privacy_record_to_activity(record)
                    if activity:
                        activities.append(activity)

                logger.debug(f"{len(activities)} activités converties")
                return activities

            except Exception as e:
                logger.error(f"Erreur récupération activités: {e}")
                return []

    def _convert_privacy_record_to_activity(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convertit un enregistrement Privacy au format d'activité standard.

        Args:
            record: Enregistrement de l'API Privacy

        Returns:
            Activité formatée ou None si conversion impossible
        """
        try:
            # Extraire les informations de base
            record_key = record.get("recordKey", "")
            timestamp = record.get("timestamp", 0)
            device = record.get("device", {})
            voice_items = record.get("voiceHistoryRecordItems", [])

            # Créer l'activité de base
            activity = {
                "id": record_key,
                "timestamp": datetime.fromtimestamp(timestamp / 1000).isoformat() if timestamp else None,
                "deviceSerialNumber": device.get("serialNumber"),
                "deviceName": device.get("deviceName"),
                "activityStatus": record.get("activityStatus", "UNKNOWN"),
                "source": "privacy_api",
            }

            # Enrichir avec les informations du cache des appareils si disponible
            if activity.get("deviceSerialNumber"):
                device_info = self._get_device_info_from_cache(activity["deviceSerialNumber"])
                if device_info:
                    activity["deviceName"] = device_info.get("accountName", activity.get("deviceName", "N/A"))

            # Déterminer le type d'activité et enrichir les données
            if voice_items:
                # C'est une interaction vocale
                customer_transcript = None
                alexa_response = None

                for item in voice_items:
                    item_type = item.get("recordItemType")
                    transcript = item.get("transcriptText", "")

                    if item_type == "CUSTOMER_TRANSCRIPT":
                        customer_transcript = transcript
                    elif item_type == "ALEXA_RESPONSE":
                        alexa_response = transcript

                activity.update(
                    {
                        "type": "voice",
                        "utterance": customer_transcript,
                        "alexaResponse": alexa_response,
                        "description": customer_transcript or "Interaction vocale",
                    }
                )
            else:
                # Autre type d'activité (musique, alarme, etc.)
                activity.update({"type": "system", "description": "Activité système"})

            return activity

        except Exception as e:
            logger.warning(f"Erreur conversion enregistrement Privacy: {e}")
            return None

    def _get_device_info_from_cache(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un appareil depuis le cache.

        Args:
            serial_number: Numéro de série de l'appareil

        Returns:
            Informations de l'appareil ou None si non trouvé
        """
        try:
            # Accéder au cache des appareils via le contexte
            # L'ActivityManager n'a pas directement accès au contexte, mais on peut utiliser le cache service
            # Pour l'instant, on va utiliser une approche simple en important le cache directement
            import json
            from pathlib import Path

            cache_file = Path("data/cache/devices.json")
            if cache_file.exists():
                with open(cache_file, encoding="utf-8") as f:
                    cache_data = cast(Dict[str, Any], json.load(f))

                devices = cast(List[Dict[str, Any]], cache_data.get("devices", []))
                for device in devices:
                    if device.get("serialNumber") == serial_number:
                        return device

            return None

        except Exception as e:
            logger.debug(f"Erreur récupération info appareil {serial_number}: {e}")
            return None

    def get_activity(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une activité spécifique par son ID via l'API Privacy.

        Args:
            activity_id: ID de l'activité (recordKey de l'API Privacy)

        Returns:
            Dictionnaire de l'activité ou None si introuvable
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None

            try:
                # Récupérer les activités récentes via l'API Privacy
                activities = self.get_activities(limit=100)  # Récupérer les 100 dernières

                # Rechercher l'activité par ID (recordKey)
                for activity in activities:
                    if activity.get("id") == activity_id:
                        logger.debug(f"Activité {activity_id} trouvée")
                        return activity

                logger.warning(f"Activité {activity_id} introuvable")
                return None

            except Exception as e:
                logger.error(f"Erreur récupération activité {activity_id}: {e}")
                return None

    def delete_activity(self, activity_id: str) -> bool:
        """
        Supprime une activité de l'historique.

        ⚠️  NON SUPPORTÉ PAR L'API PRIVACY
        L'API Privacy ne permet pas la suppression d'activités individuelles.
        Cette méthode retourne toujours False.

        Args:
            activity_id: ID de l'activité à supprimer

        Returns:
            Toujours False (non supporté)
        """
        logger.warning("Suppression d'activité individuelle non supportée par l'API Privacy")
        return False

    def delete_activities_range(self, start_time: datetime, end_time: Optional[datetime] = None) -> bool:
        """
        Supprime une plage d'activités.

        ⚠️  NON SUPPORTÉ PAR L'API PRIVACY
        L'API Privacy ne permet pas la suppression d'activités.
        Cette méthode retourne toujours False.

        Args:
            start_time: Début de la période
            end_time: Fin de la période (optionnel)

        Returns:
            Toujours False (non supporté)
        """
        logger.warning("Suppression de plage d'activités non supportée par l'API Privacy")
        return False

    def get_last_device(self) -> Optional[str]:
        """
        Récupère le nom de l'appareil qui a eu la dernière interaction.

        Returns:
            Nom de l'appareil ou None si aucune activité trouvée
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None

            try:
                activities = self.get_activities(limit=1)
                if activities:
                    return activities[0].get("deviceName")
                return None
            except Exception as e:
                logger.error(f"Erreur récupération dernier appareil: {e}")
                return None

    def get_last_command(self, device_name: Optional[str] = None) -> Optional[str]:
        """
        Récupère la dernière commande vocale.

        Args:
            device_name: Filtrer par nom d'appareil (optionnel)

        Returns:
            Dernière commande vocale ou None
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None

            try:
                activities = self.get_activities(limit=10)  # Récupérer les 10 dernières

                # Filtrer par appareil si demandé
                if device_name:
                    activities = [a for a in activities if a.get("deviceName") == device_name]

                # Trouver la première activité vocale
                for activity in activities:
                    if activity.get("type") == "voice" and activity.get("utterance"):
                        return cast(str | None, activity["utterance"])

                return None

            except Exception as e:
                logger.error(f"Erreur récupération dernière commande: {e}")
                return None

    def get_voice_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Récupère l'historique vocal des N derniers jours."""
        start = datetime.now() - timedelta(days=days)
        return self.get_activities(limit=200, start_time=start)

    def delete_voice_history(self, days: int = 7) -> bool:
        """Supprime l'historique vocal des N derniers jours."""
        start = datetime.now() - timedelta(days=days)
        return self.delete_activities_range(start)

    def get_last_interaction(self, device_serial: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Récupère la dernière interaction (optionnellement filtrée par appareil)."""
        activities = self.get_activities(limit=10)
        if not device_serial:
            return activities[0] if activities else None

        for activity in activities:
            if activity.get("deviceSerialNumber") == device_serial:
                return activity
        return None

    def add_mock_activity(self, utterance: str, alexa_response: str, device_name: str = "Salon Echo") -> bool:
        """
        Ajoute une activité simulée au cache local.

        Args:
            utterance: Commande vocale de l'utilisateur
            alexa_response: Réponse d'Alexa
            device_name: Nom de l'appareil (optionnel)

        Returns:
            True si ajoutée avec succès
        """
        try:
            # Créer une activité simulée
            mock_activity = {
                "recordKey": f"manual-{int(datetime.now().timestamp())}",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "device": {
                    "deviceName": device_name,
                    "serialNumber": f"MANUAL{int(datetime.now().timestamp())}",
                    "deviceType": "A2UONLFQW0PADH",
                },
                "voiceHistoryRecordItems": [
                    {"recordItemType": "CUSTOMER_TRANSCRIPT", "transcriptText": utterance},
                    {"recordItemType": "ALEXA_RESPONSE", "transcriptText": alexa_response},
                ],
                "activityStatus": "SUCCESS",
            }

            # Charger les activités existantes
            cache_data = self._load_from_local_cache("activities") or {
                "records": [],
                "last_updated": datetime.now().isoformat(),
                "source": "manual",
            }

            # Ajouter la nouvelle activité
            cache_data["records"].insert(0, mock_activity)  # Au début pour qu'elle soit la plus récente
            cache_data["last_updated"] = datetime.now().isoformat()

            # Limiter à 100 activités maximum
            if len(cache_data["records"]) > 100:
                cache_data["records"] = cache_data["records"][:100]

            # Sauvegarder
            self._save_to_local_cache("activities", cache_data)

            logger.info(f"✅ Activité ajoutée: '{utterance}' -> '{alexa_response}'")
            return True

        except Exception as e:
            logger.error(f"Erreur ajout activité simulée: {e}")
            return False

    def get_last_response(self, device_name: Optional[str] = None) -> Optional[str]:
        """
        Récupère la dernière réponse d'Alexa.

        Args:
            device_name: Filtrer par nom d'appareil (optionnel)

        Returns:
            Dernière réponse d'Alexa ou None
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return None

            try:
                activities = self.get_activities(limit=10)  # Récupérer les 10 dernières

                # Filtrer par appareil si demandé
                if device_name:
                    activities = [a for a in activities if a.get("deviceName") == device_name]

                # Trouver la première activité vocale avec réponse Alexa
                for activity in activities:
                    if activity.get("type") == "voice" and activity.get("alexaResponse"):
                        return cast(str | None, activity["alexaResponse"])

                return None

            except Exception as e:
                logger.error(f"Erreur récupération dernière réponse Alexa: {e}")
                return None





