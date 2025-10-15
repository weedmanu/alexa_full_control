"""
Gestionnaire de rappels Alexa.

Ce module fournit une interface thread-safe pour créer, lister,
modifier et supprimer des rappels via l'API Alexa.
"""

import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine, ConnectionState
from services.cache_service import CacheService


class ReminderManager:
    """
    Gestionnaire thread-safe de rappels Alexa.

    Cette classe permet de gérer les rappels sur les appareils Alexa
    de manière sécurisée avec protection contre les défaillances.

    Attributes:
        auth: Instance d'authentification Alexa
        config: Configuration de l'application
        state_machine: Machine à états pour la connexion
        breaker: Circuit breaker pour la résilience
        cache_service: Service de cache pour la persistance
        _lock: Verrou pour la thread-safety
        _reminders_cache: Cache mémoire des rappels
        _cache_timestamp: Timestamp du dernier refresh du cache
        _cache_ttl: Durée de vie du cache mémoire (secondes)
    """

    def __init__(
        self,
        auth,
        config,
        state_machine: Optional[AlexaStateMachine] = None,
        cache_service: Optional[CacheService] = None,
    ):
        """
        Initialise le gestionnaire de rappels.

        Args:
            auth: Instance AlexaAuth avec session authentifiée
            config: Instance Config avec paramètres
            state_machine: Machine à états optionnelle (créée si None)
            cache_service: Service de cache optionnel (créé si None)
        """
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30, half_open_max_calls=1)
        self.cache_service = cache_service or CacheService()

        # Cache multi-niveaux pour les rappels
        self._reminders_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: int = 60  # 1 minute pour le cache mémoire
        self._lock = threading.RLock()

        logger.info("ReminderManager initialisé")

    def _is_cache_valid(self) -> bool:
        """
        Vérifie si le cache mémoire est encore valide.

        Returns:
            True si le cache existe et n'a pas expiré
        """
        if self._reminders_cache is None:
            return False

        age = time.time() - self._cache_timestamp
        is_valid = age < self._cache_ttl

        if not is_valid:
            logger.debug(f"Cache rappels expiré (âge: {age:.1f}s, TTL: {self._cache_ttl}s)")

        return is_valid

    def _check_connection(self) -> bool:
        """
        Vérifie l'état de la connexion.

        Returns:
            True si connecté, False sinon
        """
        if not self.state_machine.can_execute_commands:
            logger.error(
                f"Impossible d'exécuter la commande - État: {self.state_machine.state.name}"
            )
            return False
        return True

    def create_reminder(self, device_serial: str, label: str, datetime_str: str) -> Optional[Dict]:
        """
        Crée un nouveau rappel ponctuel sur un appareil Alexa.

        Args:
            device_serial: Numéro de série de l'appareil
            label: Texte du rappel
            datetime_str: Date et heure du rappel (format ISO 8601)

        Returns:
            Dictionnaire avec les détails du rappel créé, None en cas d'erreur
        """
        with self._lock:
            if not self._check_connection():
                return None

            try:
                payload = {
                    "type": "Reminder",
                    "deviceSerialNumber": device_serial,
                    "label": label,
                    "createdDate": datetime.now().isoformat(),
                    "reminderTime": datetime_str,
                    "status": "ON",
                }

                logger.debug(f"Création rappel: {payload}")

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/notifications",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

                result = response.json()
                logger.success(f"Rappel créé pour {device_serial}")

                # Invalider le cache
                self._reminders_cache = None

                return result

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la création du rappel: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return None
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la création du rappel: {e}")
                return None

    def create_recurring_reminder(
        self, device_serial: str, label: str, recurrence: str, time_str: str
    ) -> Optional[Dict]:
        """
        Crée un nouveau rappel récurrent sur un appareil Alexa.

        Args:
            device_serial: Numéro de série de l'appareil
            label: Texte du rappel
            recurrence: Type de récurrence (daily, weekly, monthly)
            time_str: Heure du rappel (format HH:MM)

        Returns:
            Dictionnaire avec les détails du rappel créé, None en cas d'erreur
        """
        with self._lock:
            if not self._check_connection():
                return None

            try:
                # Convertir la récurrence en format Alexa
                recurrence_mapping = {"daily": "DAILY", "weekly": "WEEKLY", "monthly": "MONTHLY"}
                alexa_recurrence = recurrence_mapping.get(recurrence.lower(), "DAILY")

                payload = {
                    "type": "Reminder",
                    "deviceSerialNumber": device_serial,
                    "label": label,
                    "createdDate": datetime.now().isoformat(),
                    "recurringTime": time_str,
                    "recurrence": alexa_recurrence,
                    "status": "ON",
                }

                logger.debug(f"Création rappel récurrent: {payload}")

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/notifications",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

                result = response.json()
                logger.success(f"Rappel récurrent créé pour {device_serial}")

                # Invalider le cache
                self._reminders_cache = None

                return result

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la création du rappel récurrent: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return None
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la création du rappel récurrent: {e}")
                return None

    def get_reminders(self, device_serial: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Liste tous les rappels.

        Args:
            device_serial: Numéro de série de l'appareil (optionnel, tous les appareils si None)

        Returns:
            Liste des rappels
        """
        with self._lock:
            if not self._check_connection():
                return []

            # Utiliser le cache si valide
            if self._is_cache_valid():
                logger.debug("💾 Cache rappels valide, utilisation du cache mémoire")
                cached_reminders = self._reminders_cache
            else:
                # Charger depuis le cache disque d'abord
                cached_data = self.cache_service.get("reminders")
                if cached_data and isinstance(cached_data, dict):
                    cached_reminders = cached_data.get("reminders", [])
                    logger.debug(f"💾 Cache disque: {len(cached_reminders)} rappel(s)")
                else:
                    cached_reminders = None

                # Si pas de cache disque ou expiré, rafraîchir depuis l'API
                if cached_reminders is None:
                        cached_reminders = self._refresh_reminders_cache()
                else:
                    self._reminders_cache = cached_reminders
                    self._cache_timestamp = time.time()

            # Filtrer par appareil si spécifié
            if device_serial:
                reminders = [
                    r for r in cached_reminders if r.get("deviceSerialNumber") == device_serial
                ]
            else:
                reminders = cached_reminders

            return reminders

    def _refresh_reminders_cache(self) -> List[Dict[str, Any]]:
        """
        Rafraîchit le cache des rappels en effectuant un appel API.

        Les rappels sont récupérés depuis /api/notifications et filtrés par type "Reminder".

        Returns:
            Liste des rappels ou liste vide en cas d'erreur
        """
        try:
            logger.debug("🌐 Récupération de tous les rappels depuis l'API notifications")

            response = self.breaker.call(
                self.auth.session.get,
                f"https://{self.config.alexa_domain}/api/notifications",
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "csrf": self.auth.csrf,
                },
                timeout=10,
            )
            response.raise_for_status()

            # Gérer le cas où la réponse est vide
            if not response.content.strip():
                logger.info("Aucun rappel trouvé (réponse vide)")
                reminders = []
            else:
                data = response.json()
                # Les rappels sont dans la liste des notifications
                notifications = data.get("notifications", [])

                # Filtrer pour ne garder que les rappels (type="Reminder")
                reminders = [
                    notification
                    for notification in notifications
                    if notification.get("type") == "Reminder"
                ]

            # Mise à jour cache mémoire (Niveau 1)
            self._reminders_cache = reminders
            self._cache_timestamp = time.time()

            # Mise à jour cache disque (Niveau 2) - TTL 5min
            self.cache_service.set("reminders", {"reminders": reminders}, ttl_seconds=300)

            logger.info(
                f"✅ {len(reminders)} rappel(s) récupéré(s) et mis en cache (mémoire + disque)"
            )
            return reminders

        except ValueError as e:
            # Erreur de parsing JSON (réponse vide ou malformée)
            logger.warning(f"Réponse JSON invalide pour les rappels: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des rappels: {e}")
            if self.breaker.state.name == "OPEN":
                self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération des rappels: {e}")
            return []

    def delete_reminder(self, reminder_id: str) -> bool:
        """
        Supprime un rappel existant.

        Args:
            reminder_id: ID du rappel à supprimer

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                response = self.breaker.call(
                    self.auth.session.delete,
                    f"https://{self.config.alexa_domain}/api/notifications/{reminder_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
                    },
                    timeout=10,
                )
                response.raise_for_status()

                logger.success(f"Rappel {reminder_id} supprimé")

                # Invalider le cache
                self._reminders_cache = None

                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la suppression du rappel: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la suppression du rappel: {e}")
                return False

    def complete_reminder(self, reminder_id: str) -> bool:
        """
        Marque un rappel comme complété.

        Args:
            reminder_id: ID du rappel

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                payload = {"status": "COMPLETED"}

                response = self.breaker.call(
                    self.auth.session.put,
                    f"https://{self.config.alexa_domain}/api/notifications/{reminder_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

                logger.success(f"Rappel {reminder_id} marqué comme complété")

                # Invalider le cache
                self._reminders_cache = None

                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors du marquage du rappel comme complété: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue lors du marquage du rappel comme complété: {e}")
                return False
