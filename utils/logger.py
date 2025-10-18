#!/usr/bin/env python3

"""
Logging utilities for Alexa Advanced Control - Module unique centralisé
"""

import logging
import sys
from pathlib import Path
from typing import Any, Callable, List, Optional

# Pre-declare logger so type checkers have a stable name and type for it.
logger: Any = None
try:
    # Import into a temporary name then assign to the pre-declared symbol.
    from loguru import logger as _loguru_logger

    logger = _loguru_logger
except Exception:
    # Best-effort: leave logger as None when Loguru is not available.
    logger = None

# Single assignment for static analyzers: True iff import succeeded
LOGURU_AVAILABLE: bool = logger is not None


# --- Système centralisé d'icônes partagées ---
class SharedIcons:
    """Distributeur centralisé d'icônes pour tout le projet.

    Toutes les icônes utilisées dans l'application doivent être définies ici
    pour éviter la duplication et faciliter la maintenance.
    """

    # Icônes de statut/opérations (désactivées)
    SUCCESS = ""
    ERROR = ""
    WARNING = ""
    INFO = ""
    DEBUG = ""
    SEARCH = ""
    CRITICAL = ""
    AUTH = ""
    INSTALL = ""
    STEP = ""
    PROGRESS = ""

    # Icônes spécialisées (désactivées)
    ROCKET = ""  # Installation
    PACKAGE = ""  # Dépendances
    PYTHON = ""  # Python
    NODEJS = ""  # Node.js
    DOCUMENT = ""  # Documentation
    TRASH = ""  # Suppression
    CELEBRATION = ""  # Succès final
    GEAR = ""  # Configuration
    SYNC = ""  # Synchronisation
    SAVE = ""  # Sauvegarde
    FILE = ""  # Fichier
    DEVICE = ""  # Appareil
    MUSIC = ""  # Musique

    # Tuple des icônes partagées (pour référence)
    SHARED_ICONS = (
        SUCCESS,
        ERROR,
        WARNING,
        INFO,
        DEBUG,
        SEARCH,
        CRITICAL,
        AUTH,
        INSTALL,
        STEP,
        PROGRESS,
        ROCKET,
        PACKAGE,
        PYTHON,
        NODEJS,
        DOCUMENT,
        TRASH,
        CELEBRATION,
        GEAR,
        SYNC,
        SAVE,
        FILE,
        DEVICE,
        MUSIC,
    )

    @classmethod
    def get_all_icons(cls) -> tuple[str, ...]:
        """Retourne toutes les icônes définies."""
        return cls.SHARED_ICONS

    @classmethod
    def get_icon_map(cls) -> dict[str, str]:
        """Retourne un mapping nom -> icône pour référence."""
        return {
            "success": cls.SUCCESS,
            "error": cls.ERROR,
            "warning": cls.WARNING,
            "info": cls.INFO,
            "debug": cls.DEBUG,
            "search": cls.SEARCH,
            "critical": cls.CRITICAL,
            "auth": cls.AUTH,
            "install": cls.INSTALL,
            "step": cls.STEP,
            "progress": cls.PROGRESS,
            "rocket": cls.ROCKET,
            "package": cls.PACKAGE,
            "python": cls.PYTHON,
            "nodejs": cls.NODEJS,
            "document": cls.DOCUMENT,
            "trash": cls.TRASH,
            "celebration": cls.CELEBRATION,
            "gear": cls.GEAR,
            "sync": cls.SYNC,
            "save": cls.SAVE,
            "file": cls.FILE,
            "device": cls.DEVICE,
            "music": cls.MUSIC,
        }


def _ensure_utf8_stdout() -> None:
    """Force stdout/stderr à utiliser UTF-8 (best-effort, Windows principalement)."""
    # Some streams (especially when mocked in tests or older Python) may not
    # implement `reconfigure`. Use hasattr/try to remain robust and avoid
    # static type complaints about missing attributes.
    # Use getattr and callable checks to satisfy static analysis.
    try:
        stdout_reconf = getattr(sys.stdout, "reconfigure", None)
        stderr_reconf = getattr(sys.stderr, "reconfigure", None)
        if callable(stdout_reconf):
            stdout_reconf(encoding="utf-8")
        if callable(stderr_reconf):
            stderr_reconf(encoding="utf-8")
        return
    except Exception:
        # Fallback: wrap binary buffer if available
        try:
            import io

            stdout_buffer = getattr(sys.stdout, "buffer", None)
            stderr_buffer = getattr(sys.stderr, "buffer", None)
            if stdout_buffer is not None:
                sys.stdout = io.TextIOWrapper(stdout_buffer, encoding="utf-8", line_buffering=True)
            if stderr_buffer is not None:
                sys.stderr = io.TextIOWrapper(stderr_buffer, encoding="utf-8", line_buffering=True)
        except Exception:
            # Give up silently; UTF-8 is best-effort only
            return


