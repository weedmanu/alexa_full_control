"""
Configuration centralisée et validation pour Alexa CLI.

Gère tous les paramètres de configuration avec validation robuste.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Utiliser logger standard si loguru n'est pas disponible
try:
    from loguru import logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # type: ignore


class ConfigurationError(Exception):
    """Erreur levée lors d'une configuration invalide."""


class Config:
    """
    Configuration globale de l'application Alexa CLI.

    Centralise tous les paramètres de configuration avec validation
    et valeurs par défaut sécurisées.
    """

    def __init__(self) -> None:
        """Initialise la configuration avec validation."""
        self.script_dir = Path(__file__).parent.parent.absolute()

        # === Fichiers d'authentification ===
        self.auth_dir = self.script_dir / "alexa_auth"
        self.data_dir = self.auth_dir / "data"
        self.nodejs_dir = self.auth_dir / "nodejs"

        self.token_file = self.data_dir / "cookie-resultat.json"
        self.refresh_script = self.nodejs_dir / "auth-refresh.js"

        # Valider que les fichiers critiques existent
        self._validate_critical_files()

        # === Configuration régionale ===
        self.language = os.getenv("LANGUAGE", "fr_FR")
        self.tts_locale = os.getenv("TTS_LOCALE", "fr-FR")
        self.amazon_domain = os.getenv("AMAZON", "amazon.fr")
        self.alexa_domain = os.getenv("ALEXA", "alexa.amazon.fr")

        # === User Agent ===
        self.user_agent = os.getenv(
            "BROWSER",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) Alexa-CLI/1.0",
        )

        # === Répertoire temporaire ===
        self.tmp_dir = self._get_temp_dir()

        # === Fichiers de travail (dans temp) ===
        self.cookie_file = self.tmp_dir / ".alexa.cookie"
        self.devlist_file = self.tmp_dir / ".alexa.devicelist"

        # === Durées de vie ===
        self.cookie_lifetime_seconds = 24 * 60 * 60  # 24 heures
        self.devlist_cache_seconds = 3600  # 1 heure

        # === Configuration du volume ===
        self.speak_volume = self._get_int_env("SPEAKVOL", 0, min_val=0, max_val=100)
        self.normal_volume = self._get_int_env("NORMALVOL", 10, min_val=0, max_val=100)
        self.volume_max_age_hours = self._get_int_env("VOLMAXAGE", 1, min_val=1)

        # === Volumes spécifiques par appareil ===
        self.device_volume_names: List[str] = os.getenv("DEVICEVOLNAME", "").split()
        self.device_volumes_speak = self._parse_int_list(os.getenv("DEVICEVOLSPEAK", ""), min_val=0, max_val=100)
        self.device_volumes_normal = self._parse_int_list(os.getenv("DEVICEVOLNORMAL", ""), min_val=0, max_val=100)

        # === Configuration API ===
        self.api_timeout_seconds = 30
        self.api_max_retries = 3
        self.api_retry_delay_seconds = 1

        # === Circuit Breaker ===
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout_seconds = 60

        # === Rate Limiting ===
        self.rate_limit_calls = 10
        self.rate_limit_period_seconds = 60

        # === Version ===
        self.gui_version = 0
        self.cli_version = "1.0.0"

        logger.info("✅ Configuration initialisée")
        self._log_config()

    def _get_temp_dir(self) -> Path:
        """Retourne le répertoire temporaire selon la plateforme."""
        import tempfile

        # On Windows prefer the TEMP env var but fall back to the system tempdir
        if sys.platform == "win32":
            tmp_env = os.getenv("TEMP")
            tmp_path = Path(tmp_env) if tmp_env else Path(tempfile.gettempdir())
        else:
            # For non-Windows platforms prefer the system temporary directory.
            # Use tempfile.gettempdir() rather than hardcoding '/tmp' to avoid
            # Bandit warnings about hardcoded temp dirs and to be portable.
            try:
                # Use a platform-independent temporary directory instead of hardcoding /tmp
                tmp_dir = tempfile.gettempdir()
                tmp_path = Path(tmp_dir)
            except Exception:
                # Fallback to current working directory if tempfile fails
                tmp_path = Path(".")

        # Vérifier que le répertoire existe et est accessible
        if not tmp_path.exists():
            raise ConfigurationError(f"Répertoire temporaire inexistant: {tmp_path}")

        if not os.access(tmp_path, os.W_OK):
            raise ConfigurationError(f"Pas de permission d'écriture: {tmp_path}")

        return tmp_path

    def _get_int_env(
        self,
        env_var: str,
        default: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
    ) -> int:
        """
        Récupère une variable d'environnement entière avec validation.

        Args:
            env_var: Nom de la variable d'environnement
            default: Valeur par défaut
            min_val: Valeur minimale autorisée
            max_val: Valeur maximale autorisée

        Returns:
            Valeur validée

        Raises:
            ConfigurationError: Si la valeur est invalide
        """
        value_str = os.getenv(env_var)
        if not value_str:
            return default

        try:
            value = int(value_str)
        except ValueError as e:
            raise ConfigurationError(f"Variable {env_var}='{value_str}' n'est pas un entier valide") from e

        if min_val is not None and value < min_val:
            raise ConfigurationError(f"Variable {env_var}={value} < minimum {min_val}")

        if max_val is not None and value > max_val:
            raise ConfigurationError(f"Variable {env_var}={value} > maximum {max_val}")

        return value

    def _parse_int_list(
        self, value_str: str, min_val: Optional[int] = None, max_val: Optional[int] = None
    ) -> List[int]:
        """
        Parse une liste d'entiers depuis une chaîne.

        Args:
            value_str: Chaîne contenant les entiers séparés par des espaces
            min_val: Valeur minimale autorisée
            max_val: Valeur maximale autorisée

        Returns:
            Liste d'entiers validés
        """
        if not value_str.strip():
            return []

        result = []
        for part in value_str.split():
            try:
                value = int(part)
                if min_val is not None and value < min_val:
                    logger.warning(f"Valeur {value} < minimum {min_val}, ignorée")
                    continue
                if max_val is not None and value > max_val:
                    logger.warning(f"Valeur {value} > maximum {max_val}, ignorée")
                    continue
                result.append(value)
            except ValueError:
                logger.warning(f"Valeur '{part}' n'est pas un entier, ignorée")
                continue

        return result

    def _validate_critical_files(self) -> None:
        """
        Valide l'existence des fichiers critiques.

        Raises:
            ConfigurationError: Si un fichier critique est manquant
        """
        # Le fichier token peut ne pas exister au premier lancement
        if not self.token_file.exists():
            logger.warning(f"⚠️ Fichier token absent: {self.token_file} (sera créé lors de l'authentification)")

        # Le script de refresh doit exister
        if not self.refresh_script.exists():
            raise ConfigurationError(f"Script de refresh manquant: {self.refresh_script}. Veuillez exécuter install.py")

    def _log_config(self) -> None:
        """Log la configuration actuelle (sans données sensibles)."""
        logger.debug("📋 Configuration:")
        logger.debug(f"  - Langue: {self.language}")
        logger.debug(f"  - Domaine Amazon: {self.amazon_domain}")
        logger.debug(f"  - Domaine Alexa: {self.alexa_domain}")
        logger.debug(f"  - Répertoire temp: {self.tmp_dir}")
        logger.debug(f"  - Timeout API: {self.api_timeout_seconds}s")
        logger.debug(f"  - Max retries: {self.api_max_retries}")

    def get_api_base_url(self) -> str:
        """Retourne l'URL de base de l'API Alexa."""
        return f"https://{self.alexa_domain}"

    def get_amazon_base_url(self) -> str:
        """Retourne l'URL de base d'Amazon."""
        return f"https://www.{self.amazon_domain}"
