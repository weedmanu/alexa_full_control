"""
BaseManager: classe de base pour tous les managers Alexa.

Fournit:
- cache mémoire + disque via CacheService
- vérification de connexion via AlexaStateMachine
- RLock pour thread-safety
- logger binding
"""

import time
from threading import RLock
from typing import Any, Generic, List, Optional, TypeVar, cast

import requests
from loguru import logger

from core.state_machine import AlexaStateMachine
from core.types import HTTPClientProtocol
from services.cache_service import CacheService


class _ClientWrapper:
    """Petit wrapper pour les objets legacy qui exposent `session`.

    Permet d'utiliser un ancien `auth` (avec `.session` et `.csrf`) comme
    `HTTPClientProtocol` sans modifier tous les managers.
    """

    def __init__(self, session: Any, csrf_val: Optional[str] = None) -> None:
        self._session = session
        self.csrf = csrf_val

    def get(self, url: str, **kwargs: Any) -> "requests.Response":
        return cast("requests.Response", self._session.get(url, **kwargs))

    def post(self, url: str, **kwargs: Any) -> "requests.Response":
        return cast("requests.Response", self._session.post(url, **kwargs))

    def put(self, url: str, **kwargs: Any) -> "requests.Response":
        return cast("requests.Response", self._session.put(url, **kwargs))

    def delete(self, url: str, **kwargs: Any) -> "requests.Response":
        return cast("requests.Response", self._session.delete(url, **kwargs))


def create_http_client_from_auth(auth: Any) -> HTTPClientProtocol:
    """Fabrique publique qui retourne un client HTTP utilisable depuis un objet legacy `auth`.

    Si `auth` expose `.session` (ancien pattern), on wrap la session dans un objet
    compatible (get/post/put/delete) et on expose `csrf` si présent. Sinon, on
    retourne directement `auth` (on suppose qu'il implémente déjà l'interface).
    """
    from typing import cast

    if hasattr(auth, "session"):
        return _ClientWrapper(auth.session, getattr(auth, "csrf", None))
    # auth may already implement HTTPClientProtocol; cast for the typechecker
    return cast(HTTPClientProtocol, auth)


T = TypeVar("T")


class BaseManager(Generic[T]):
    """Classe de base réutilisable pour managers Alexa."""

    def __init__(
        self,
        http_client: Any,
        config: Any,
        state_machine: AlexaStateMachine,
        cache_service: Optional[CacheService] = None,
        cache_ttl: int = 60,
    ) -> None:
        # If a legacy object with `.session` is passed (old auth), wrap it
        # Declare attribute with type once
        self.http_client: HTTPClientProtocol
        if hasattr(http_client, "session"):
            wrapper = _ClientWrapper(http_client.session, getattr(http_client, "csrf", None))
            self.http_client = wrapper
        else:
            self.http_client = http_client

        self.config: Any = config
        self.state_machine = state_machine
        self.cache_service = cache_service or CacheService()

        self._cache: Optional[List[T]] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: int = cache_ttl
        self._lock = RLock()

        self.logger = logger.bind(manager=self.__class__.__name__)

    def _is_cache_valid(self) -> bool:
        """Vérifie si le cache mémoire est encore valide."""
        if self._cache is None:
            return False

        age = time.time() - self._cache_timestamp
        return age < self._cache_ttl

    def _check_connection(self) -> bool:
        """Retourne True si la state machine permet d'exécuter des commandes.

        Gardons un contrat simple (bool) pour que les managers l'utilisent dans des guards `if`.
        """
        if not self.state_machine.can_execute_commands:
            self.logger.error(f"État connexion invalide: {self.state_machine.state.name}")
            return False
        return True

    def _invalidate_cache(self) -> None:
        """Invalide le cache mémoire."""
        with self._lock:
            self._cache = None
            self._cache_timestamp = 0.0
            self.logger.debug("Cache invalidé")
