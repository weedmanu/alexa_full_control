"""
Circuit Breaker pattern pour éviter les avalanches d'erreurs.

Implémentation thread-safe du pattern Circuit Breaker qui :
- Détecte les défaillances répétées
- Ouvre le circuit après un seuil d'erreurs
- Permet des tentatives de récupération
- Protège le système contre les surcharges
"""

import threading
import time
from enum import Enum, auto
from typing import Any, Callable, TypeVar

# Utiliser logger standard si loguru n'est pas disponible
try:
    from utils.logger import get_logger
    logger = get_logger("circuit_breaker")
except ImportError:
    try:
        from loguru import logger
    except ImportError:
        import logging

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)  # type: ignore

T = TypeVar("T")


class CircuitState(Enum):
    """États du circuit breaker."""

    CLOSED = auto()  # Circuit fermé, requêtes normales
    OPEN = auto()  # Circuit ouvert, requêtes bloquées
    HALF_OPEN = auto()  # Test de récupération


class CircuitBreakerError(Exception):
    """Erreur levée quand le circuit est ouvert."""


class CircuitBreaker:
    """
    Circuit Breaker thread-safe pour protéger contre les défaillances en cascade.

    Utilisation:
        breaker = CircuitBreaker(failure_threshold=5, timeout=60)

        @breaker.protected
        def api_call():
            return requests.get("https://api.example.com")
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        half_open_max_calls: int = 1,
    ):
        """
        Initialise le circuit breaker.

        Args:
            failure_threshold: Nombre d'échecs avant d'ouvrir le circuit
            timeout: Durée en secondes avant de tenter la récupération
            half_open_max_calls: Nombre d'appels autorisés en mode HALF_OPEN
        """
        self._failure_threshold = failure_threshold
        self._timeout = timeout
        self._half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0
        self._half_open_calls = 0

        self._lock = threading.RLock()

        logger.info("Initialisation du Circuit Breaker")
        logger.success(
            f"Circuit Breaker initialisé: threshold={failure_threshold}, timeout={timeout}s"
        )

    @property
    def state(self) -> CircuitState:
        """Retourne l'état actuel du circuit."""
        with self._lock:
            return self._state

    @property
    def is_open(self) -> bool:
        """Vérifie si le circuit est ouvert."""
        return self.state == CircuitState.OPEN

    @property
    def failure_count(self) -> int:
        """Retourne le nombre d'échecs consécutifs."""
        with self._lock:
            return self._failure_count

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Exécute une fonction protégée par le circuit breaker.

        Args:
            func: Fonction à exécuter
            *args: Arguments positionnels
            **kwargs: Arguments nommés

        Returns:
            Résultat de la fonction

        Raises:
            CircuitBreakerError: Si le circuit est ouvert
        """
        with self._lock:
            # Vérifier si on peut tenter une récupération
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self._timeout:
                    logger.info("🔄 Circuit OPEN → HALF_OPEN (tentative récupération)")
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                else:
                    raise CircuitBreakerError(
                        f"Circuit ouvert (timeout restant: "
                        f"{self._timeout - (time.time() - self._last_failure_time):.1f}s)"
                    )

            # Limiter les appels en mode HALF_OPEN
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self._half_open_max_calls:
                    raise CircuitBreakerError("Circuit HALF_OPEN saturé")
                self._half_open_calls += 1

        # Exécuter la fonction
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self) -> None:
        """Appelé après un succès."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info("✅ Circuit HALF_OPEN → CLOSED (récupération réussie)")
                self._state = CircuitState.CLOSED

            self._failure_count = 0

    def _on_failure(self) -> None:
        """Appelé après un échec."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                logger.warning("⚠️ Circuit HALF_OPEN → OPEN (récupération échouée)")
                self._state = CircuitState.OPEN
                return

            if self._failure_count >= self._failure_threshold:
                logger.error(
                    f"❌ Circuit CLOSED → OPEN " f"({self._failure_count} échecs consécutifs)"
                )
                self._state = CircuitState.OPEN

    def reset(self) -> None:
        """Réinitialise le circuit breaker."""
        with self._lock:
            logger.info("🔄 Réinitialisation du Circuit Breaker")
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0
            self._last_failure_time = 0

    def protected(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Décorateur pour protéger une fonction avec le circuit breaker.

        Args:
            func: Fonction à protéger

        Returns:
            Fonction décorée
        """

        def wrapper(*args: Any, **kwargs: Any) -> T:
            return self.call(func, *args, **kwargs)

        return wrapper

    def __str__(self) -> str:
        """Représentation textuelle."""
        return (
            f"CircuitBreaker(state={self.state.name}, "
            f"failures={self._failure_count}/{self._failure_threshold})"
        )

    def __repr__(self) -> str:
        """Représentation détaillée."""
        return self.__str__()
