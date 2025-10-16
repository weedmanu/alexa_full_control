"""
CSRF Token Manager - Centralized CSRF token management with validation and refresh.

Provides:
- Centralized CSRF token retrieval
- Token validation (format, expiration)
- Automatic refresh on expiration (30 min TTL)
- Thread-safe caching
"""

import threading
import time
from typing import Any, Dict, Optional

from loguru import logger


class SecurityError(Exception):
    """Raised when security check fails."""

    pass


class CSRFManager:
    """
    Centralized CSRF token manager.

    Manages Amazon Alexa CSRF tokens with:
    - Validation (format, non-empty)
    - Automatic refresh (30 min TTL)
    - Thread-safe caching
    - Error handling

    Example:
        >>> csrf_mgr = CSRFManager(auth)
        >>> token = csrf_mgr.get_csrf(validate=True)
        >>> # Token is validated format before returning
    """

    def __init__(self, auth: Any) -> None:
        """
        Initialize CSRF manager.

        Args:
            auth: AlexaAuth instance for token retrieval
        """
        self.auth = auth
        self._csrf_cache: Optional[str] = None
        self._csrf_timestamp: float = 0.0
        self._lock = threading.RLock()
        self._refresh_ttl = 1800  # 30 minutes
        self._min_token_len = 10

        logger.debug("CSRFManager initialized")

    def get_csrf(self, validate: bool = True) -> str:
        """
        Get CSRF token with optional validation.

        Args:
            validate: Validate token format before returning (default: True)

        Returns:
            CSRF token string

        Raises:
            SecurityError: If token invalid and validate=True
        """
        with self._lock:
            # Refresh if expired (30 min TTL)
            if self._should_refresh_csrf():
                self._refresh_csrf_from_auth()

            csrf = self._csrf_cache or ""

            if validate and not self._is_valid_csrf(csrf):
                raise SecurityError(f"Invalid or empty CSRF token (length: {len(csrf)})")

            return csrf

    def get_csrf_safe(self, default: str = "") -> str:
        """
        Get CSRF token safely without raising errors.

        Args:
            default: Default value if token invalid

        Returns:
            CSRF token or default
        """
        try:
            return self.get_csrf(validate=True)
        except SecurityError:
            logger.warning("CSRF token invalid, using default")
            return default

    def invalidate(self) -> None:
        """Invalidate cached token to force refresh on next get."""
        with self._lock:
            self._csrf_cache = None
            self._csrf_timestamp = 0.0
            logger.debug("CSRF token cache invalidated")

    # === Private Methods ===

    def _should_refresh_csrf(self) -> bool:
        """Check if CSRF token should be refreshed (>30 min old)."""
        age = time.time() - self._csrf_timestamp
        return age > self._refresh_ttl

    def _is_valid_csrf(self, csrf: str) -> bool:
        """
        Validate CSRF token format.

        Valid tokens:
        - Non-empty
        - Length >= 10 chars
        - Amazon format: starts with 'amzn.' OR alphanumeric+hyphens

        Args:
            csrf: Token to validate

        Returns:
            True if valid, False otherwise
        """
        if not csrf:
            return False

        if len(csrf) < self._min_token_len:
            return False

        # Amazon format tokens start with 'amzn.' or are long alphanumeric
        is_amazon_format = csrf.startswith("amzn.")
        is_alphanum = all(c.isalnum() or c in "-_" for c in csrf)

        return is_amazon_format or (is_alphanum and len(csrf) > 20)

    def _refresh_csrf_from_auth(self) -> None:
        """Fetch CSRF token from auth and cache it."""
        try:
            csrf = getattr(self.auth, "csrf", None)

            if csrf and self._is_valid_csrf(csrf):
                self._csrf_cache = csrf
                self._csrf_timestamp = time.time()
                logger.debug(f"CSRF token refreshed (expires in {self._refresh_ttl}s)")
            else:
                logger.warning(f"Auth CSRF invalid: {csrf[:10] if csrf else 'None'}...")
                self._csrf_cache = None
                self._csrf_timestamp = 0.0

        except Exception as e:
            logger.error(f"Error refreshing CSRF from auth: {e}")
            self._csrf_cache = None
            self._csrf_timestamp = 0.0

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        with self._lock:
            age = time.time() - self._csrf_timestamp
            return {
                "cached": self._csrf_cache is not None,
                "age_seconds": age if self._csrf_cache else None,
                "valid": self._is_valid_csrf(self._csrf_cache or ""),
                "needs_refresh": self._should_refresh_csrf(),
                "token_length": len(self._csrf_cache) if self._csrf_cache else 0,
            }
