"""
Gestionnaire d'alarmes Alexa.

Ce module fournit une interface thread-safe pour créer, lister,
modifier et supprimer des alarmes via l'API Alexa.
"""

import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import requests
from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine, ConnectionState

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.alarm_schemas import AlarmDTO, GetAlarmsResponse

    HAS_ALARM_DTO = True
except ImportError:
    HAS_ALARM_DTO = False


class AlarmManager:
    """
    Gestionnaire thread-safe d'alarmes Alexa.

    Cette classe permet de gérer les alarmes sur les appareils Alexa
    de manière sécurisée avec protection contre les défaillances.

    Attributes:
        auth: Instance d'authentification Alexa
        config: Configuration de l'application
        state_machine: Machine à états pour la connexion
        breaker: Circuit breaker pour la résilience
        _lock: Verrou pour la thread-safety
    """

    def __init__(self, auth: Any, config: Any, state_machine: Optional[AlexaStateMachine] = None) -> None:
        """
        Initialise le gestionnaire d'alarmes.

        Args:
            auth: Instance AlexaAuth avec session authentifiée
            config: Instance Config avec paramètres
            state_machine: Machine à états optionnelle
        """
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30, half_open_max_calls=1)
        self._lock = threading.RLock()
        # Normalize http_client for migration compatibility
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth

        logger.info("AlarmManager initialisé")

    def _check_connection(self) -> bool:
        """Vérifie l'état de la connexion."""
        if not self.state_machine.can_execute_commands:
            logger.error(f"Impossible d'exécuter la commande - État: {self.state_machine.state.name}")
            return False
        return True

    def create_alarm(
        self,
        device_serial: str,
        device_type: str,
        alarm_time: str,
        recurring_pattern: str = "ONCE",
        label: str = "Alarme",
    ) -> Optional[Dict[Any, Any]]:
        """
        Crée une nouvelle alarme.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil
            alarm_time: Heure au format HH:MM ou ISO 8601
            recurring_pattern: ONCE, DAILY, WEEKLY, WEEKDAYS, WEEKENDS
            label: Nom de l'alarme

        Returns:
            Dict avec les détails de l'alarme créée ou None
        """
        with self._lock:
            if not self._check_connection():
                return None

            try:
                # Convertir HH:MM en format ISO 8601 si nécessaire
                if ":" in alarm_time and "T" not in alarm_time:
                    # Format simple HH:MM
                    hour, minute = alarm_time.split(":")
                    now = datetime.now()
                    alarm_datetime = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
                    alarm_time_iso = alarm_datetime.isoformat() + ".000"
                else:
                    alarm_time_iso = alarm_time

                payload = {
                    "type": "Alarm",
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "alarmTime": alarm_time_iso,
                    "originalTime": alarm_time.split("T")[0] if "T" in alarm_time else alarm_time,
                    "status": "ON",
                    "recurringPattern": recurring_pattern,
                    "alarmLabel": label,
                }

                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/alarms",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "Origin": f"https://alexa.{self.config.amazon_domain}",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

                alarm_data = response.json()
                logger.success(f"Alarme '{label}' créée pour {alarm_time} ({recurring_pattern})")
                return cast(Optional[Dict[Any, Any]], alarm_data)

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la création de l'alarme: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return None
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                return None

    def list_alarms(self, device_serial: Optional[str] = None) -> List[Dict[Any, Any]]:
        """
        Liste toutes les alarmes actives.

        Args:
            device_serial: Filtrer par appareil (optionnel)

        Returns:
            Liste de dictionnaires contenant les détails des alarmes
        """
        with self._lock:
            if not self._check_connection():
                return []

            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/alarms",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    timeout=10,
                )
                response.raise_for_status()

                data = response.json()
                alarms = data.get("alarms", [])

                if device_serial:
                    alarms = [a for a in alarms if a.get("deviceSerialNumber") == device_serial]

                logger.info(f"Récupéré {len(alarms)} alarme(s)")
                return cast(List[Dict[Any, Any]], alarms)

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la récupération des alarmes: {e}")
                return []
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                return []

    def get_alarms_typed(self) -> Optional["GetAlarmsResponse"]:
        """
        Phase 3.7: Typed DTO version of list_alarms returning GetAlarmsResponse.

        Returns alarms as GetAlarmsResponse DTO with full type safety.
        Falls back gracefully if DTOs not available.

        Returns:
            GetAlarmsResponse DTO or None if DTOs unavailable
        """
        if not HAS_ALARM_DTO:
            logger.debug("DTO not available, falling back to legacy path")
            return None

        try:
            # Get alarms as dict list
            alarms_list = self.list_alarms()

            # Convert to AlarmDTO objects
            alarm_dtos: list[AlarmDTO] = []
            for a in alarms_list:
                try:
                    alarm_dict = {
                        "alarmId": a.get("id") or a.get("alarmId", f"alarm_{len(alarm_dtos)}"),
                        "label": a.get("label", "Alarm"),
                        "time": a.get("time", "00:00:00"),
                        "enabled": a.get("enabled", True),
                        "recurring": a.get("recurring", False),
                        "daysOfWeek": a.get("daysOfWeek") or a.get("days_of_week", []),
                        "soundUri": a.get("soundUri", a.get("sound_uri")),
                    }
                    alarm_dtos.append(AlarmDTO(**alarm_dict))
                except Exception as e:
                    logger.warning(f"Could not convert alarm to DTO: {e}, skipping")
                    continue

            response = GetAlarmsResponse(alarms=alarm_dtos)
            logger.debug(f"Returning {len(alarm_dtos)} alarms as DTO")
            return response

        except Exception as e:
            logger.error(f"Error in get_alarms_typed: {e}")
            return None

    def delete_alarm(self, alarm_id: str) -> bool:
        """
        Supprime une alarme.

        Args:
            alarm_id: ID de l'alarme à supprimer

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                response = self.breaker.call(
                    self.http_client.delete,
                    f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    timeout=10,
                )
                response.raise_for_status()

                logger.success(f"Alarme {alarm_id} supprimée")
                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la suppression de l'alarme: {e}")
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                return False

    def set_alarm_enabled(self, device_serial: str, device_type: str, alarm_id: str, enabled: bool) -> bool:
        """
        Active ou désactive une alarme.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil
            alarm_id: ID de l'alarme
            enabled: True pour activer, False pour désactiver

        Returns:
            True si succès, False sinon
        """
        # Utiliser update_alarm avec le paramètre enabled
        return self.update_alarm(alarm_id=alarm_id, enabled=enabled)

    def update_alarm(
        self,
        alarm_id: str,
        alarm_time: Optional[str] = None,
        recurring_pattern: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> bool:
        """
        Modifie une alarme existante.

        Args:
            alarm_id: ID de l'alarme
            alarm_time: Nouvelle heure (optionnel)
            recurring_pattern: Nouveau pattern (optionnel)
            enabled: Activer/désactiver (optionnel)

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                payload = {}

                if alarm_time:
                    # Convertir si nécessaire
                    if ":" in alarm_time and "T" not in alarm_time:
                        hour, minute = alarm_time.split(":")
                        now = datetime.now()
                        alarm_datetime = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
                        payload["alarmTime"] = alarm_datetime.isoformat() + ".000"
                    else:
                        payload["alarmTime"] = alarm_time

                if recurring_pattern:
                    payload["recurringPattern"] = recurring_pattern

                if enabled is not None:
                    payload["status"] = "ON" if enabled else "OFF"

                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

                logger.success(f"Alarme {alarm_id} modifiée")
                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la modification de l'alarme: {e}")
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                return False
