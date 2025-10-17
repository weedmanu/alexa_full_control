"""
Input Validators - Centralized input validation and sanitization.

Provides:
- Device serial validation
- Device type validation
- Alarm time validation
- Text sanitization (with JSON escaping)
- Error reporting

Usage:
    >>> serial = InputValidator.validate_device_serial("ABC123DEF456")
    >>> label = InputValidator.sanitize_text("Alarm Label", max_len=100)
"""

import re
from datetime import datetime
from typing import Any

from loguru import logger


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


class InputValidator:
    """Centralized input validation for Alexa API calls."""

    # ===Device Serial Validation===

    @staticmethod
    def validate_device_serial(serial: object) -> str:
        """
        Validate device serial number.

        Format:
        - Non-empty string
        - Length 8-50 chars
        - Only uppercase letters, numbers, and hyphens

        Args:
            serial: Device serial to validate

        Returns:
            Validated serial (same as input)

        Raises:
            ValidationError: If format invalid
        """
        if not isinstance(serial, str):
            raise ValidationError(f"device_serial must be string, got {type(serial).__name__}")

        if not serial:
            raise ValidationError("device_serial cannot be empty")

        if len(serial) < 8:
            raise ValidationError(f"device_serial too short: {len(serial)}/8 chars")

        if len(serial) > 50:
            raise ValidationError(f"device_serial too long: {len(serial)}/50 chars")

        # Only uppercase, numbers, hyphens
        if not re.match(r"^[A-Z0-9-]+$", serial):
            raise ValidationError(f"device_serial contains invalid characters: {serial}")

        logger.debug(f"Valid device_serial: {serial}")
        return serial

    # === Device Type Validation ===

    VALID_DEVICE_TYPES = {
        "ALEXA_CURRENT_DEVICE_TYPE",
        "ECHO_DOT",
        "ECHO",
        "ECHO_PLUS",
        "ECHO_SHOW",
        "ECHO_SHOW_5",
        "ECHO_SHOW_8",
        "ECHO_SPOT",
        "ECHO_AUTO",
        "FIRE_TABLET",
        "MOBILE",
    }

    @staticmethod
    def validate_device_type(device_type: object) -> str:
        """
        Validate device type.

        Args:
            device_type: Device type to validate

        Returns:
            Validated device type (same as input)

        Raises:
            ValidationError: If not in valid types list
        """
        if not isinstance(device_type, str):
            raise ValidationError(f"device_type must be string, got {type(device_type).__name__}")

        if device_type not in InputValidator.VALID_DEVICE_TYPES:
            raise ValidationError(f"device_type invalid: {device_type}. Valid: {InputValidator.VALID_DEVICE_TYPES}")

        logger.debug(f"Valid device_type: {device_type}")
        return device_type

    # === Alarm Time Validation ===

    @staticmethod
    def validate_alarm_time(alarm_time: object) -> str:
        """
        Validate alarm time.

        Formats:
        - HH:MM (24-hour format, 00:00-23:59)
        - ISO 8601 (2025-10-16T14:30:00)

        Args:
            alarm_time: Time to validate

        Returns:
            Validated time (same as input)

        Raises:
            ValidationError: If format invalid
        """
        if not isinstance(alarm_time, str):
            raise ValidationError(f"alarm_time must be string, got {type(alarm_time).__name__}")

        if not alarm_time:
            raise ValidationError("alarm_time cannot be empty")

        # Try HH:MM format
        if ":" in alarm_time:
            try:
                parts = alarm_time.split(":")
                if len(parts) != 2:
                    raise ValueError("Not HH:MM format")

                hour, minute = int(parts[0]), int(parts[1])

                if not (0 <= hour <= 23):
                    raise ValueError(f"Hour invalid: {hour}")
                if not (0 <= minute <= 59):
                    raise ValueError(f"Minute invalid: {minute}")

                logger.debug(f"Valid alarm_time HH:MM: {alarm_time}")
                return alarm_time

            except ValueError as e:
                raise ValidationError(f"alarm_time HH:MM invalid: {e}") from None

        # Try ISO 8601 format
        try:
            datetime.fromisoformat(alarm_time)
            logger.debug(f"Valid alarm_time ISO: {alarm_time}")
            return alarm_time
        except ValueError:
            raise ValidationError(f"alarm_time format invalid (expected HH:MM or ISO 8601): {alarm_time}") from None

    # === Text Sanitization ===

    @staticmethod
    def sanitize_text(text: object, max_len: int = 500) -> str:
        """
        Sanitize text for JSON encoding (labels, descriptions, etc).

        Removes:
        - Non-printable characters (except newline, tab)
        - Null bytes

        Escapes:
        - Backslashes
        - Double quotes

        Args:
            text: Text to sanitize
            max_len: Maximum length (default: 500)

        Returns:
            Sanitized text

        Raises:
            ValidationError: If invalid or too long
        """
        if not isinstance(text, str):
            raise ValidationError(f"text must be string, got {type(text).__name__}")

        if len(text) > max_len:
            raise ValidationError(f"text too long: {len(text)}/{max_len} chars")

        # Remove non-printable chars (keep newline, tab)
        text = "".join(c for c in text if c.isprintable() or c in "\n\t")

        # Escape backslashes first (before quotes)
        text = text.replace("\\", "\\\\")

        # Escape double quotes
        text = text.replace('"', '\\"')

        # Strip leading/trailing whitespace
        text = text.strip()

        logger.debug(f"Sanitized text: {len(text)} chars")
        return text

    # === Batch Validation ===

    @staticmethod
    def validate_alarm_create_params(
        device_serial: str, device_type: str, alarm_time: str, label: str = ""
    ) -> dict[str, Any]:
        """
        Validate all parameters for create_alarm in one call.

        Args:
            device_serial: Device serial
            device_type: Device type
            alarm_time: Alarm time
            label: Alarm label (optional)

        Returns:
            Dict with validated params

        Raises:
            ValidationError: If any param invalid
        """
        return {
            "device_serial": InputValidator.validate_device_serial(device_serial),
            "device_type": InputValidator.validate_device_type(device_type),
            "alarm_time": InputValidator.validate_alarm_time(alarm_time),
            "label": InputValidator.sanitize_text(label, max_len=100) if label else "",
        }

    @staticmethod
    def validate_device_params(device_serial: str, device_type: str) -> dict[str, str]:
        """
        Validate device parameters (serial + type).

        Args:
            device_serial: Device serial
            device_type: Device type

        Returns:
            Dict with validated params

        Raises:
            ValidationError: If any param invalid
        """
        return {
            "device_serial": InputValidator.validate_device_serial(device_serial),
            "device_type": InputValidator.validate_device_type(device_type),
        }
