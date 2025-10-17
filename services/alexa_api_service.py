"""
Squelette minimal de AlexaAPIService pour Phase 1.
Comportement minimal :
- centraliser ENDPOINTS
- get_devices with cache fallback
- send_speak_command
- _call wrapper (utilise circuit breaker si disponible)

Ce fichier est volontairement simple pour permettre TDD initial.
"""
import uuid
from typing import Any, Dict, List, Optional

try:
    from loguru import logger
except Exception:
    import logging
    logger = logging.getLogger("alexa_api_service")

try:
    from pybreaker import CircuitBreaker
except Exception:
    # fallback minimal circuit breaker with same interface (call)
    class CircuitBreaker:
        def __init__(self, *args, **kwargs):
            pass

        def call(self, fn, *args, **kwargs):
            return fn(*args, **kwargs)

from core.exceptions import APIError
import contextlib


class AlexaAPIService:
    """Service centralisé pour appels Alexa (squelette pour TDD).

    Notes:
    - méthodes publiques simples pour tests
    - extension prévue: retries, logging structuré, DTOs
    """

    ENDPOINTS = {
        "get_devices": "/api/devices-v2/device",
        "speak": "/api/speak",
    }

    def __init__(
        self,
        auth,
        cache,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
    ) -> None:
        self._auth = auth
        self._cache = cache
        self._circuit_breaker = CircuitBreaker(fail_max=circuit_breaker_threshold, reset_timeout=circuit_breaker_timeout)
        # correlation id per instance/request
        self._current_correlation_id: Optional[str] = None

    def _get_correlation_id(self) -> str:
        if not self._current_correlation_id:
            self._current_correlation_id = str(uuid.uuid4())
        return self._current_correlation_id

    def _call(self, method_fn, *args, **kwargs):
        """Wrapper around HTTP calls (uses circuit breaker)."""
        try:
            return self._circuit_breaker.call(method_fn, *args, **kwargs)
        except Exception:
            # bubble up, higher-level methods will convert to APIError
            raise

    def get_devices(self, use_cache_fallback: bool = True) -> List[Dict[str, Any]]:
        cache_key = "devices_list"
        try:
            url = f"https://alexa.{getattr(self._auth, 'amazon_domain', 'amazon.fr')}{self.ENDPOINTS['get_devices']}"
            response = self._call(self._auth.get, url, timeout=10)
            data = response.json()
            devices = data.get("devices", [])
            # set correlation id for tracing
            self._get_correlation_id()
            # Best-effort logging; don't fail on logging errors
            with contextlib.suppress(Exception):
                logger.info("get_devices success", extra={"count": len(devices), "correlation_id": self._current_correlation_id})
            return devices
        except Exception as e:
            # fallback
            if use_cache_fallback and hasattr(self._cache, 'get'):
                cached = self._cache.get(cache_key, ignore_ttl=True)
                if cached:
                    return cached.get("devices", [])
            raise APIError(f"Failed to get devices: {e}") from e

    def send_speak_command(self, device_serial: str, text: str) -> None:
        try:
            url = f"https://alexa.{getattr(self._auth, 'amazon_domain', 'amazon.fr')}{self.ENDPOINTS['speak']}"
            payload = {"deviceSerialNumber": device_serial, "textToSpeak": text}
            self._call(self._auth.post, url, data=payload, timeout=10)
        except Exception as e:
            raise APIError(f"Failed to send speak command: {e}") from e
