"""
Modèles de commandes pour contrôle des devices Alexa.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class CommandAction(str, Enum):
    """Actions disponibles pour les commandes."""

    # Power
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"

    # Brightness
    SET_BRIGHTNESS = "SET_BRIGHTNESS"
    INCREASE_BRIGHTNESS = "INCREASE_BRIGHTNESS"
    DECREASE_BRIGHTNESS = "DECREASE_BRIGHTNESS"

    # Color
    SET_COLOR = "SET_COLOR"
    SET_COLOR_RGB = "SET_COLOR_RGB"
    SET_COLOR_TEMPERATURE = "SET_COLOR_TEMPERATURE"

    # Volume
    SET_VOLUME = "SET_VOLUME"
    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    MUTE = "MUTE"
    UNMUTE = "UNMUTE"

    # Playback
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    STOP = "STOP"
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"

    # Temperature
    SET_TEMPERATURE = "SET_TEMPERATURE"
    INCREASE_TEMPERATURE = "INCREASE_TEMPERATURE"
    DECREASE_TEMPERATURE = "DECREASE_TEMPERATURE"


class DeviceCommand:
    """Commande pour contrôler un device."""

    def __init__(self, device_id: str, action: CommandAction, parameters: Optional[Dict[str, Any]] = None):
        self.device_id = device_id
        self.action = action
        self.parameters = parameters or {}
        self.timestamp = datetime.now()

    def to_alexa_format(self) -> Dict[str, Any]:
        """
        Convertit la commande au format attendu par /api/np/command.

        Returns:
            Dictionnaire au format Alexa
        """
        return {
            "deviceId": self.device_id,
            "action": self.action.value,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat(),
        }


class CommandResult:
    """Résultat d'exécution d'une commande."""

    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.success = success
        self.message = message
        self.data = data
        self.error_code = error_code
        self.timestamp = datetime.now()

    @classmethod
    def success_result(cls, message: str, data: Optional[Dict[str, Any]] = None) -> "CommandResult":
        """Factory pour créer un résultat de succès."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_result(cls, message: str, error_code: str, data: Optional[Dict[str, Any]] = None) -> "CommandResult":
        """Factory pour créer un résultat d'erreur."""
        return cls(success=False, message=message, error_code=error_code, data=data)
