#!/usr/bin/env python3

"""
Logging utilities for Alexa Advanced Control

Système de logging centralisé avec emojis et niveaux personnalisés.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def setup_loguru_logger(
    log_file: Optional[Path] = None,
    console_level: str = "INFO",
    file_level: str = "DEBUG"
) -> None:
    """
    Configure le logger loguru avec niveaux personnalisés et emojis.

    Args:
        log_file: Chemin du fichier de log (optionnel)
        console_level: Niveau pour la console (DEBUG, INFO, WARNING, ERROR)
        file_level: Niveau pour le fichier (DEBUG, INFO, WARNING, ERROR)
    """
    # Supprimer tous les handlers existants
    logger.remove()

    # Format pour la console avec emojis et couleurs
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level.icon} {level: <12}</level> | "
        "<level>{message}</level>"
    )

    # Format pour le fichier (sans couleurs ANSI)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level.icon} {level: <12} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # Handler console
    logger.add(
        sys.stdout,
        format=console_format,
        level=console_level,
        colorize=True,
        filter=lambda record: record["level"].name not in ["DEBUG"] or console_level == "DEBUG"
    )

    # Handler fichier (optionnel)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                log_file,
                format=file_format,
                level=file_level,
                rotation="10 MB",
                retention="1 week",
                encoding="utf-8"
            )
        except Exception as e:
            logger.warning(f"Impossible de créer le fichier de log {log_file}: {e}")

    # Niveaux personnalisés avec emojis (seulement s'ils n'existent pas déjà)
    try:
        logger.level("INIT", no=25, icon="🔧", color="<cyan>")
    except ValueError:
        pass  # Niveau déjà défini
    try:
        logger.level("PROCESS", no=26, icon="⚙️ ", color="<blue>")
    except ValueError:
        pass
    try:
        logger.level("CONFIG", no=27, icon="🔧", color="<cyan>")
    except ValueError:
        pass
    try:
        logger.level("CLEANUP", no=28, icon="🧹", color="<yellow>")
    except ValueError:
        pass
    try:
        logger.level("CACHE", no=29, icon="💾", color="<magenta>")
    except ValueError:
        pass
    try:
        logger.level("AUTH", no=30, icon="🔐", color="<green>")
    except ValueError:
        pass
    try:
        logger.level("DEVICE", no=31, icon="📱", color="<blue>")
    except ValueError:
        pass
    try:
        logger.level("MUSIC", no=32, icon="🎵", color="<magenta>")
    except ValueError:
        pass
    try:
        logger.level("TIMER", no=33, icon="⏰", color="<yellow>")
    except ValueError:
        pass
    try:
        logger.level("VOICE", no=34, icon="🎤", color="<cyan>")
    except ValueError:
        pass
    try:
        logger.level("ALARM", no=35, icon="⏰", color="<red>")
    except ValueError:
        pass
    try:
        logger.level("CALENDAR", no=36, icon="📅", color="<green>")
    except ValueError:
        pass
    try:
        logger.level("ROUTINE", no=37, icon="🔄", color="<blue>")
    except ValueError:
        pass
    try:
        logger.level("LIST", no=38, icon="📝", color="<yellow>")
    except ValueError:
        pass
    try:
        logger.level("REMINDER", no=39, icon="📌", color="<magenta>")
    except ValueError:
        pass
    try:
        logger.level("DND", no=40, icon="🔕", color="<red>")
    except ValueError:
        pass
    try:
        logger.level("MULTIROOM", no=41, icon="🔊", color="<cyan>")
    except ValueError:
        pass
    try:
        logger.level("ANNOUNCEMENT", no=42, icon="📢", color="<yellow>")
    except ValueError:
        pass
    try:
        logger.level("ACTIVITY", no=43, icon="📊", color="<blue>")
    except ValueError:
        pass
    try:
        logger.level("NOTIFICATION", no=44, icon="🔔", color="<magenta>")
    except ValueError:
        pass
    try:
        logger.level("SETTINGS", no=45, icon="⚙️ ", color="<cyan>")
    except ValueError:
        pass
    try:
        logger.level("SMART_HOME", no=46, icon="🏠", color="<green>")
    except ValueError:
        pass
    try:
        logger.level("BLUETOOTH", no=47, icon="🎧", color="<blue>")
    except ValueError:
        pass
    try:
        logger.level("EQUALIZER", no=48, icon="🎚️", color="<magenta>")
    except ValueError:
        pass
    try:
        logger.level("TUNEIN", no=49, icon="📻", color="<cyan>")
    except ValueError:
        pass

    # Ajustements pour l'alignement visuel des emojis
    # Certains emojis prennent plus de place visuellement
    try:
        logger.level("INFO", icon="ℹ️ ", color="<blue>")  # Plus large
    except ValueError:
        pass
    try:
        logger.level("WARNING", icon="⚠️ ", color="<yellow>")  # Plus large
    except ValueError:
        pass
    try:
        logger.level("SUCCESS", icon="✅ ", color="<green>")  # Plus large
    except ValueError:
        pass
    try:
        logger.level("VOICE", icon="🎤", color="<cyan>")  # Plus large
    except ValueError:
        pass

    logger.info("Initialisation du système de logging")
    logger.success("Système de logging initialisé avec succès")


def get_logger(name: str = "alexa"):
    """
    Retourne une instance du logger configuré.

    Args:
        name: Nom du logger (pour identification dans les logs)

    Returns:
        Logger loguru configuré
    """
    return logger.bind(name=name)


# Configuration par défaut au premier import
setup_loguru_logger()
