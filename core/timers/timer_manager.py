"""
Gestionnaire de timers Alexa.

Ce module fournit une interface thread-safe pour créer, lister,
modifier et annuler des timers via l'API Alexa.
"""

import threading
import time
from typing import Any, Dict, List, Optional

import requests
from loguru import logger

from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine, ConnectionState
from services.cache_service import CacheService
from core.base_manager import BaseManager


class TimerManager(BaseManager[Dict[str, Any]]):
    """
    Gestionnaire thread-safe de timers Alexa.

    Cette classe permet de gérer les timers sur les appareils Alexa
    de manière sécurisée avec protection contre les défaillances.

    Attributes:
        auth: Instance d'authentification Alexa
        config: Configuration de l'application
        state_machine: Machine à états pour la connexion
        breaker: Circuit breaker pour la résilience
        cache_service: Service de cache pour la persistance
        _lock: Verrou pour la thread-safety
        _timers_cache: Cache mémoire des timers
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
        Initialise le gestionnaire de timers.

        Args:
            auth: Instance AlexaAuth avec session authentifiée
            config: Instance Config avec paramètres
            state_machine: Machine à états optionnelle (créée si None)
            cache_service: Service de cache optionnel (créé si None)
        """
        # compatibility: wrap legacy auth.session into http_client if needed
        if hasattr(auth, "session"):
            class _ClientWrapper:
                def __init__(self, session, csrf_val):
                    self.session = session
                    self.csrf = csrf_val

                def get(self, url: str, **kwargs):
                    return self.session.get(url, **kwargs)

                def post(self, url: str, **kwargs):
                    return self.session.post(url, **kwargs)

                def put(self, url: str, **kwargs):
                    return self.session.put(url, **kwargs)

                def delete(self, url: str, **kwargs):
                    return self.session.delete(url, **kwargs)

            http_client = _ClientWrapper(auth.session, getattr(auth, "csrf", None))
        else:
            http_client = auth

        super().__init__(http_client=http_client, config=config, state_machine=state_machine or AlexaStateMachine(), cache_service=cache_service, cache_ttl=60)

        self.auth = auth
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30, half_open_max_calls=1)

        # compatibility memory cache attrs
        self._timers_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: int = 60
        self._lock = threading.RLock()

        logger.info("TimerManager initialisé")

    def _is_cache_valid(self) -> bool:
        """
        Vérifie si le cache mémoire est encore valide.

        Returns:
            True si le cache existe et n'a pas expiré
        """
        if self._timers_cache is None:
            return False

        age = time.time() - self._cache_timestamp
        is_valid = age < self._cache_ttl

        if not is_valid:
            logger.debug(f"Cache timers expiré (âge: {age:.1f}s, TTL: {self._cache_ttl}s)")

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

    def create_timer(
        self, device_serial: str, device_type: str, duration_minutes: int, label: str = "Timer"
    ) -> Optional[Dict]:
        """
        Crée un nouveau timer sur un appareil Alexa.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil
            duration_minutes: Durée en minutes
            label: Nom du timer (optionnel)

        Returns:
            Dict avec les détails du timer créé ou None en cas d'erreur

        Raises:
            RequestException: Si l'API retourne une erreur
        """
        with self._lock:
            if not self._check_connection():
                return None

            try:
                # Convertir en format ISO 8601 duration
                duration_iso = f"PT{duration_minutes}M"

                payload = {
                    "type": "Timer",
                    "status": "ON",
                    "timerLabel": label,
                    "originalDuration": duration_iso,
                    "deviceSerialNumber": device_serial,
                    "deviceType": device_type,
                }

                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/timers",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "Origin": f"https://alexa.{self.config.amazon_domain}",
                        "csrf": getattr(self.http_client, "csrf", None),
                    },
                    json=payload,
                    timeout=10,
                )
                assert response is not None
                response.raise_for_status()

                timer_data = response.json()
                logger.success(f"Timer '{label}' créé ({duration_minutes} min)")
                return timer_data

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la création du timer: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return None
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la création du timer: {e}")
                return None

    def list_timers(
        self, device_serial: Optional[str] = None, force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Liste tous les timers actifs avec système de cache multi-niveaux.

        Utilise un cache multi-niveaux :
        1. Cache mémoire (rapide, TTL 1min)
        2. Cache disque (persistant, TTL 5min)
        3. API Amazon (si cache expiré)

        Args:
            device_serial: Filtrer par appareil (optionnel)
            force_refresh: Force le refresh du cache

        Returns:
            Liste de dictionnaires contenant les détails des timers
        """
        with self._lock:
            if not self._check_connection():
                return []

            # Niveau 1 : Cache mémoire
            if not force_refresh and self._is_cache_valid():
                if self._timers_cache is not None:
                    logger.debug(f"✅ Cache mémoire: {len(self._timers_cache)} timer(s)")
                    timers = self._timers_cache
                else:
                    timers = []
            else:
                # Niveau 2 : Cache disque
                if not force_refresh:
                    disk_cache = self.cache_service.get("timers")
                    if disk_cache and "timers" in disk_cache:
                        logger.debug(f"💾 Cache disque: {len(disk_cache['timers'])} timer(s)")
                        self._timers_cache = disk_cache["timers"]
                        self._cache_timestamp = time.time()
                        timers = self._timers_cache if self._timers_cache is not None else []
                    else:
                        timers = self._refresh_timers_cache()
                else:
                    timers = self._refresh_timers_cache()

            # Filtrer par appareil si spécifié
            if device_serial:
                timers = [t for t in timers if t.get("deviceSerialNumber") == device_serial]

            return timers

    def _refresh_timers_cache(self) -> List[Dict[str, Any]]:
        """
        Rafraîchit le cache des timers en effectuant un appel API.

        Les timers sont récupérés depuis /api/notifications et filtrés par type "Timer" et status "ON".

        Returns:
            Liste des timers ou liste vide en cas d'erreur
        """
        try:
            logger.debug("🌐 Récupération de tous les timers depuis l'API notifications")

            response = self.breaker.call(
                self.http_client.get,
                f"https://{self.config.alexa_domain}/api/notifications",
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "csrf": getattr(self.http_client, "csrf", None),
                },
                timeout=10,
            )
            assert response is not None
            response.raise_for_status()

            # Gérer le cas où la réponse est vide
            if not response.content.strip():
                logger.info("Aucun timer trouvé (réponse vide)")
                timers = []
            else:
                data = response.json()
                # Les timers sont dans la liste des notifications
                notifications = data.get("notifications", [])

                # Filtrer pour ne garder que les timers actifs (type="Timer" et status="ON")
                timers = [
                    notification
                    for notification in notifications
                    if notification.get("type") == "Timer" and notification.get("status") == "ON"
                ]

            # Mise à jour cache mémoire (Niveau 1)
            self._timers_cache = timers
            self._cache_timestamp = time.time()

            # Mise à jour cache disque (Niveau 2) - TTL 5min
            self.cache_service.set("timers", {"timers": timers}, ttl_seconds=300)

            logger.info(
                f"✅ {len(timers)} timer(s) actif(s) récupéré(s) et mis en cache (mémoire + disque)"
            )
            return timers

        except ValueError as e:
            # Erreur de parsing JSON (réponse vide ou malformée)
            logger.warning(f"Réponse JSON invalide pour les timers: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des timers: {e}")
            if self.breaker.state.name == "OPEN":
                self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération des timers: {e}")
            return []

    def cancel_all_timers(self, device_serial: str, device_type: str) -> bool:
        """
        Annule tous les timers d'un appareil.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil

        Returns:
            True si au moins un timer annulé, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                # Récupérer tous les timers de l'appareil
                timers = self.list_timers(device_serial)

                if not timers:
                    logger.info(f"Aucun timer actif pour {device_serial}")
                    return True

                # Annuler chaque timer
                success_count = 0
                for timer in timers:
                    timer_id = timer.get("id") or timer.get("timerId")
                    if timer_id and self.cancel_timer(timer_id):
                        success_count += 1

                logger.success(
                    f"{success_count}/{len(timers)} timer(s) annulé(s) pour {device_serial}"
                )
                return success_count > 0
            except Exception as e:
                logger.error(f"Erreur annulation timers: {e}")
                return False

    def cancel_timer(self, timer_id: str) -> bool:
        """
        Annule un timer existant.

        Args:
            timer_id: ID du timer à annuler

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                response = self.breaker.call(
                    self.http_client.delete,
                    f"https://{self.config.alexa_domain}/api/timers/{timer_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", None),
                    },
                    timeout=10,
                )
                assert response is not None
                response.raise_for_status()

                logger.success(f"Timer {timer_id} annulé")
                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de l'annulation du timer: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue lors de l'annulation du timer: {e}")
                return False

    def pause_timer(self, timer_id: str) -> bool:
        """
        Met en pause un timer.

        Args:
            timer_id: ID du timer à mettre en pause

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                payload = {"status": "PAUSED"}

                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/timers/{timer_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", None),
                    },
                    json=payload,
                    timeout=10,
                )
                assert response is not None
                response.raise_for_status()

                logger.success(f"Timer {timer_id} mis en pause")
                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la mise en pause du timer: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la mise en pause du timer: {e}")
                return False

    def resume_timer(self, timer_id: str) -> bool:
        """
        Reprend un timer en pause.

        Args:
            timer_id: ID du timer à reprendre

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                payload = {"status": "ON"}

                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/timers/{timer_id}",
                    headers={
                        "Content-Type": "application/json; charset=UTF-8",
                        "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                        "csrf": getattr(self.http_client, "csrf", None),
                    },
                    json=payload,
                    timeout=10,
                )
                assert response is not None
                response.raise_for_status()

                logger.success(f"Timer {timer_id} repris")
                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la reprise du timer: {e}")
                if self.breaker.state.name == "OPEN":
                    self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)
                return False
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la reprise du timer: {e}")
                return False
