"""AlexaAPIService for Phase 1."""
from __future__ import annotations
import time, logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AlexaAPIError(Exception):
    pass

class ApiError(AlexaAPIError):
    def __init__(self, status: int, body: Any = None, endpoint: str | None = None):
        super().__init__(f"API error {status} for {endpoint}: {body}")
        self.status = status
        self.body = body
        self.endpoint = endpoint

class NetworkError(AlexaAPIError):
    pass

class CircuitOpen(AlexaAPIError):
    pass

class AlexaAPIService:
    ENDPOINTS: Dict[str, str] = {"get_devices": "/api/devices-v2/device", "speak": "/api/speak"}
    
    def __init__(self, *args: Any, session: Any = None, cache_service: Any = None, breaker_registry: Any = None, **kwargs: Any) -> None:
        self._breaker_failures: Dict[str, int] = {}
        if args:
            auth = args[0] if len(args) > 0 else None
            cache = args[1] if len(args) > 1 else None
            self._auth = auth
            self._cache = cache
            class _AuthSessionShim:
                def __init__(self, auth_obj: Any): self._a = auth_obj
                def request(self, method: str, url: str, **kw: Any) -> Any:
                    m = method.lower()
                    if m == "get": return self._a.get(url, **kw)
                    if m == "post": return self._a.post(url, **kw)
                    if m == "put": return self._a.put(url, **kw)
                    if m == "delete": return self._a.delete(url, **kw)
                    raise ValueError(f"Unsupported: {method}")
            self._session = _AuthSessionShim(self._auth)
            return
        self._session = session or __import__("requests").Session()
        self._cache = cache_service
        self._auth = None
    
    def _resolve_path(self, key_or_path: str) -> str:
        if key_or_path.startswith("http"): return key_or_path
        if key_or_path in self.ENDPOINTS: return self.ENDPOINTS[key_or_path]
        if key_or_path.startswith("/"): return key_or_path
        return "/" + key_or_path
    
    def _check_breaker(self, endpoint: str) -> None:
        if self._breaker_failures.get(endpoint, 0) >= 2:
            raise CircuitOpen(f"Circuit open for {endpoint}")
    
    def _record_failure(self, endpoint: str) -> None:
        self._breaker_failures[endpoint] = self._breaker_failures.get(endpoint, 0) + 1
    
    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        endpoint = path
        self._check_breaker(endpoint)
        url = self._resolve_path(path)
        try:
            start = time.time()
            resp = self._session.request(method, url, **kwargs)
            duration = time.time() - start
            logger.debug("Request %s %s -> %s (%.3fs)", method, url, getattr(resp, "status_code", None), duration)
        except Exception as exc:
            logger.exception("Network error for %s %s", method, url)
            self._record_failure(endpoint)
            raise NetworkError(exc)
        status = getattr(resp, "status_code", None)
        try:
            body = resp.json() if hasattr(resp, "json") else None
        except Exception:
            body = getattr(resp, "text", None)
        if status is not None and status >= 400:
            self._record_failure(endpoint)
            raise ApiError(status, body=body, endpoint=endpoint)
        return body
    
    def get(self, path: str, cache_key: Optional[str] = None, **kwargs: Any) -> Any:
        try:
            return self._request("GET", path, **kwargs)
        except NetworkError:
            if cache_key and self._cache:
                try:
                    cached = self._cache.get(cache_key, ignore_ttl=True)
                    if cached is not None:
                        logger.info("Cached: %s", cache_key)
                        return cached
                except Exception:
                    pass
            raise
    
    def post(self, path: str, json: Any = None, **kwargs: Any) -> Any:
        return self._request("POST", path, json=json, **kwargs)
    
    def get_devices(self, use_cache_fallback: bool = True) -> list:
        if not hasattr(self, "_auth") or self._auth is None:
            res = self.get("devices")
            if isinstance(res, dict): return res.get("devices", [])
            return res
        cache_key = "devices_list"
        try:
            path = self.ENDPOINTS.get("get_devices", "/devices")
            domain = getattr(self._auth, "amazon_domain", "amazon.fr")
            url = f"https://alexa.{domain}{path}"
            resp = self._auth.get(url, timeout=10)
            data = resp.json()
            return data.get("devices", [])
        except Exception as exc:
            if use_cache_fallback and hasattr(self, "_cache") and self._cache:
                try:
                    cached = self._cache.get(cache_key, ignore_ttl=True)
                    if cached: return cached.get("devices", [])
                except Exception:
                    pass
            from core.exceptions import APIError as CoreAPIError
            raise CoreAPIError(f"Failed: {exc}") from exc
    
    def send_speak_command(self, device_serial: str, text: str) -> None:
        if not hasattr(self, "_auth") or self._auth is None:
            path = self.ENDPOINTS.get("speak", "/speak")
            self.post(path, json={"deviceSerialNumber": device_serial, "textToSpeak": text}, timeout=10)
            return
        try:
            path = self.ENDPOINTS.get("speak", "/speak")
            domain = getattr(self._auth, "amazon_domain", "amazon.fr")
            url = f"https://alexa.{domain}{path}"
            payload = {"deviceSerialNumber": device_serial, "textToSpeak": text}
            self._auth.post(url, data=payload, timeout=10)
        except Exception as exc:
            from core.exceptions import APIError as CoreAPIError
            raise CoreAPIError(f"Failed: {exc}") from exc
