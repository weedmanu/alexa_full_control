"""
Secure Headers Builder - Build HTTP headers securely and uniformly.

Provides:
- Centralized header construction
- CSRF token injection (validated)
- Standard headers (User-Agent, Origin, Referer)
- Extra headers merging
- Thread-safe

Usage:
    >>> csrf_mgr = CSRFManager(auth)
    >>> headers_builder = SecureHeadersBuilder(config, csrf_mgr)
    >>> headers = headers_builder.build(extra_header="value")
"""

from typing import Any, Dict, Optional

from loguru import logger

from .csrf_manager import CSRFManager, SecurityError


class SecureHeadersBuilder:
    """Build secure HTTP headers with validated CSRF tokens."""

    def __init__(self, config: Any, csrf_mgr: Optional[CSRFManager] = None) -> None:
        """
        Initialize headers builder.

        Args:
            config: Configuration with alexa_domain, amazon_domain
            csrf_mgr: CSRFManager instance (required for CSRF token)

        Raises:
            ValueError: If csrf_mgr is None
        """
        if not csrf_mgr:
            raise ValueError("csrf_mgr cannot be None")

        self.config = config
        self.csrf_mgr = csrf_mgr

        logger.debug("SecureHeadersBuilder initialized")

    def build(self, extra_headers: Optional[Dict[str, str]] = None, require_csrf: bool = True) -> Dict[str, str]:
        """
        Build complete HTTP headers with validated CSRF.

        Args:
            extra_headers: Additional headers to merge (optional)
            require_csrf: Raise error if CSRF invalid (default: True)

        Returns:
            Complete headers dictionary

        Raises:
            SecurityError: If CSRF invalid and require_csrf=True
        """
        headers: Dict[str, str] = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Alexa-CLI/1.0",
            "Accept": "application/json",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Referer": f"https://{self.config.alexa_domain}/spa/index.html",
            "Origin": f"https://{self.config.alexa_domain}",
            "DNT": "1",
            "Connection": "keep-alive",
        }

        # Add CSRF token
        try:
            csrf_token = self.csrf_mgr.get_csrf(validate=require_csrf)
            headers["csrf"] = csrf_token
        except SecurityError as e:
            if require_csrf:
                logger.error(f"Invalid CSRF token: {e}")
                raise
            else:
                logger.warning(f"CSRF validation disabled, using empty: {e}")
                headers["csrf"] = ""

        # Merge extra headers
        if extra_headers:
            headers.update(extra_headers)

        return headers

    def build_safe(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Build headers without failing on CSRF errors.

        Args:
            extra_headers: Additional headers to merge

        Returns:
            Headers dict (with empty CSRF if invalid)
        """
        return self.build(extra_headers, require_csrf=False)

    @staticmethod
    def get_standard_headers(config: Any) -> Dict[str, str]:
        """
        Get standard headers without CSRF (for endpoints not requiring auth).

        Args:
            config: Configuration

        Returns:
            Standard headers dict
        """
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Alexa-CLI/1.0",
            "Accept": "application/json",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "DNT": "1",
            "Connection": "keep-alive",
        }
