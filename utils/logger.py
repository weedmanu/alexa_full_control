#!/usr/bin/env python3

"""
Logging utilities for Alexa Advanced Control
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str, log_file: Optional[Path] = None, level: int = logging.INFO
) -> logging.Logger:
    """Configure un logger avec sortie console et fichier optionnel.

    Args:
        name: Nom du logger
        log_file: Chemin du fichier de log (optionnel)
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)

    # Éviter les doublons si déjà configuré
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optionnel)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Impossible de créer le fichier de log {log_file}: {e}")

    return logger


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
