"""
Classe de base pour les sous-commandes de gestion du temps.

Auteur: M@nu
Date: 8 octobre 2025
"""

import re
from datetime import timedelta
from typing import Optional

from loguru import logger


class TimeSubCommand:
    """
    Classe de base pour les sous-commandes de gestion du temps.

    Fournit des utilitaires communs pour timer, alarm, reminder.
    """

    def __init__(self):
        """Initialise la sous-commande."""
        self.context = None
        self.logger = logger

    def get_device_serial(self, device_name: str) -> Optional[str]:
        """
        Récupère le serial d'un appareil par son nom.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Serial de l'appareil ou None
        """
        if self.context is None or self.context.device_mgr is None:
            return None

        devices = self.context.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                return device.get("serialNumber")

        return None

    def error(self, message: str):
        """Affiche un message d'erreur."""
        self.logger.error(message)

    def success(self, message: str):
        """Affiche un message de succès."""
        self.logger.success(message)

    def info(self, message: str):
        """Affiche un message d'information."""
        self.logger.info(message)

    def warning(self, message: str):
        """Affiche un message d'avertissement."""
        self.logger.warning(message)

    def debug(self, message: str):
        """Affiche un message de debug."""
        self.logger.debug(message)

    def _get_device_type(self, device_name: str) -> str:
        """
        Récupère le type d'appareil.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Type d'appareil (ex: "ECHO")
        """
        if self.context is None or self.context.device_mgr is None:
            return "ECHO"

        devices = self.context.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                return device.get("deviceType", "ECHO")

        return "ECHO"

    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """
        Parse une chaîne de durée en secondes.

        Formats acceptés:
        - 10m, 1h30m, 2h, 90s
        - '1 minute', '2 heures', '1 heure 30 minutes'

        Args:
            duration_str: Chaîne de durée

        Returns:
            Durée en secondes ou None si format invalide
        """
        duration_str = duration_str.strip().lower()
        total_seconds = 0

        # Format compact: 1h30m, 10m, 2h, 90s
        compact_pattern = r"(\d+)\s*([hms])"
        matches = re.findall(compact_pattern, duration_str)

        if matches:
            for value, unit in matches:
                value = int(value)
                if unit == "h":
                    total_seconds += value * 3600
                elif unit == "m":
                    total_seconds += value * 60
                elif unit == "s":
                    total_seconds += value
            return total_seconds if total_seconds > 0 else None

        # Format texte: '1 heure 30 minutes', '2 heures', etc.
        text_pattern = r"(\d+)\s*(heure|heures|minute|minutes|seconde|secondes|h|m|s)"
        matches = re.findall(text_pattern, duration_str)

        if matches:
            for value, unit in matches:
                value = int(value)
                if unit in ["heure", "heures", "h"]:
                    total_seconds += value * 3600
                elif unit in ["minute", "minutes", "m"]:
                    total_seconds += value * 60
                elif unit in ["seconde", "secondes", "s"]:
                    total_seconds += value
            return total_seconds if total_seconds > 0 else None

        # Format numérique pur (supposé être en minutes)
        try:
            minutes = int(duration_str)
            return minutes * 60 if minutes > 0 else None
        except ValueError:
            pass

        return None

    def _format_duration(self, seconds: int) -> str:
        """
        Formate une durée en secondes en texte lisible.

        Args:
            seconds: Durée en secondes

        Returns:
            Texte formaté (ex: "1h 30m", "45m", "2h")
        """
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds_remainder = divmod(remainder, 60)

        parts = []
        if td.days > 0:
            parts.append(f"{td.days}j")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds_remainder > 0 and not parts:  # Afficher secondes seulement si < 1 minute
            parts.append(f"{seconds_remainder}s")

        return " ".join(parts) if parts else "0s"

    def call_with_breaker(self, func, *args, **kwargs):
        """
        Appelle une fonction avec le circuit breaker.

        Args:
            func: Fonction à appeler
            *args: Arguments positionnels
            **kwargs: Arguments nommés

        Returns:
            Résultat de la fonction
        """
        if self.context and hasattr(self.context, "breaker"):
            return self.context.breaker.call(func, *args, **kwargs)
        return func(*args, **kwargs)