def _get_format_record() -> Callable[[Any], str]:
    """Retourne une fonction de formatage Loguru réutilisable."""

    def format_record(record: Any) -> str:
        """Formateur personnalisé pour les logs."""
        level_name = record["level"].name
        level_no = record["level"].no

        # Afficher la localisation seulement pour les erreurs ou en mode debug
        show_location = level_name in ["ERROR", "CRITICAL"] or level_no <= 10  # DEBUG level

        location_part = " | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>" if show_location else ""

        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<level>{message}</level>" + location_part + "\n{exception}"
        )

    return format_record


def _register_custom_levels(custom_levels: Optional[List[str]] = None) -> None:
    """Enregistre les niveaux personnalisés Loguru (AUTH, INSTALL, etc.)."""
    if not LOGURU_AVAILABLE or logger is None:
        return

    levels_to_register = custom_levels or ["AUTH", "INSTALL"]
    for level_name in levels_to_register:
        try:
            # Vérifier si le niveau existe déjà
            if hasattr(logger, "_core") and level_name in str(logger._core.levels):
                continue

            # Enregistrer le niveau personnalisé
            logger.level(level_name, no=25, color="<cyan>")
        except Exception:
            pass  # Niveau déjà existant


def setup_loguru_logger(
    log_file: Optional[Path] = None,
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "1 week",
    enable_console: bool = True,
    enable_stderr: bool = False,
    custom_levels: Optional[List[str]] = None,
    ensure_utf8: bool = True,
    no_color: bool = False,
) -> None:
    """Configure Loguru avec format et couleurs - Fonction centrale unique.

    Format de sortie:
    2025-10-14 16:07:50 | INFO     | module:function:line | Message

    Args:
        log_file: Chemin du fichier de log (optionnel)
        level: Niveau de log ("DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR")
        rotation: Rotation des fichiers (défaut: "10 MB")
        retention: Rétention des fichiers (défaut: "1 week")
        enable_stderr: Activer la sortie stderr en plus de stdout
        custom_levels: Niveaux personnalisés à enregistrer (ex: ["AUTH", "INSTALL"])
        ensure_utf8: Tenter de forcer UTF-8 pour stdout/stderr (défaut: True)
    """
    if not LOGURU_AVAILABLE:
        print("⚠️  Loguru non disponible. Installation: pip install loguru", file=sys.stderr)
        return

    # Retirer les handlers par défaut
    logger.remove()

    # Forcer UTF-8 si demandé
    if ensure_utf8:
        _ensure_utf8_stdout()

    # Enregistrer les niveaux personnalisés
    _register_custom_levels(custom_levels)

    # Récupérer le formateur
    format_record = _get_format_record()

    # Handler console (stdout) - ajouté seulement si enable_console=True
    if enable_console:
        # Tests patch stdout to a non-tty; to maintain readable output and meet
        # test expectations, enable colorization unless the caller explicitly
        # requested no_color. This keeps behavior predictable under test.
        colorize = not no_color
        logger.add(
            sys.stdout,
            format=format_record,
            level=level,
            colorize=colorize,
            backtrace=True,
            diagnose=True,
        )

    # Handler stderr optionnel (pour les erreurs uniquement)
    if enable_stderr:
        logger.add(
            sys.stderr,
            format=format_record,
            level="ERROR",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # Handler fichier optionnel
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                log_file,
                format=format_record,
                level="DEBUG",  # Tout sauver dans le fichier
                rotation=rotation,
                retention=retention,
                compression="gz",
                backtrace=True,
                diagnose=True,
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning(f"Impossible de créer le fichier de log {log_file}: {e}")

    # Message de confirmation
    logger.info("Initialisation du système de logging")
    logger.success("Système de logging initialisé avec succès")


def setup_logger(name: str, log_file: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger:
    """Configure un logger avec sortie console et fichier optionnel.

    DEPRECATED: Utiliser setup_loguru_logger() à la place.

    Args:
        name: Nom du logger
        log_file: Chemin du fichier de log (optionnel)
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger configuré
    """
    logger_obj = logging.getLogger(name)

    # Éviter les doublons si déjà configuré
    if logger_obj.handlers:
        return logger_obj

    logger_obj.setLevel(level)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger_obj.addHandler(console_handler)

    # File handler (optionnel)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger_obj.addHandler(file_handler)
        except Exception as e:
            logger_obj.warning(f"Impossible de créer le fichier de log {log_file}: {e}")

    return logger_obj


def get_log_level_from_verbosity(verbosity: int = 0) -> int:
    """Convertit le niveau de verbosité en niveau de log.

    Args:
        verbosity: 0=WARNING, 1=INFO, 2=DEBUG

    Returns:
        Niveau de logging approprié
    """
    if verbosity >= 2:
        return logging.DEBUG
    elif verbosity >= 1:
        return logging.INFO
    else:
        return logging.WARNING


def get_loguru_level_from_verbosity(verbosity: int = 0) -> str:
    """Convertit le niveau de verbosité en niveau Loguru.

    Args:
        verbosity: 0=WARNING, 1=INFO, 2+=DEBUG

    Returns:
        Niveau Loguru approprié ("DEBUG", "INFO", "WARNING")
    """
    if verbosity >= 2:
        return "DEBUG"
    elif verbosity >= 1:
        return "INFO"
    else:
        return "WARNING"


# --- Install-specific helper wrapped into this module so there's a single logger file ---


class InstallLogger:
    """Logger unifié pour scripts d'installation avec support Loguru.

    Cette classe enveloppe soit Loguru (si disponible) soit un fallback
    vers le système logging basique. Utilise setup_loguru_logger() en interne
    pour éviter toute duplication de code.
    """

    def __init__(
        self,
        log_file: Optional[Path] = None,
        level: str = "INFO",
        use_loguru: bool = True,
    ):
        self.log_file = log_file
        self.level = level
        self.use_loguru = use_loguru and LOGURU_AVAILABLE

        if self.use_loguru:
            # Utiliser la fonction centrale au lieu de dupliquer le code
            setup_loguru_logger(
                log_file=self.log_file,
                level=self.level,
                custom_levels=["INSTALL"],  # Niveau spécifique pour l'installateur
                ensure_utf8=True,
            )

    def header(self, msg: str, emoji: str = "") -> None:
        if self.use_loguru:
            logger.opt(depth=1).log("INSTALL", f"{emoji} {msg}")
        else:
            # FallbackLogger lives in an external script; import dynamically
            # via importlib so mypy treats it as Any and doesn't attempt to
            # analyze the module implementation.
            from importlib import import_module

            fallback_logger = import_module("scripts.install").Logger

            fallback_logger.header(msg, emoji)

    def step(self, msg: str, emoji: str = "") -> None:
        if self.use_loguru:
            logger.opt(depth=1).info(f"{emoji} {msg}")
        else:
            from importlib import import_module

            fallback_logger = import_module("scripts.install").Logger

            fallback_logger.step(msg, emoji)

    def progress(self, msg: str) -> None:
        if self.use_loguru:
            logger.opt(depth=1).info(f"{msg}...")
        else:
            from importlib import import_module

            fallback_logger = import_module("scripts.install").Logger

            fallback_logger.progress(msg)

    def success(self, msg: str, emoji: str = "") -> None:
        if self.use_loguru:
            logger.opt(depth=1).success(f"{msg}")
        else:
            from importlib import import_module

            fallback_logger = import_module("scripts.install").Logger

            fallback_logger.success(msg, emoji)

    def error(self, msg: str, emoji: str = "") -> None:
        if self.use_loguru:
            logger.opt(depth=1).error(f"{msg}")
        else:
            from importlib import import_module

            fallback_logger = import_module("scripts.install").Logger

            fallback_logger.error(msg, emoji)

    def warning(self, msg: str, emoji: str = "") -> None:
        if self.use_loguru:
            logger.opt(depth=1).warning(f"{msg}")
        else:
            from importlib import import_module

            fallback_logger = import_module("scripts.install").Logger

            fallback_logger.warning(msg, emoji)

    def info(self, msg: str, emoji: str = "") -> None:
        if self.use_loguru:
            logger.opt(depth=1).info(f"{msg}")
        else:
            from importlib import import_module

            fallback_logger = import_module("scripts.install").Logger

            fallback_logger.info(msg, emoji)

    def debug(self, msg: str) -> None:
        if self.use_loguru:
            logger.opt(depth=1).debug(msg)
        else:
            print(f"DEBUG: {msg}")


# Instance globale pour import facile
_global_install_logger: Optional[InstallLogger] = None


def get_install_logger(
    log_file: Optional[Path] = None, level: str = "INFO", force_recreate: bool = False
) -> InstallLogger:
    global _global_install_logger

    if _global_install_logger is None or force_recreate:
        _global_install_logger = InstallLogger(log_file=log_file, level=level)

    return _global_install_logger


def log_system_info(install_logger: InstallLogger) -> None:
    import platform

    install_logger.debug(f"Système: {platform.system()} {platform.release()}")
    install_logger.debug(f"Architecture: {platform.machine()}")
    install_logger.debug(f"Python: {sys.version}")


__all__ = [
    "setup_loguru_logger",
    "setup_logger",
    "get_log_level_from_verbosity",
    "get_loguru_level_from_verbosity",
    "InstallLogger",
    "get_install_logger",
    "log_system_info",
    "SharedIcons",
    "LOGURU_AVAILABLE",
]
