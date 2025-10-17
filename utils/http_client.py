"""
Client HTTP unifié pour l'API Alexa.

Combine authenticaton injection, cache via OptimizedHTTPSession,
et protection par CircuitBreaker. Convertit erreurs HTTP en exceptions
typiées (core.exceptions).
"""

from typing import Any, Dict, Optional, cast

import requests
from loguru import logger

from core import exceptions
from core.circuit_breaker import CircuitBreaker
from utils.http_session import OptimizedHTTPSession


class AlexaHTTPClient:
    """Client HTTP unifié pour les appels Alexa.

    Args:
        auth_manager: Objet gérant l'auth (possède attributs utiles, ex: csrf)
        cache_enabled: Active l'utilisation du cache HTTP
        circuit_breaker: Instance de CircuitBreaker (créée si None)
    """

    def __init__(
        self,
        auth_manager: Optional[Any] = None,
        cache_enabled: bool = True,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ) -> None:
        self.auth = auth_manager
        self.session: OptimizedHTTPSession = OptimizedHTTPSession(cache_enabled=cache_enabled)
        # Expose a csrf attribute to match HTTPClientProtocol when wrappers are used
        self.csrf: Optional[str] = getattr(auth_manager, "csrf", None) if auth_manager is not None else None
        self.breaker = circuit_breaker or CircuitBreaker()
        self.logger = logger.bind(component="AlexaHTTPClient")

    def _inject_auth(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Injecte headers d'auth (CSRF) si disponible sur auth manager."""
        headers = dict(kwargs.get("headers") or {})
        if self.auth is not None:
            csrf = getattr(self.auth, "csrf", None)
            if csrf:
                headers.setdefault("csrf", csrf)
        if headers:
            kwargs["headers"] = headers
        return kwargs

    def _check_response(self, response: requests.Response) -> None:
        """Lève une requests.HTTPError si le status indique une erreur."""
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            # Log minimal avant conversion
            status = getattr(e.response, "status_code", None)
            self.logger.debug(f"HTTP {status}: {e}")
            # Convertir plus haut via _handle_http_error
            self._handle_http_error(e)

    def _handle_http_error(self, error: requests.HTTPError) -> None:
        """Convertit requests.HTTPError en exceptions typées du domaine."""
        resp = getattr(error, "response", None)
        status = getattr(resp, "status_code", None)

        if status in (401, 403):
            raise exceptions.AuthenticationError(
                f"Authentification échouée ({status})",
                can_refresh=(status == 401),
            ) from error

        # Tenter de récupérer un JSON si disponible
        response_json = None
        try:
            if resp is not None and getattr(resp, "content", None):
                response_json = resp.json()
        except Exception:
            response_json = None

        raise exceptions.APIError(f"Erreur API: HTTP {status}", status_code=status, response=response_json) from error

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Requête GET avec auth injection, cache et circuit breaker.

        Raises:
            AuthenticationError, APIError
        """
        # Provide a sane default timeout if not provided
        kwargs = self._inject_auth(kwargs)
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10

        try:
            response = self.breaker.call(self.session.get, url, **kwargs)
            self._check_response(response)
            return cast(requests.Response, response)
        except requests.HTTPError as e:
            # Convert HTTP errors to domain exceptions
            self._handle_http_error(e)
            raise
        except requests.RequestException as e:
            # Network / connection level errors
            self.logger.error(f"Request failed: {e}")
            raise exceptions.APIError(f"Network error calling {url}") from e

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """Requête POST avec injection auth + retry + breaker.

        Raises:
            AuthenticationError, APIError
        """
        kwargs = self._inject_auth(kwargs)
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10

        try:
            response = self.breaker.call(self.session.post, url, **kwargs)
            self._check_response(response)
            return cast(requests.Response, response)
        except requests.HTTPError as e:
            self._handle_http_error(e)
            raise
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise exceptions.APIError(f"Network error calling {url}") from e

    def put(self, url: str, **kwargs: Any) -> requests.Response:
        """Requête PUT similaire à post/get."""
        kwargs = self._inject_auth(kwargs)
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10

        try:
            response = self.breaker.call(self.session.put, url, **kwargs)
            self._check_response(response)
            return cast(requests.Response, response)
        except requests.HTTPError as e:
            self._handle_http_error(e)
            raise
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise exceptions.APIError(f"Network error calling {url}") from e

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        """Requête DELETE similaire aux autres méthodes."""
        kwargs = self._inject_auth(kwargs)
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10

        try:
            response = self.breaker.call(self.session.delete, url, **kwargs)
            self._check_response(response)
            return cast(requests.Response, response)
        except requests.HTTPError as e:
            self._handle_http_error(e)
            raise
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise exceptions.APIError(f"Network error calling {url}") from e
