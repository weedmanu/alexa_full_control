"""
Configuration runtime de l'application.

Ce module gère les paramètres configurables via :
- Variables d'environnement
- Arguments CLI
- Fichiers de configuration

Fournit une interface unifiée pour accéder aux paramètres.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .constants import AmazonRegions, AppConstants


@dataclass
class AppSettings:
    """Configuration runtime de l'application."""

    # === RÉGION ===
    region: str = field(default=AmazonRegions.FR)

    # === AUTHENTIFICATION ===
    refresh_token: Optional[str] = None
    csrf_token: Optional[str] = None

    # === RÉSEAU ===
    timeout: int = field(default=AppConstants.DEFAULT_TIMEOUT)
    max_retries: int = field(default=AppConstants.MAX_RETRIES)
    verify_ssl: bool = True

    # === CACHE ===
    cache_enabled: bool = True
    cache_ttl: int = field(default=AppConstants.DEVICES_CACHE_TTL)

    # === LOGGING ===
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True

    # === DEBUG ===
    debug_mode: bool = False
    verbose: bool = False

    # === CHEMINS PERSONNALISÉS ===
    config_dir: Optional[Path] = None
    token_file: Optional[Path] = None

    @classmethod
    def from_env(cls) -> "AppSettings":
        """
        Crée les paramètres depuis les variables d'environnement.

        Variables d'environnement supportées:
            - ALEXA_REGION: Région Amazon (fr, de, com, uk, it, es, ca)
            - ALEXA_REFRESH_TOKEN: Token de rafraîchissement
            - ALEXA_CSRF_TOKEN: Token CSRF
            - ALEXA_TIMEOUT: Timeout des requêtes HTTP (secondes)
            - ALEXA_MAX_RETRIES: Nombre max de tentatives
            - ALEXA_VERIFY_SSL: Vérifier les certificats SSL (true/false)
            - ALEXA_CACHE_ENABLED: Activer le cache (true/false)
            - ALEXA_CACHE_TTL: Durée de vie du cache (secondes)
            - ALEXA_LOG_LEVEL: Niveau de log (DEBUG, INFO, WARNING, ERROR)
            - ALEXA_LOG_TO_FILE: Logger dans un fichier (true/false)
            - ALEXA_LOG_TO_CONSOLE: Logger en console (true/false)
            - ALEXA_DEBUG: Mode debug (true/false)
            - ALEXA_VERBOSE: Mode verbose (true/false)
            - ALEXA_CONFIG_DIR: Dossier de configuration personnalisé
            - ALEXA_TOKEN_FILE: Fichier de tokens personnalisé

        Returns:
            AppSettings: Configuration depuis l'environnement
        """
        return cls(
            # Région
            region=os.getenv("ALEXA_REGION", AmazonRegions.FR),
            # Authentification
            refresh_token=os.getenv("ALEXA_REFRESH_TOKEN"),
            csrf_token=os.getenv("ALEXA_CSRF_TOKEN"),
            # Réseau
            timeout=int(os.getenv("ALEXA_TIMEOUT", str(AppConstants.DEFAULT_TIMEOUT))),
            max_retries=int(os.getenv("ALEXA_MAX_RETRIES", str(AppConstants.MAX_RETRIES))),
            verify_ssl=os.getenv("ALEXA_VERIFY_SSL", "true").lower() == "true",
            # Cache
            cache_enabled=os.getenv("ALEXA_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("ALEXA_CACHE_TTL", str(AppConstants.DEVICES_CACHE_TTL))),
            # Logging
            log_level=os.getenv("ALEXA_LOG_LEVEL", "INFO").upper(),
            log_to_file=os.getenv("ALEXA_LOG_TO_FILE", "true").lower() == "true",
            log_to_console=os.getenv("ALEXA_LOG_TO_CONSOLE", "true").lower() == "true",
            # Debug
            debug_mode=os.getenv("ALEXA_DEBUG", "false").lower() == "true",
            verbose=os.getenv("ALEXA_VERBOSE", "false").lower() == "true",
            # Chemins personnalisés
            config_dir=Path(config_dir_str) if (config_dir_str := os.getenv("ALEXA_CONFIG_DIR")) else None,
            token_file=Path(token_file_str) if (token_file_str := os.getenv("ALEXA_TOKEN_FILE")) else None,
        )

    def validate(self) -> None:
        """
        Valide la configuration.

        Raises:
            ValueError: Si la configuration est invalide
        """
        # Valider la région
        if not AmazonRegions.is_valid(self.region):
            valid_regions = ", ".join(AmazonRegions.get_all())
            raise ValueError(f"Région invalide: '{self.region}'. " f"Régions valides: {valid_regions}")

        # Valider le timeout
        if self.timeout <= 0:
            raise ValueError(f"Timeout doit être > 0, reçu: {self.timeout}")

        # Valider les retries
        if self.max_retries < 0:
            raise ValueError(f"max_retries doit être >= 0, reçu: {self.max_retries}")

        # Valider le cache TTL
        if self.cache_ttl < 0:
            raise ValueError(f"cache_ttl doit être >= 0, reçu: {self.cache_ttl}")

        # Valider le log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(f"log_level invalide: '{self.log_level}'. " f"Niveaux valides: {', '.join(valid_levels)}")

    def to_dict(self) -> dict[str, str | int | bool | None]:
        """
        Convertit les paramètres en dictionnaire.

        Returns:
            dict: Paramètres sous forme de dictionnaire
        """
        return {
            "region": self.region,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "verify_ssl": self.verify_ssl,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "log_level": self.log_level,
            "log_to_file": self.log_to_file,
            "log_to_console": self.log_to_console,
            "debug_mode": self.debug_mode,
            "verbose": self.verbose,
            "config_dir": str(self.config_dir) if self.config_dir else None,
            "token_file": str(self.token_file) if self.token_file else None,
        }

    def __repr__(self) -> str:
        """Représentation string des paramètres (cache les tokens)."""
        safe_dict = self.to_dict()
        return f"AppSettings({safe_dict})"


# === INSTANCE GLOBALE ===

# Instance par défaut chargée depuis l'environnement
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """
    Retourne l'instance globale des paramètres.

    Charge depuis l'environnement au premier appel.
    Ensuite, retourne toujours la même instance (singleton).

    Returns:
        AppSettings: Instance globale de configuration

    Example:
        >>> from config import get_settings
        >>> settings = get_settings()
        >>> print(settings.region)
        fr
    """
    global _settings
    if _settings is None:
        _settings = AppSettings.from_env()
        _settings.validate()
    return _settings


def set_settings(settings: AppSettings) -> None:
    """
    Définit l'instance globale des paramètres.

    Utile pour les tests ou la configuration programmatique.

    Args:
        settings: Nouvelle instance de paramètres

    Example:
        >>> from config import AppSettings, set_settings
        >>> custom = AppSettings(region="de", debug_mode=True)
        >>> set_settings(custom)
    """
    global _settings
    settings.validate()
    _settings = settings


def reset_settings() -> None:
    """
    Réinitialise l'instance globale (force rechargement depuis l'env).

    Utile pour les tests.
    """
    global _settings
    _settings = None
