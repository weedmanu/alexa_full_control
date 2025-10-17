"""
Example CLI Command Implementation using ManagerCommand Template.

This module demonstrates how to create concrete command implementations
using the ManagerCommand base class.
"""

from typing import Any, Dict

from cli.command_template import ManagerCommand
from core.di_container import DIContainer
from core.exceptions import ValidationError


class PlaybackPlayCommand(ManagerCommand):
    """
    Command to start playback on a device.

    Usage:
        playback play --device DEVICE_SERIAL
    """

    def __init__(self, di_container: DIContainer) -> None:
        """Initialize playback play command."""
        super().__init__("playback", di_container)

    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate that device parameter is provided.

        Args:
            params: Command parameters

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if "device" not in params:
            raise ValidationError("Device serial is required")

        if not isinstance(params["device"], str):
            raise ValidationError("Device must be a string")

        if len(params["device"]) == 0:
            raise ValidationError("Device serial cannot be empty")

        return True

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute playback play command.

        Args:
            params: Validated parameters with 'device' key

        Returns:
            Result dictionary with success status
        """
        try:
            device = params["device"]
            manager = self.get_manager("playback_manager")

            result = await manager.play(device_serial=device)

            return {"success": True, "data": result, "formatted": f"Playing on device {device}"}
        except Exception as e:
            self.logger.error(f"Failed to play: {e}")
            return {"success": False, "error": str(e)}

    def help(self) -> Dict[str, Any]:
        """Generate help text for playback play command."""
        return {
            "name": "playback play",
            "description": "Start music playback on a device",
            "usage": "playback play --device DEVICE_SERIAL",
            "parameters": {
                "device": "Device serial number (required)",
                "resume": "Resume from pause point (optional, bool)",
            },
            "examples": ["playback play --device ABCD1234", "playback play --device LIVING_ROOM"],
            "errors": {
                "Device serial is required": "Use --device parameter",
                "Device not found": "Check device serial with 'device list'",
                "API Error": "Ensure device is online and connected",
            },
        }


class DeviceListCommand(ManagerCommand):
    """
    Command to list all available devices.

    Usage:
        device list
    """

    def __init__(self, di_container: DIContainer) -> None:
        """Initialize device list command."""
        super().__init__("device", di_container)

    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate device list parameters.

        For list command, no parameters required.

        Args:
            params: Command parameters (usually empty)

        Returns:
            True (always valid for list)
        """
        return True

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute device list command.

        Args:
            params: Command parameters

        Returns:
            Result dictionary with devices list
        """
        try:
            manager = self.get_manager("device_manager")
            devices = await manager.get_devices()

            formatted = f"Found {len(devices)} device(s):\n"
            for device in devices:
                formatted += f"  - {device.get('name', 'Unknown')} " f"({device.get('serial', 'N/A')})\n"

            return {"success": True, "data": devices, "formatted": formatted}
        except Exception as e:
            self.logger.error(f"Failed to list devices: {e}")
            return {"success": False, "error": str(e)}

    def help(self) -> Dict[str, Any]:
        """Generate help text for device list command."""
        return {
            "name": "device list",
            "description": "List all available Alexa devices",
            "usage": "device list",
            "parameters": {},
            "examples": ["device list"],
            "errors": {"API Error": "Check your authentication or internet connection"},
        }


class AlarmAddCommand(ManagerCommand):
    """
    Command to add a new alarm.

    Usage:
        alarm add 07:30 --device DEVICE_SERIAL [--recurring PATTERN]
    """

    def __init__(self, di_container: DIContainer) -> None:
        """Initialize alarm add command."""
        super().__init__("alarm", di_container)

    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate alarm parameters.

        Args:
            params: Command parameters

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if "time" not in params:
            raise ValidationError("Alarm time is required (format: HH:MM)")

        # Validate time format
        time_str = params["time"]
        try:
            hour, minute = map(int, time_str.split(":"))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError()
        except (ValueError, AttributeError):
            raise ValidationError("Invalid time format. Use HH:MM (e.g., 07:30)")

        # Validate recurring pattern if provided
        if "recurring" in params:
            valid_patterns = ["daily", "weekdays", "weekends", "weekly", "once"]
            if params["recurring"] not in valid_patterns:
                raise ValidationError(f"Invalid recurring pattern. Valid: {', '.join(valid_patterns)}")

        return True

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute alarm add command.

        Args:
            params: Validated parameters

        Returns:
            Result dictionary with created alarm info
        """
        try:
            manager = self.get_manager("alarm_manager")

            alarm_data = {
                "time": params["time"],
                "recurring": params.get("recurring", "once"),
                "label": params.get("label", "Alarm"),
            }

            result = await manager.add_alarm(**alarm_data)

            return {
                "success": True,
                "data": result,
                "formatted": f"Alarm set for {params['time']} ({alarm_data['recurring']})",
            }
        except Exception as e:
            self.logger.error(f"Failed to add alarm: {e}")
            return {"success": False, "error": str(e)}

    def help(self) -> Dict[str, Any]:
        """Generate help text for alarm add command."""
        return {
            "name": "alarm add",
            "description": "Add a new alarm",
            "usage": "alarm add HH:MM [--recurring PATTERN] [--label TEXT]",
            "parameters": {
                "time": "Alarm time in HH:MM format (required)",
                "recurring": "Pattern: daily, weekdays, weekends, weekly, once (default: once)",
                "label": "Alarm label/description (optional)",
            },
            "examples": [
                "alarm add 07:30",
                "alarm add 07:30 --recurring daily",
                "alarm add 22:00 --label Bedtime --recurring daily",
            ],
            "errors": {
                "Invalid time format": "Use HH:MM format (e.g., 07:30)",
                "Invalid recurring pattern": "Valid patterns: daily, weekdays, weekends, weekly, once",
            },
        }
