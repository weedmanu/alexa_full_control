"""
Gestionnaire d'alarmes Alexa.

Ce module fournit une interface thread-safe pour créer, lister,
modifier et supprimer des alarmes via l'API Alexa.
"""

import threading
import time
from typing import Any, Dict, List, Optional

import requests
from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine, ConnectionState
from services.cache_service import CacheService


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
        cache_service: Service de cache pour la persistance
        _lock: Verrou pour la thread-safety
        _alarms_cache: Cache mémoire des alarmes
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
        Initialise le gestionnaire d'alarmes.

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

        # Cache multi-niveaux pour les alarmes
        self._alarms_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: int = 60  # 1 minute pour le cache mémoire
        self._lock = threading.RLock()

        logger.info("AlarmManager initialisé")

    def _is_cache_valid(self) -> bool:
        """
        Vérifie si le cache mémoire est encore valide.

        Returns:
            True si le cache existe et n'a pas expiré
        """
        if self._alarms_cache is None:
            return False

        age = time.time() - self._cache_timestamp
        is_valid = age < self._cache_ttl

        if not is_valid:
            logger.debug(f"Cache alarmes expiré (âge: {age:.1f}s, TTL: {self._cache_ttl}s)")

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

    def create_alarm(
        self,
        device_serial: str,
        device_type: str,
        alarm_time: str,
        repeat: str = "ONCE",
        label: str = "",
        sound: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Crée une nouvelle alarme sur un appareil Alexa.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil
            alarm_time: Heure de l'alarme (format ISO 8601)
            repeat: Pattern de répétition (ONCE, DAILY, WEEKLY, etc.)
            label: Étiquette de l'alarme
            sound: ID du son d'alarme (optionnel)

        Returns:
            Dictionnaire avec les détails de l'alarme créée, None en cas d'erreur
        """
        with self._lock:
            if not self._check_connection():
                return None

            try:
                # Construire explicitement le pattern pour que mypy infère bien le type
                pattern: List[Dict[str, Any]] = [
                    {"type": "alarm", "time": alarm_time, "recurrence": repeat}
                ]

                if label:
                    pattern[0]["label"] = label

                if sound:
                    pattern[0]["sound"] = {"id": sound}

                payload: Dict[str, Any] = {
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                    "pattern": pattern,
                }

                logger.debug(f"Création alarme: {payload}")

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/alarms",
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
                logger.success(f"Alarme créée pour {device_serial}")

                # Invalider le cache
                self._alarms_cache = None

                return result

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la création de l'alarme: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return None
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la création de l'alarme: {e}")
                return None

    def list_alarms(self, device_serial: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Liste toutes les alarmes actives.

        Args:
            device_serial: Numéro de série de l'appareil (optionnel, tous les appareils si None)

        Returns:
            Liste des alarmes
        """
        with self._lock:
            if not self._check_connection():
                return []

            # Utiliser le cache si valide
            # Toujours assurer que `cached_alarms` est une liste (pas None)
            cached_alarms: List[Dict[str, Any]] = []
            if self._is_cache_valid():
                logger.debug("💾 Cache alarmes valide, utilisation du cache mémoire")
                if self._alarms_cache is not None:
                    cached_alarms = self._alarms_cache
            else:
                # Charger depuis le cache disque d'abord
                cached_data = self.cache_service.get("alarms")
                if cached_data and isinstance(cached_data, dict):
                    cached_alarms = cached_data.get("alarms", [])
                    logger.debug(f"💾 Cache disque: {len(cached_alarms)} alarme(s)")

                # Si pas de cache disque ou expiré, rafraîchir depuis l'API
                if not cached_alarms:
                    cached_alarms = self._refresh_alarms_cache()
                else:
                    self._alarms_cache = cached_alarms
                    self._cache_timestamp = time.time()

            # Filtrer par appareil si spécifié
            if device_serial:
                alarms = [a for a in cached_alarms if a.get("deviceSerialNumber") == device_serial]
            else:
                alarms = cached_alarms

            return alarms

    def _refresh_alarms_cache(self) -> List[Dict[str, Any]]:
        """
        Rafraîchit le cache des alarmes en effectuant un appel API.

        Les alarmes sont récupérées depuis /api/notifications et filtrées par type "Alarm".

        Returns:
            Liste des alarmes ou liste vide en cas d'erreur
        """
        try:
            logger.debug("🌐 Récupération de toutes les alarmes depuis l'API notifications")

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
                logger.info("Aucune alarme trouvée (réponse vide)")
                alarms = []
            else:
                data = response.json()
                # Les alarmes sont dans la liste des notifications
                notifications = data.get("notifications", [])

                # Filtrer pour ne garder que les alarmes (type="Alarm")
                alarms = [
                    notification
                    for notification in notifications
                    if notification.get("type") == "Alarm"
                ]

            # Mise à jour cache mémoire (Niveau 1)
            self._alarms_cache = alarms
            self._cache_timestamp = time.time()

            # Mise à jour cache disque (Niveau 2) - TTL 5min
            self.cache_service.set("alarms", {"alarms": alarms}, ttl_seconds=300)

            logger.info(
                f"✅ {len(alarms)} alarme(s) récupérée(s) et mise(s) en cache (mémoire + disque)"
            )
            return alarms

        except ValueError as e:
            # Erreur de parsing JSON (réponse vide ou malformée)
            logger.warning(f"Réponse JSON invalide pour les alarmes: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des alarmes: {e}")
            if self.breaker.state.name == "OPEN":
                self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération des alarmes: {e}")
            return []

    def delete_alarm(self, device_serial: str, device_type: str, alarm_id: str) -> bool:
        """
        Supprime une alarme existante.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil
            alarm_id: ID de l'alarme à supprimer

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                response = self.breaker.call(
                    self.auth.session.delete,
                    f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
                    },
                    timeout=10,
                )
                response.raise_for_status()

                logger.success(f"Alarme {alarm_id} supprimée")

                # Invalider le cache
                self._alarms_cache = None

                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la suppression de l'alarme: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la suppression de l'alarme: {e}")
                return False

    def update_alarm(self, device_serial: str, device_type: str, alarm_id: str, **updates) -> bool:
        """
        Modifie une alarme existante.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil
            alarm_id: ID de l'alarme à modifier
            updates: Dictionnaire des modifications (time, label, repeat, sound)

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                payload = {}

                if "time" in updates:
                    payload["time"] = updates["time"]
                if "label" in updates:
                    payload["label"] = updates["label"]
                if "repeat" in updates:
                    payload["recurrence"] = updates["repeat"]
                if "sound" in updates:
                    payload["sound"] = {"id": updates["sound"]}

                if not payload:
                    logger.warning("Aucune modification spécifiée pour l'alarme")
                    return False

                response = self.breaker.call(
                    self.auth.session.put,
                    f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

                logger.success(f"Alarme {alarm_id} modifiée")

                # Invalider le cache
                self._alarms_cache = None

                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la modification de l'alarme: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la modification de l'alarme: {e}")
                return False

    def set_alarm_enabled(
        self, device_serial: str, device_type: str, alarm_id: str, enabled: bool
    ) -> bool:
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
        with self._lock:
            if not self._check_connection():
                return False

            try:
                payload = {"enabled": enabled}

                response = self.breaker.call(
                    self.auth.session.put,
                    f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": self.auth.csrf,
                    },
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

                action = "activée" if enabled else "désactivée"
                logger.success(f"Alarme {alarm_id} {action}")

                # Invalider le cache
                self._alarms_cache = None

                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de l'activation/désactivation de l'alarme: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(
                    f"Erreur inattendue lors de l'activation/désactivation de l'alarme: {e}"
                )
                return False
