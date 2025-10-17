import threading
import time
from typing import Any, Dict, List, Optional

from loguru import logger

from core.base_manager import BaseManager
from core.circuit_breaker import CircuitBreaker
from core.state_machine import AlexaStateMachine
from services.cache_service import CacheService

# Phase 3.7: Import DTO for typed return
try:
    from core.schemas.timer_schemas import GetTimersResponse, TimerDTO

    HAS_TIMER_DTO = True
except ImportError:
    HAS_TIMER_DTO = False


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
        auth: Any,
        state_machine: AlexaStateMachine,
        api_service: Any,
        cache_service: Optional[CacheService] = None,
        cache_ttl: int = 60,
    ) -> None:
        """
        Initialise le gestionnaire de timers avec injection obligatoire.

        Args:
            auth: Instance AlexaAuth avec session authentifiée
            state_machine: Machine à états pour gestion d'état
            api_service: Service API centralisé (MANDATORY, jamais None)
            cache_service: Service de cache optionnel (créé si None)
            cache_ttl: Durée de vie du cache en secondes (défaut: 60)

        Raises:
            ValueError: Si api_service est None (injection obligatoire)
        """
        if api_service is None:
            raise ValueError("api_service is mandatory and cannot be None")

        # Use central factory to obtain an http_client from legacy auth
        from core.base_manager import create_http_client_from_auth

        http_client = create_http_client_from_auth(auth)

        # Phase 2: Create minimal config for BaseManager (only needs amazon_domain)
        # In Phase 2+, config is not needed for operations, only for headers
        class _MinimalConfig:
            amazon_domain = "amazon.com"

        minimal_config = _MinimalConfig()

        # Phase 2: Mandatory API Service (no fallback)
        super().__init__(
            http_client=http_client,
            config=minimal_config,  # Minimal config just for BaseManager initialization
            state_machine=state_machine,
            cache_service=cache_service,
            cache_ttl=cache_ttl,
        )

        self.auth = auth
        self._api_service = api_service
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30, half_open_max_calls=1)

        # Compatibility memory cache attrs
        self._timers_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: int = cache_ttl
        self._lock = threading.RLock()

        logger.info("✅ TimerManager initialisé avec api_service obligatoire")

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
            logger.error(f"Impossible d'exécuter la commande - État: {self.state_machine.state.name}")
            return False
        return True

    def create_timer(
        self, device_serial: str, device_type: str, duration_minutes: int, label: str = "Timer"
    ) -> Optional[Dict[str, Any]]:
        """
        Crée un nouveau timer sur un appareil Alexa via AlexaAPIService.

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

                # Phase 2: Use api_service directly (no fallback)
                timer_data = self._api_service.post(
                    "/api/timers",
                    json=payload,
                    timeout=10,
                )

                from typing import cast

                timer_data = cast(Dict[str, Any], timer_data)
                logger.success(f"✅ Timer '{label}' créé ({duration_minutes} min)")
                return timer_data

            except Exception as e:
                logger.error(f"❌ Erreur lors de la création du timer: {e}")
                return None

    def list_timers(self, device_serial: Optional[str] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
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

    def get_timers_typed(self, force_refresh: bool = False) -> Optional["GetTimersResponse"]:
        """
        Phase 3.7: Typed DTO version of list_timers returning GetTimersResponse.

        Returns timers as GetTimersResponse DTO with full type safety.
        Falls back gracefully if DTOs not available.

        Args:
            force_refresh: Force refresh from API

        Returns:
            GetTimersResponse DTO or None if DTOs unavailable
        """
        if not HAS_TIMER_DTO:
            logger.debug("DTO not available, falling back to legacy path")
            return None

        try:
            # Get timers as dict list
            timers_list = self.list_timers(force_refresh=force_refresh)

            # Convert to TimerDTO objects
            timer_dtos = []
            for t in timers_list:
                try:
                    # Map dict to TimerDTO with camelCase aliases
                    timer_dict = {
                        "timerId": t.get("id") or t.get("timerId", f"timer_{len(timer_dtos)}"),
                        "label": t.get("timerLabel", t.get("label", "Timer")),
                        "durationMs": t.get("durationMs", t.get("duration", 0)),
                        "state": t.get("status") or t.get("state"),
                        "remainingMs": t.get("remainingMs", t.get("remaining")),
                        "soundUri": t.get("soundUri", t.get("sound_uri")),
                    }
                    timer_dtos.append(TimerDTO(**timer_dict))
                except Exception as e:
                    logger.warning(f"Could not convert timer to DTO: {e}, skipping")
                    continue

            response = GetTimersResponse(timers=timer_dtos)
            logger.debug(f"Returning {len(timer_dtos)} timers as DTO")
            return response

        except Exception as e:
            logger.error(f"Error in get_timers_typed: {e}")
            return None

    def _refresh_timers_cache(self) -> List[Dict[str, Any]]:
        """
        Rafraîchit le cache des timers via AlexaAPIService.

        Les timers sont récupérés depuis /api/notifications et filtrés par type "Timer" et status "ON".

        Returns:
            Liste des timers ou liste vide en cas d'erreur
        """
        try:
            logger.debug("🌐 Récupération de tous les timers depuis l'API notifications")

            # Phase 2: Use api_service directly (mandatory, no fallback)
            data = self._api_service.get("/api/notifications", timeout=10)

            if data is None:
                logger.warning("⚠️  Réponse vide pour les timers")
                timers = []
            else:
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

            logger.info(f"✅ {len(timers)} timer(s) actif(s) récupéré(s) et mis en cache")
            return timers

        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des timers: {e}")
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

                logger.success(f"{success_count}/{len(timers)} timer(s) annulé(s) pour {device_serial}")
                return success_count > 0
            except Exception as e:
                logger.error(f"Erreur annulation timers: {e}")
                return False

    def cancel_timer(self, timer_id: str) -> bool:
        """
        Annule un timer existant via AlexaAPIService.

        Args:
            timer_id: ID du timer à annuler

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self._check_connection():
                return False

            try:
                # Phase 2: Use api_service directly (no fallback)
                self._api_service.delete(f"/api/timers/{timer_id}", timeout=10)
                logger.success(f"✅ Timer {timer_id} annulé")
                return True

            except Exception as e:
                logger.error(f"❌ Erreur lors de l'annulation du timer: {e}")
                return False

    def pause_timer(self, timer_id: str) -> bool:
        """
        Met en pause un timer via AlexaAPIService.

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

                # Phase 2: Use api_service directly (no fallback)
                self._api_service.put(f"/api/timers/{timer_id}", json=payload, timeout=10)
                logger.success(f"✅ Timer {timer_id} mis en pause")
                return True

            except Exception as e:
                logger.error(f"❌ Erreur lors de la mise en pause du timer: {e}")
                return False

    def resume_timer(self, timer_id: str) -> bool:
        """
        Reprend un timer en pause via AlexaAPIService.

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

                # Phase 2: Use api_service directly (no fallback)
                self._api_service.put(f"/api/timers/{timer_id}", json=payload, timeout=10)
                logger.success(f"✅ Timer {timer_id} repris")
                return True

            except Exception as e:
                logger.error(f"❌ Erreur lors de la reprise du timer: {e}")
                return False
