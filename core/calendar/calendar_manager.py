"""
Gestionnaire des événements du calendrier Alexa via TextCommand.

Ce module gère les événements du calendrier synchronisés avec Amazon Alexa.
ATTENTION: Amazon n'expose PAS d'API REST pour le calendrier.
On utilise donc TextCommand (commandes vocales simulées).

Limitations:
    - Pas d'API REST pour créer/modifier/supprimer des événements
    - Les événements proviennent de Google/Microsoft/Apple Calendar (sync externe)
    - Seule la consultation via commande vocale est possible
    - Pas d'accès aux détails complets (ID, participants, etc.)

Auteur: M@nu
Date: 12 octobre 2025
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from loguru import logger

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.base import ResponseDTO  # noqa: F401

    HAS_CALENDAR_DTO = True
except ImportError:
    HAS_CALENDAR_DTO = False


class CalendarManager:
    """
    Gestionnaire des événements du calendrier Alexa via TextCommand.

    Utilise des commandes vocales simulées pour interroger le calendrier.
    Amazon ne fournit PAS d'API REST pour gérer le calendrier directement.

    Fonctionnalités disponibles:
        - Consulter les événements (via commande vocale)
        - Demander les événements du jour/demain/semaine

    Limitations:
        - Pas de création/modification/suppression via API
        - Pas d'accès aux détails structurés (ID, participants, lieu exact)
        - Dépend de la réponse vocale d'Alexa (parsing nécessaire)

    Attributes:
        auth: Instance d'authentification AlexaAuth
        voice_service: Service de commandes vocales TextCommand

    Example:
        >>> calendar_mgr = CalendarManager(auth, voice_service)
        >>> response = calendar_mgr.query_events("aujourd'hui", "Salon Echo")
        >>> print(response)  # "Alexa va énoncer vos événements aujourd'hui"
    """

    def __init__(
        self,
        auth: Any,
        config: Any = None,
        voice_service: Optional[Any] = None,
        device_manager: Optional[Any] = None,
    ):
        """
        Initialise le gestionnaire de calendrier.

        Args:
            auth: Instance AlexaAuth avec session et credentials
            config: Configuration Alexa (domaine Amazon, etc.)
            voice_service: Service de commandes vocales (VoiceCommandService)
            device_manager: Gestionnaire de devices pour résoudre les noms
        """
        self.auth = auth
        self.config = config
        self.voice_service = voice_service
        self.device_manager = device_manager
        self._privacy_csrf_cache = None
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            # Fallback: utiliser directement l'objet auth (legacy auth expose session)
            self.http_client = self.auth
        logger.debug("CalendarManager initialisé (mode TextCommand)")

    def get_privacy_csrf(self) -> Optional[str]:
        """
        Récupère le token CSRF pour l'API Privacy.

        Returns:
            Token CSRF Privacy ou None
        """
        try:
            # Utiliser directement le CSRF des cookies (fonctionne pour Privacy API)
            if self.auth.csrf:
                logger.debug("✅ Utilisation du token CSRF pour l'API Privacy")
                return cast(str | None, self.auth.csrf)

            logger.error("❌ Aucun token CSRF disponible")
            return None

        except Exception:
            logger.exception("Erreur lors de la récupération du CSRF Privacy")
            return None

    def test_privacy_api_endpoints(self) -> Dict[str, Any]:
        """
        Teste différents endpoints Privacy API pour le calendrier.

        Returns:
            Dictionnaire avec les résultats des tests
        """
        results = {}

        privacy_csrf = self.get_privacy_csrf()
        if not privacy_csrf:
            return {"error": "Pas de token CSRF Privacy"}

        # Liste d'endpoints à tester (GET et POST)
        tests = [
            ("/alexa-privacy/apd/calendar", "GET"),
            ("/alexa-privacy/apd/calendar", "POST"),
            ("/alexa-privacy/apd/calendar/events", "GET"),
            ("/alexa-privacy/apd/calendar/events", "POST"),
            ("/alexa-privacy/apd/rvh/calendar-events", "POST"),
            ("/api/calendar/events", "GET"),
            ("/api/calendar-events", "GET"),
            ("/api/namedLists?listType=CALENDAR", "GET"),
        ]

        for endpoint, method in tests:
            try:
                url = f"https://www.{self.config.amazon_domain}{endpoint}"
                logger.debug(f"Test {method} {endpoint}")

                headers = {
                    "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    "anti-csrftoken-a2z": privacy_csrf,
                    "Content-Type": "application/json; charset=UTF-8",
                }

                if method == "POST":
                    # Payload minimal pour POST
                    payload: Dict[str, Any] = {}
                    response = self.http_client.post(url, json=payload, headers=headers)
                else:
                    response = self.http_client.get(url, headers=headers)

                results[f"{method} {endpoint}"] = {
                    "status": response.status_code,
                    "content_type": response.headers.get("Content-Type", ""),
                    "size": len(response.content),
                }

                if response.status_code == 200:
                    logger.info(f"✅ {method} {endpoint} → {response.status_code}")
                    # Sauvegarder la réponse pour analyse
                    try:
                        results[f"{method} {endpoint}"]["data"] = response.json()
                    except Exception:
                        results[f"{method} {endpoint}"]["text"] = response.text[:500]
                else:
                    logger.warning(f"⚠️ {method} {endpoint} → {response.status_code}")

            except Exception as e:
                results[f"{method} {endpoint}"] = {"error": str(e)}
                logger.error(f"❌ {method} {endpoint} → Erreur: {e}")

        return results

    def query_events(self, timeframe: str = "aujourd'hui", device_name: Optional[str] = None) -> Optional[str]:
        """
        Interroge Alexa sur les événements du calendrier via commande vocale.

        Args:
            timeframe: Période à consulter ("aujourd'hui", "demain", "cette semaine", etc.)
            device_name: Nom de l'appareil (OBLIGATOIRE pour TextCommand)

        Returns:
            Réponse vocale d'Alexa (texte) ou None si erreur

        Example:
            >>> response = calendar_mgr.query_events("aujourd'hui", "Salon Echo")
            >>> print(response)  # "Vous avez 2 événements aujourd'hui..."
        """
        try:
            # Device obligatoire pour TextCommand
            if not device_name:
                logger.error("❌ Device obligatoire pour TextCommand")
                return None

            if not self.voice_service:
                logger.error("VoiceCommandService non disponible")
                return None

            if not self.device_manager:
                logger.error("DeviceManager non disponible")
                return None

            # Convertir nom du device en serial
            device_serial = self.device_manager.get_device_serial(device_name)
            if not device_serial:
                logger.error(f"❌ Device {device_name} introuvable dans le cache")
                return None

            # Construire la commande vocale
            command = f"quels sont mes événements {timeframe}"

            logger.debug(f"Commande calendrier: '{command}' sur {device_name} (serial={device_serial})")

            # Envoyer la commande via TextCommand
            success = self.voice_service.speak(command, device_serial)

            if success:
                logger.info(f"✅ Commande calendrier '{timeframe}' envoyée à {device_name}")
                return f"Alexa va énoncer vos événements {timeframe}"
            else:
                logger.error("❌ Échec de la commande calendrier")
                return None

        except Exception:
            logger.exception("Erreur lors de la requête calendrier")
            return None

    def get_events(self, limit: int = 50, days_ahead: int = 30) -> Optional[List[Dict[str, Any]]]:
        """
        SIMULATION: Récupère les événements via commande vocale.

        ATTENTION: Cette méthode ne peut PAS retourner de données structurées
        car Amazon n'expose pas d'API REST pour le calendrier.

        Args:
            limit: Non utilisé (compat API)
            days_ahead: Utilisé pour déterminer la période

        Returns:
            Liste vide (API REST non disponible)
        """
        logger.warning("⚠️ API REST calendrier non disponible - utilisez query_events()")

        # Déterminer la période
        if days_ahead == 1:
            timeframe = "aujourd'hui"
        elif days_ahead == 2:
            timeframe = "demain"
        elif days_ahead <= 7:
            timeframe = "cette semaine"
        else:
            timeframe = "ce mois"

        # Exécuter la commande vocale
        self.query_events(timeframe)

        return []  # Pas de données structurées disponibles

    def add_event(
        self,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        SIMULATION: Ajoute un événement via commande vocale.

        ATTENTION: La création d'événements calendrier n'est PAS supportée
        par l'API Amazon Alexa. Les événements doivent être créés via
        Google Calendar, Outlook, ou Apple Calendar qui se synchronisent avec Alexa.

        Args:
            title: Titre de l'événement
            start_time: Date/heure de début
            end_time: Date/heure de fin (ignoré)
            location: Lieu (ignoré)
            description: Description (ignorée)

        Returns:
            None (fonctionnalité non disponible)
        """
        logger.warning("⚠️ Création d'événements non disponible via API Alexa")
        logger.info("💡 Utilisez Google Calendar, Outlook ou Apple Calendar pour créer des événements")

        # Alternative: essayer une commande vocale (limitée)
        if self.voice_service:
            # Format de la date pour Alexa
            date_str = start_time.strftime("%d %B à %H heures %M")
            command = f"crée un événement {title} le {date_str}"

            logger.debug(f"Tentative création via TextCommand: {command}")
            self.voice_service.speak(command)

        # mark unused parameters to avoid static dead-code detectors
        _ = location
        _ = description

        return None

    def delete_event(self, event_id: str) -> bool:
        """
        SIMULATION: Supprime un événement.

        ATTENTION: La suppression d'événements n'est PAS supportée.
        Les événements doivent être supprimés depuis l'application source
        (Google Calendar, Outlook, Apple Calendar).

        Args:
            event_id: ID de l'événement (non utilisé)

        Returns:
            False (fonctionnalité non disponible)
        """
        # mark event_id as intentionally unused (API not available)
        _ = event_id
        logger.warning("⚠️ Suppression d'événements non disponible via API Alexa")
        logger.info("💡 Supprimez l'événement depuis Google Calendar, Outlook ou Apple Calendar")
        return False

    def get_event_details(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        SIMULATION: Récupère les détails d'un événement.

        ATTENTION: L'accès aux détails d'événements n'est PAS supporté.

        Args:
            event_id: ID de l'événement (non utilisé)

        Returns:
            None (fonctionnalité non disponible)
        """
        # event_id is intentionally unused; detailed API not available
        _ = event_id
        logger.warning("⚠️ Détails d'événements non disponibles via API Alexa")
        logger.info("💡 Consultez l'événement depuis Google Calendar, Outlook ou Apple Calendar")
        return None
