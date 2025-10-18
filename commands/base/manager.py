"""
BaseManager: classe de base pour tous les managers Alexa.

Fournit:
- cache m?moire + disque via CacheService
- v?rification de connexion via AlexaStateMachine
- RLock pour thread-safety
- logger binding
"""

import time
from threading import RLock
from typing import Any, Dict, Generic, List, Optional, TypeVar, cast

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
    compatible (get/post/put/delete) et on expose `csrf` si pr?sent. Sinon, on
    retourne directement `auth` (on suppose qu'il impl?mente d?j? l'interface).
    """
    from typing import cast

    if hasattr(auth, "session"):
        return _ClientWrapper(auth.session, getattr(auth, "csrf", None))
    # auth may already implement HTTPClientProtocol; cast for the typechecker
    return cast(HTTPClientProtocol, auth)


T = TypeVar("T")


class BaseManager(Generic[T]):
    """Classe de base r?utilisable pour managers Alexa."""

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

        # Pr?-calcul des headers statiques pour optimisation
        self._base_headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
            "Origin": f"https://alexa.{self.config.amazon_domain}",
        }

        # Optimisation : niveau de log pour ?viter les logs inutiles en production
        import os

        self._debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

        self.logger = logger.bind(manager=self.__class__.__name__)

    def _is_cache_valid(self) -> bool:
        """V?rifie si le cache m?moire est encore valide."""
        if self._cache is None:
            return False

        age = time.time() - self._cache_timestamp
        return age < self._cache_ttl

    def _check_connection(self) -> bool:
        """Retourne True si la state machine permet d'ex?cuter des commandes.

        Gardons un contrat simple (bool) pour que les managers l'utilisent dans des guards `if`.
        """
        if not self.state_machine.can_execute_commands:
            self.logger.error(f"?tat connexion invalide: {self.state_machine.state.name}")
            return False
        return True

    def _invalidate_cache(self) -> None:
        """Invalide le cache m?moire."""
        with self._lock:
            self._cache = None
            self._cache_timestamp = 0.0
            self.logger.debug("Cache invalid?")

    def _get_api_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Retourne les headers HTTP standard pour les appels API Alexa.

        Args:
            extra: Headers additionnels optionnels (fusionn?s avec les standards)

        Returns:
            Dictionnaire de headers pr?t pour requests

        Example:
            >>> headers = self._get_api_headers({"X-Custom": "value"})
        """
        headers = self._base_headers.copy()

        csrf_value = getattr(self.http_client, "csrf", None)
        if csrf_value is not None:
            headers["csrf"] = csrf_value

        if extra:
            headers.update(extra)

        return headers

    def _make_cache_key(self, endpoint: str, params_obj: Optional[Dict[str, Any]] = None) -> str:
        """
        Construire une cl? de cache s?re ? partir d'un endpoint et de ses params.

        La cl? est nettoy?e pour ?tre s?re pour le syst?me de fichiers.
        """
        try:
            import json as _json, re as _re

            params_str = _json.dumps(params_obj or {}, sort_keys=True, ensure_ascii=False)
            raw = f"api:{endpoint}:{params_str}"
            safe = _re.sub(r"[^A-Za-z0-9._-]+", "_", raw)
            return safe
        except Exception:
            # Fallback conservative
            return endpoint.replace("/", "_").replace("?", "_").replace("=", "_")

    def _api_call(
        self, method: str, endpoint: str, use_breaker: bool = True, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Wrapper unifi? pour tous les appels API avec gestion d'erreurs compl?te.

        Cette m?thode encapsule:
        - Construction URL compl?te
        - Injection headers standards (via _get_api_headers)
        - Protection circuit breaker
        - Gestion erreurs HTTP
        - Logging standardis?
        - Transition state machine si circuit open

        Args:
            method: M?thode HTTP ('get', 'post', 'put', 'delete')
            endpoint: Endpoint relatif (ex: '/api/alarms')
            use_breaker: Utiliser le circuit breaker (d?faut: True)
            **kwargs: Arguments pour requests (json, params, timeout, etc.)

        Returns:
            R?ponse JSON pars?e ou None si erreur

        Example:
            >>> result = self._api_call('post', '/api/alarms', json=payload, timeout=10)
        """
        # Construction URL compl?te
        url = f"https://{self.config.alexa_domain}{endpoint}"

        # Injection headers (fusionner avec headers fournis si pr?sents)
        headers = self._get_api_headers(kwargs.pop("headers", None))
        kwargs["headers"] = headers

        # D?finir timeout par d?faut si non fourni
        kwargs.setdefault("timeout", 10)

        # --- Caching: uniquement pour les GET retournant JSON ---
        cache_key = None
        is_get = method.lower() == "get"
        if is_get:
            # key based on endpoint + params (if any)
            try:
                params_obj = kwargs.get("params") or {}
                # deterministic serialization
                import json as _json

                params_str = _json.dumps(params_obj, sort_keys=True, ensure_ascii=False)
            except Exception:
                params_str = ""
            cache_key = f"api:{endpoint}:{params_str}"
            # sanitize cache key for filesystem storage (CacheService uses it as filename)
            try:
                import re as _re

                safe_cache_key = _re.sub(r"[^A-Za-z0-9._-]+", "_", cache_key)
            except Exception:
                safe_cache_key = cache_key.replace("/", "_").replace(":", "_")

            # try to return cached value if present
                try:
                    cached = None
                    if self.cache_service:
                        cached = self.cache_service.get(safe_cache_key)
                    if cached is not None:
                        # debug info
                        if self._debug_mode:
                            self.logger.debug(f"? CacheService hit: {cache_key} -> {safe_cache_key}")
                        return cast(Dict[str, Any], cached)
                    else:
                        if self._debug_mode:
                            self.logger.debug(f"?? CacheService miss: {cache_key} -> {safe_cache_key}")
                except Exception:
                    # Cache errors must not break API calls
                    self.logger.debug("CacheService unavailable or error during get")

        try:
            # Appel avec ou sans breaker
            if use_breaker and hasattr(self, "breaker"):
                response = self.breaker.call(getattr(self.http_client, method), url, **kwargs)
            else:
                response = getattr(self.http_client, method)(url, **kwargs)

            # V?rifier status HTTP
            response.raise_for_status()

            # Parser JSON (g?rer r?ponse vide)
            if response.content.strip():
                parsed = cast(Dict[str, Any], response.json())

                # Si c'?tait un GET et que nous avons une cl? cache, enregistrer
                if is_get and cache_key and parsed is not None:
                    try:
                        # TTL: essayer d'obtenir depuis le client HTTP (si expos?)
                        ttl = getattr(self.http_client, "get_cache_ttl", None)
                        if callable(ttl):
                            try:
                                ttl_val = int(ttl(url))
                            except Exception:
                                ttl_val = int(self._cache_ttl)
                        else:
                            ttl_val = int(self._cache_ttl)

                        if self.cache_service:
                            # ensure serializable; cache_service.set will handle
                            # use filesystem-safe key
                            try:
                                self.cache_service.set(safe_cache_key, parsed, ttl_seconds=ttl_val)
                                if self._debug_mode:
                                    self.logger.debug(f"CacheService saved: {cache_key} -> {safe_cache_key} (ttl={ttl_val}s)")
                            except Exception:
                                self.logger.debug("CacheService.save failed")
                    except Exception:
                        # Never break the API call on cache error
                        self.logger.debug("CacheService.save failed")

                return parsed
            else:
                if self._debug_mode:
                    self.logger.debug(f"R?ponse vide pour {method.upper()} {endpoint}")
                return {}

        except ValueError as e:
            # Erreur parsing JSON
            self.logger.warning(f"R?ponse JSON invalide pour {endpoint}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            # Erreur HTTP/r?seau
            self.logger.error(f"Erreur {method.upper()} {endpoint}: {e}")

            # Transition state machine si circuit ouvert
            if hasattr(self, "breaker") and hasattr(self.breaker, "state") and self.breaker.state.name == "OPEN":
                from core.state_machine import ConnectionState

                self.state_machine.transition_to(ConnectionState.CIRCUIT_OPEN)

            return None

        except Exception as e:
            # Erreur inattendue
            self.logger.error(f"Erreur inattendue {method.upper()} {endpoint}: {e}")
            return None






