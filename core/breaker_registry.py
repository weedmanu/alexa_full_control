"""
CircuitBreaker Registry - Centralized singleton circuit breaker management.

Provides:
- Singleton pattern for circuit breakers by name
- Centralized configuration per manager type
- Efficient resource pooling (33 instances → ~5 centralized)
- Thread-safe registry

Usage:
    >>> breaker = CircuitBreakerRegistry.get_or_create("music")
    >>> response = breaker.call(http_client.get, url, **kwargs)
"""

import threading
from typing import Any, Dict

from loguru import logger

from .circuit_breaker import CircuitBreaker


class CircuitBreakerRegistry:
    """Centralized registry of circuit breakers (singleton pattern)."""

    _registry: Dict[str, CircuitBreaker] = {}
    _lock = threading.RLock()

    # Default configurations per manager type
    _configs: Dict[str, Dict[str, Any]] = {
        "default": {
            "failure_threshold": 3,
            "timeout": 30,
            "recovery_timeout": 60,
        },
        "music": {
            "failure_threshold": 2,
            "timeout": 20,
            "recovery_timeout": 40,
        },
        "device": {
            "failure_threshold": 4,
            "timeout": 60,
            "recovery_timeout": 120,
        },
        "alarm": {
            "failure_threshold": 3,
            "timeout": 30,
            "recovery_timeout": 60,
        },
        "routine": {
            "failure_threshold": 3,
            "timeout": 40,
            "recovery_timeout": 80,
        },
    }

    @classmethod
    def get_or_create(cls, name: str) -> CircuitBreaker:
        """
        Get or create circuit breaker by name.

        Uses singleton pattern - same instance returned for same name.

        Args:
            name: Breaker name (ex: "music", "device", "default")

        Returns:
            CircuitBreaker instance
        """
        with cls._lock:
            if name not in cls._registry:
                config = cls._get_config(name)
                cls._registry[name] = CircuitBreaker(**config)
                logger.debug(f"Created CircuitBreaker '{name}': {config}")

            return cls._registry[name]

    @classmethod
    def _get_config(cls, name: str) -> Dict[str, Any]:
        """Get configuration for breaker by name."""
        return cls._configs.get(name, cls._configs["default"])

    @classmethod
    def get_config(cls, name: str) -> Dict[str, Any]:
        """Get configuration (public method)."""
        return cls._get_config(name)

    @classmethod
    def list_breakers(cls) -> Dict[str, CircuitBreaker]:
        """List all registered breakers."""
        with cls._lock:
            return dict(cls._registry)

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get statistics for all breakers."""
        with cls._lock:
            stats: Dict[str, Any] = {}
            for name, breaker in cls._registry.items():
                stats[name] = {
                    "name": name,
                    "state": str(breaker.state),
                    "failure_count": breaker.failure_count,
                    "config": cls._get_config(name),
                }
            return stats

    @classmethod
    def reset(cls) -> None:
        """Reset registry (for testing)."""
        with cls._lock:
            cls._registry.clear()
            logger.debug("CircuitBreaker registry reset")

    @classmethod
    def reset_breaker(cls, name: str) -> None:
        """Reset specific breaker."""
        with cls._lock:
            if name in cls._registry:
                cls._registry[name].reset()
                logger.debug(f"CircuitBreaker '{name}' reset")
