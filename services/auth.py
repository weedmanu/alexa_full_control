"""
Contrats et types pour l'authentification Alexa.

Ce module ne fournit pas l'implémentation de l'authentification (voir
``alexa_auth/alexa_auth.py`` pour `AlexaAuth`). Il expose un contrat léger
pour typer les services qui consomment une session authentifiée.
"""

from typing import Optional, Protocol

import requests


class AuthClient(Protocol):
    """Contrat minimal attendu par les services.

    Attributs requis:
        - session: requests.Session déjà peuplée avec les cookies Alexa
        - csrf: token CSRF si disponible

    Toute classe fournissant ces attributs est compatible (ex: `AlexaAuth`).
    """

    session: requests.Session
    csrf: Optional[str]


__all__ = ["AuthClient"]
