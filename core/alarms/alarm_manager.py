"""
Gestionnaire d'alarmes Alexa.

Ce module fournit une interface thread-safe pour créer, lister,
modifier et supprimer des alarmes via l'API Alexa.
"""

import threading
import time
from typing import Any, Dict, List, Optional, cast

import requests
from loguru import logger

from core.base_manager import BaseManager
from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine, ConnectionState
from services.cache_service import CacheService


class AlarmManager(BaseManager[Dict[str, Any]]):
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
        auth: Any,
        config: Any,
        state_machine: Optional[AlexaStateMachine] = None,
        cache_service: Optional[CacheService] = None,
        http_client: Optional[Any] = None,
        api_service: Optional[Any] = None,
    ) -> None:
        """
        Initialise le gestionnaire d'alarmes.

        Args:
            auth: Instance AlexaAuth avec session authentifiée
            config: Instance Config avec paramètres
            state_machine: Machine à états optionnelle (créée si None)
            cache_service: Service de cache optionnel (créé si None)
        """
        # Resolve http_client: prefer explicit param, otherwise derive from legacy auth
        from core.base_manager import create_http_client_from_auth

        resolved_http_client = http_client or create_http_client_from_auth(auth)

        # Initialize BaseManager with the resolved http_client
        super().__init__(
            http_client=resolved_http_client,
            config=config,
            state_machine=state_machine or AlexaStateMachine(),
            cache_service=cache_service,
            cache_ttl=60,
        )

        # Keep legacy attribute for compatibility
        self.auth = auth
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30, half_open_max_calls=1)

        # Optional centralized AlexaAPIService
        self._api_service: Optional[Any] = api_service

        # Backwards-compatible in-memory cache attributes used by existing methods
        self._alarms_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: int = 60
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
            logger.error(f"Impossible d'exécuter la commande - État: {self.state_machine.state.name}")
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
    ) -> Optional[Dict[str, Any]]:
        """
        Crée une nouvelle alarme sur un appareil Alexa.
        """
        with self._lock:
            if not self._check_connection():
                return None

            # Construire le payload
            pattern: List[Dict[str, Any]] = [{"type": "alarm", "time": alarm_time, "recurrence": repeat}]

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

            if self._api_service is not None:
                result = cast(Optional[Dict[str, Any]], self._api_service.post("/api/alarms", json=payload))
            else:
                result = self._api_call("post", "/api/alarms", json=payload)

            if result is not None:
                logger.success(f"Alarme créée pour {device_serial}")
                self._invalidate_cache()
                return result

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
        """
        logger.debug("🌐 Récupération de toutes les alarmes depuis l'API notifications")

        if self._api_service is not None:
            result = self._api_service.get("/api/notifications")
        else:
            result = self._api_call("get", "/api/notifications")

        if result is None:
            return []

        # Gérer le cas où la réponse est vide
        if not result:
            logger.info("Aucune alarme trouvée (réponse vide)")
            alarms = []
        else:
            # Les alarmes sont dans la liste des notifications
            notifications = result.get("notifications", [])
            # Filtrer pour ne garder que les alarmes (type="Alarm")
            alarms = [notification for notification in notifications if notification.get("type") == "Alarm"]

        # Mise à jour cache mémoire (Niveau 1)
        self._alarms_cache = alarms
        self._cache_timestamp = time.time()

        # Mise à jour cache disque (Niveau 2) - TTL 5min
        self.cache_service.set("alarms", {"alarms": alarms}, ttl_seconds=300)

        logger.info(f"✅ {len(alarms)} alarme(s) récupérée(s) et mise(s) en cache (mémoire + disque)")
        return alarms

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
                    self.http_client.delete,
                    f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", None),
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

    def update_alarm(self, device_serial: str, device_type: str, alarm_id: str, **updates: Any) -> bool:
        """
        Modifie une alarme existante.
        """
        with self._lock:
            if not self._check_connection():
                return False

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

            if self._api_service is not None:
                result = self._api_service.put(f"/api/alarms/{alarm_id}", json=payload)
            else:
                result = self._api_call("put", f"/api/alarms/{alarm_id}", json=payload)

            if result is not None:
                logger.success(f"Alarme {alarm_id} modifiée")
                self._invalidate_cache()
                return True

            return False

    def set_alarm_enabled(self, device_serial: str, device_type: str, alarm_id: str, enabled: bool) -> bool:
        """
        Active ou désactive une alarme.
        """
        with self._lock:
            if not self._check_connection():
                return False

            payload = {"enabled": enabled}

            if self._api_service is not None:
                result = self._api_service.put(f"/api/alarms/{alarm_id}", json=payload)
            else:
                result = self._api_call("put", f"/api/alarms/{alarm_id}", json=payload)

            if result is not None:
                action = "activée" if enabled else "désactivée"
                logger.success(f"Alarme {alarm_id} {action}")
                self._invalidate_cache()
                return True

            return False
