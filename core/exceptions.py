"""
Hiérarchie d'exceptions personnalisées pour Alexa Full Control.

Ce module centralise toutes les exceptions métier pour une gestion
d'erreur typée et informative.
"""
from typing import Any, Dict, List, Optional


class AlexaError(Exception):
    """Base pour toutes les exceptions spécifiques à Alexa."""


class AuthenticationError(AlexaError):
    """Erreur d'authentification.

    Args:
        message: Message d'erreur lisible
        can_refresh: Indique si une tentative de rafraîchissement est possible
    """

    def __init__(self, message: str, can_refresh: bool = True) -> None:
        super().__init__(message)
        self.can_refresh: bool = can_refresh


class APIError(AlexaError):
    """Erreur lors d'un appel API.

    Args:
        message: Message d'erreur lisible
        status_code: Code HTTP éventuel
        response: Payload JSON de la réponse si disponible
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code: Optional[int] = status_code
        self.response: Optional[Dict[str, Any]] = response


class DeviceNotFoundError(AlexaError):
    """Exception levée quand un appareil n'est pas trouvé.

    Args:
        device_name: Nom recherché de l'appareil
        available_devices: Liste des noms d'appareils disponibles
    """

    def __init__(self, device_name: str, available_devices: Optional[List[str]] = None) -> None:
        super().__init__(f"Appareil '{device_name}' non trouvé")
        self.device_name: str = device_name
        self.available_devices: List[str] = available_devices or []


class CircuitBreakerOpenError(AlexaError):
    """Circuit breaker ouvert (trop d'échecs)."""


class CacheError(AlexaError):
    """Erreur liée au service de cache."""


class ValidationError(AlexaError):
    """Erreur de validation des données (entrée invalide)."""


__all__ = [
    "AlexaError",
    "AuthenticationError",
    "APIError",
    "DeviceNotFoundError",
    "CircuitBreakerOpenError",
    "CacheError",
    "ValidationError",
]
