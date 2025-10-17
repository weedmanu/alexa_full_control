"""
Base class pour toutes les sous-commandes (SubCommand).

Consolidates common methods used by playback, library, tunein, alarms, reminders, timers.

Auteur: M@nu
Date: 17 octobre 2025
"""

from typing import Any, Callable, Optional, Tuple

from loguru import logger


class BaseSubCommand:
    """
    Classe de base pour toutes les sous-commandes.

    Consolidates common methods:
    - Device info retrieval (serial, type)
    - Logging (error, success, info, warning, debug)
    - Circuit breaker calls
    - Media owner ID retrieval

    Usage:
        class PlaybackCommands(BaseSubCommand):
            def pause(self, args):
                device_info = self.get_device_info(args.device)
                if not device_info:
                    return False
                serial, device_type = device_info
                # ... rest of logic
    """

    def __init__(self):
        """Initialise la sous-commande."""
        self.context = None
        self.logger = logger

    # ========================================================================
    # LOGGING
    # ========================================================================

    def error(self, message: str) -> None:
        """Affiche un message d'erreur."""
        self.logger.error(message)

    def success(self, message: str) -> None:
        """Affiche un message de succès."""
        self.logger.success(message)

    def info(self, message: str) -> None:
        """Affiche un message d'information."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Affiche un message d'avertissement."""
        self.logger.warning(message)

    def debug(self, message: str) -> None:
        """Affiche un message de debug."""
        self.logger.debug(message)

    # ========================================================================
    # DEVICE UTILITIES
    # ========================================================================

    def get_device_serial(self, device_name: str) -> Optional[str]:
        """
        Récupère le serial d'un appareil par son nom.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Serial de l'appareil ou None
        """
        ctx = getattr(self, "context", None)
        if ctx is None or getattr(ctx, "device_mgr", None) is None:
            return None

        devices = ctx.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                serial = device.get("serialNumber")
                return str(serial) if serial is not None else None

        return None

    def get_device_type(self, device_name: str) -> str:
        """
        Récupère le type d'appareil.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Type d'appareil (défaut: ECHO)
        """
        ctx = getattr(self, "context", None)
        if ctx is None or getattr(ctx, "device_mgr", None) is None:
            return "ECHO"

        devices = ctx.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                device_type = device.get("deviceType", "ECHO")
                return str(device_type) if device_type is not None else "ECHO"

        return "ECHO"

    def get_device_info(self, device_name: str) -> Optional[Tuple[str, str]]:
        """
        Récupère le serial et le type d'un appareil.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Tuple (serial, device_type) ou None si non trouvé
        """
        serial = self.get_device_serial(device_name)
        if not serial:
            return None

        device_type = self.get_device_type(device_name)
        return (serial, device_type)

    def get_parent_multiroom(self, device_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Récupère l'appareil parent multiroom si applicable.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Tuple (parent_id, parent_type) ou (None, None)
        """
        ctx = getattr(self, "context", None)
        if ctx is None or getattr(ctx, "device_mgr", None) is None:
            return (None, None)

        devices = ctx.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                clusters = device.get("parentClusters", [])
                if clusters:
                    parent_id = clusters[0]
                    for parent_dev in devices:
                        if parent_dev.get("serialNumber") == parent_id:
                            return (parent_id, parent_dev.get("deviceType"))
                break

        return (None, None)

    # ========================================================================
    # CIRCUIT BREAKER
    # ========================================================================

    def call_with_breaker(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Appelle une fonction via le circuit breaker si disponible.

        Args:
            func: Fonction à appeler
            *args: Arguments positionnels
            **kwargs: Arguments nommés

        Returns:
            Résultat de la fonction
        """
        ctx = getattr(self, "context", None)
        if ctx and getattr(ctx, "breaker", None):
            return ctx.breaker.call(func, *args, **kwargs)
        return func(*args, **kwargs)

    # ========================================================================
    # AUTH/MEDIA
    # ========================================================================

    def get_media_owner_id(self) -> str:
        """
        Récupère le media owner customer ID.

        Returns:
            Customer ID ou chaîne vide
        """
        ctx = getattr(self, "context", None)
        if ctx and getattr(ctx, "auth", None):
            return getattr(ctx.auth, "customer_id", "")
        return ""

    # ========================================================================
    # DURATION UTILITIES (for timers, alarms, reminders)
    # ========================================================================

    def parse_duration(self, duration_str: str) -> Optional[int]:
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
        import re

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

    def format_duration(self, seconds: int) -> str:
        """
        Formate une durée en secondes en texte lisible.

        Args:
            seconds: Durée en secondes

        Returns:
            Texte formaté (ex: "1h 30m", "45m", "2h")
        """
        from datetime import timedelta

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

    # ------------------------------------------------------------------
    # Compatibility aliases (historical names used by CLI commands)
    # ------------------------------------------------------------------
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        return self.parse_duration(duration_str)

    def _format_duration(self, seconds: int) -> str:
        return self.format_duration(seconds)

    def _get_device_type(self, device_name: str) -> str:
        return self.get_device_type(device_name)
