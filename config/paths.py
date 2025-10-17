"""
Chemins centralisés de l'application.

Ce module contient toutes les fonctions pour obtenir les chemins :
- Dossier de configuration (~/.alexa/)
- Sous-dossiers (auth, data, logs, cache)
- Fichiers spécifiques (tokens, cookies, etc.)

Utilise pathlib.Path pour compatibilité cross-platform.
"""

from pathlib import Path
from typing import Optional


class AppPaths:
    """Gestionnaire centralisé des chemins de l'application."""

    @staticmethod
    def get_config_dir() -> Path:
        """
        Retourne le dossier de configuration principal.

        Returns:
            Path: ~/.alexa/

        Note:
            Crée le dossier s'il n'existe pas.
        """
        config_dir = Path.home() / ".alexa"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @staticmethod
    def get_auth_dir() -> Path:
        """
        Retourne le dossier d'authentification.

        Returns:
            Path: ~/.alexa/auth/
        """
        auth_dir = AppPaths.get_config_dir() / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)
        return auth_dir

    @staticmethod
    def get_data_dir() -> Path:
        """
        Retourne le dossier de données.

        Returns:
            Path: ~/.alexa/data/
        """
        data_dir = AppPaths.get_config_dir() / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @staticmethod
    def get_logs_dir() -> Path:
        """
        Retourne le dossier de logs.

        Returns:
            Path: ~/.alexa/logs/
        """
        logs_dir = AppPaths.get_config_dir() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    @staticmethod
    def get_cache_dir() -> Path:
        """
        Retourne le dossier de cache.

        Returns:
            Path: ~/.alexa/cache/
        """
        cache_dir = AppPaths.get_config_dir() / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @staticmethod
    def get_temp_dir() -> Path:
        """
        Retourne le dossier temporaire selon la plateforme.

        Returns:
            Path: /tmp/.alexa/ sur Unix, %TEMP%\\.alexa\\ sur Windows
        """
        import platform
        import tempfile

        temp_base = Path(tempfile.gettempdir()) if platform.system() == "Windows" else Path("/tmp")

        temp_dir = temp_base / ".alexa"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    # === FICHIERS SPÉCIFIQUES ===

    @staticmethod
    def get_token_file() -> Path:
        """Retourne le chemin du fichier de tokens."""
        return AppPaths.get_auth_dir() / "cookie-resultat.json"

    @staticmethod
    def get_cookie_file() -> Path:
        """Retourne le chemin du fichier de cookies."""
        return AppPaths.get_temp_dir() / ".alexa.cookie"

    @staticmethod
    def get_device_list_file() -> Path:
        """Retourne le chemin du cache de la liste des appareils."""
        return AppPaths.get_temp_dir() / ".alexa.devicelist"

    @staticmethod
    def get_favorites_file() -> Path:
        """Retourne le chemin du fichier de favoris."""
        return AppPaths.get_data_dir() / "favorites.json"

    @staticmethod
    def get_scenarios_file() -> Path:
        """Retourne le chemin du fichier de scénarios."""
        return AppPaths.get_data_dir() / "scenarios.json"

    @staticmethod
    def get_multiroom_file() -> Path:
        """Retourne le chemin du fichier de groupes multiroom."""
        return AppPaths.get_data_dir() / "multiroom.json"

    @staticmethod
    def get_log_file(name: str = "alexa") -> Path:
        """
        Retourne le chemin d'un fichier de log.

        Args:
            name: Nom du fichier (sans extension)

        Returns:
            Path: ~/.alexa/logs/{name}.log
        """
        return AppPaths.get_logs_dir() / f"{name}.log"

    @staticmethod
    def get_cache_file(name: str) -> Path:
        """
        Retourne le chemin d'un fichier de cache.

        Args:
            name: Nom du fichier (avec extension)

        Returns:
            Path: ~/.alexa/cache/{name}
        """
        return AppPaths.get_cache_dir() / name

    # === CHEMINS PROJET ===

    @staticmethod
    def get_project_root() -> Path:
        """
        Retourne le dossier racine du projet.

        Returns:
            Path: Chemin absolu vers la racine du projet
        """
        # Remonte depuis config/ vers la racine
        return Path(__file__).parent.parent.absolute()

    @staticmethod
    def get_alexa_auth_dir() -> Path:
        """
        Retourne le dossier alexa_auth du projet.

        Returns:
            Path: {project_root}/alexa_auth/
        """
        return AppPaths.get_project_root() / "alexa_auth"

    @staticmethod
    def get_nodejs_dir() -> Path:
        """
        Retourne le dossier nodejs du projet.

        Returns:
            Path: {project_root}/alexa_auth/nodejs/
        """
        return AppPaths.get_alexa_auth_dir() / "nodejs"

    @staticmethod
    def get_refresh_script() -> Path:
        """
        Retourne le chemin du script de refresh des tokens.

        Returns:
            Path: {project_root}/alexa_auth/nodejs/auth-refresh.js
        """
        return AppPaths.get_nodejs_dir() / "auth-refresh.js"

    @staticmethod
    def get_custom_path(relative_path: str, base_dir: Optional[Path] = None) -> Path:
        """
        Retourne un chemin personnalisé.

        Args:
            relative_path: Chemin relatif
            base_dir: Dossier de base (défaut: config_dir)

        Returns:
            Path: Chemin complet

        Example:
            >>> path = AppPaths.get_custom_path("my_data/file.json")
            >>> print(path)
            /home/user/.alexa/my_data/file.json
        """
        base = base_dir or AppPaths.get_config_dir()
        full_path = base / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path
