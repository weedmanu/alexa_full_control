"""
Service d'authentification pour Alexa.

Interface pour l'authentification avec les services Amazon Alexa.
"""

from typing import Any, Optional


class AuthenticationService:
    """Service d'authentification."""

    def __init__(self):
        """Initialise le service d'authentification."""
        self.csrf: Optional[str] = None
        self.session: Any = None  # Mock session
