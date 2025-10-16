"""
TDD Tests for InputValidators - Write tests BEFORE implementation.

Test Coverage:
- device_serial validation
- device_type validation
- alarm_time validation
- Text sanitization (labels, descriptions)
- Edge cases and error handling
"""

import unittest

from core.security.validators import InputValidator, ValidationError


class TestDeviceSerialValidation(unittest.TestCase):
    """Test device serial number validation."""

    def test_valid_device_serial_uppercase(self):
        """Valid device serial (uppercase letters, numbers, hyphens)."""
        serial = InputValidator.validate_device_serial("ABC123DEF456")
        self.assertEqual(serial, "ABC123DEF456")

    def test_valid_device_serial_with_hyphens(self):
        """Valid device serial with hyphens."""
        serial = InputValidator.validate_device_serial("ABC-123-DEF-456")
        self.assertEqual(serial, "ABC-123-DEF-456")

    def test_invalid_device_serial_empty(self):
        """Empty device serial should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_serial("")

    def test_invalid_device_serial_too_short(self):
        """Device serial < 8 chars should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_serial("ABC123")

    def test_invalid_device_serial_too_long(self):
        """Device serial > 50 chars should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_serial("A" * 51)

    def test_invalid_device_serial_lowercase(self):
        """Device serial with lowercase should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_serial("abc123def456")

    def test_invalid_device_serial_special_chars(self):
        """Device serial with special chars (not hyphens) should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_serial("ABC@123DEF#456")

    def test_invalid_device_serial_spaces(self):
        """Device serial with spaces should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_serial("ABC 123 DEF")

    def test_invalid_device_serial_not_string(self):
        """Non-string device serial should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_serial(123456)


class TestDeviceTypeValidation(unittest.TestCase):
    """Test device type validation."""

    def test_valid_device_type_echo_dot(self):
        """Valid device type ECHO_DOT."""
        device_type = InputValidator.validate_device_type("ECHO_DOT")
        self.assertEqual(device_type, "ECHO_DOT")

    def test_valid_device_type_echo_show(self):
        """Valid device type ECHO_SHOW."""
        device_type = InputValidator.validate_device_type("ECHO_SHOW")
        self.assertEqual(device_type, "ECHO_SHOW")

    def test_valid_device_type_current(self):
        """Valid device type ALEXA_CURRENT_DEVICE_TYPE."""
        device_type = InputValidator.validate_device_type("ALEXA_CURRENT_DEVICE_TYPE")
        self.assertEqual(device_type, "ALEXA_CURRENT_DEVICE_TYPE")

    def test_invalid_device_type_unknown(self):
        """Unknown device type should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_type("UNKNOWN_DEVICE")

    def test_invalid_device_type_lowercase(self):
        """Lowercase device type should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_type("echo_dot")

    def test_invalid_device_type_empty(self):
        """Empty device type should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_device_type("")


class TestAlarmTimeValidation(unittest.TestCase):
    """Test alarm time validation."""

    def test_valid_alarm_time_hhmm(self):
        """Valid alarm time HH:MM format."""
        time = InputValidator.validate_alarm_time("14:30")
        self.assertEqual(time, "14:30")

    def test_valid_alarm_time_midnight(self):
        """Valid alarm time 00:00."""
        time = InputValidator.validate_alarm_time("00:00")
        self.assertEqual(time, "00:00")

    def test_valid_alarm_time_end_of_day(self):
        """Valid alarm time 23:59."""
        time = InputValidator.validate_alarm_time("23:59")
        self.assertEqual(time, "23:59")

    def test_valid_alarm_time_iso_format(self):
        """Valid alarm time ISO 8601 format."""
        time = InputValidator.validate_alarm_time("2025-10-16T14:30:00")
        self.assertEqual(time, "2025-10-16T14:30:00")

    def test_invalid_alarm_time_hour_too_high(self):
        """Invalid hour (> 23) should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_alarm_time("24:00")

    def test_invalid_alarm_time_minute_too_high(self):
        """Invalid minute (> 59) should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_alarm_time("12:60")

    def test_invalid_alarm_time_wrong_format(self):
        """Invalid format should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_alarm_time("14-30")

    def test_invalid_alarm_time_empty(self):
        """Empty alarm time should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_alarm_time("")

    def test_invalid_alarm_time_garbage(self):
        """Garbage input should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_alarm_time("not a time")


class TestTextSanitization(unittest.TestCase):
    """Test text sanitization (labels, descriptions)."""

    def test_sanitize_simple_text(self):
        """Simple text should be returned as-is."""
        text = InputValidator.sanitize_text("My Label")
        self.assertEqual(text, "My Label")

    def test_sanitize_text_with_spaces(self):
        """Text with spaces should be preserved."""
        text = InputValidator.sanitize_text("My Alarm Label")
        self.assertEqual(text, "My Alarm Label")

    def test_sanitize_text_with_numbers(self):
        """Text with numbers should be preserved."""
        text = InputValidator.sanitize_text("Alarm 123")
        self.assertEqual(text, "Alarm 123")

    def test_sanitize_text_strips_leading_trailing_spaces(self):
        """Leading/trailing spaces should be stripped."""
        text = InputValidator.sanitize_text("  My Label  ")
        self.assertEqual(text, "My Label")

    def test_sanitize_text_max_length_respected(self):
        """Text exceeding max_length should raise error."""
        long_text = "A" * 501
        with self.assertRaises(ValidationError):
            InputValidator.sanitize_text(long_text, max_len=500)

    def test_sanitize_text_custom_max_length(self):
        """Custom max_length should be respected."""
        text = InputValidator.sanitize_text("ABC", max_len=5)
        self.assertEqual(text, "ABC")

    def test_sanitize_text_equals_max_length(self):
        """Text exactly at max_length should be OK."""
        text = InputValidator.sanitize_text("ABCDE", max_len=5)
        self.assertEqual(text, "ABCDE")

    def test_sanitize_text_removes_control_chars(self):
        """Control characters should be removed."""
        text_with_ctrl = "My\x00Label"  # Null character
        result = InputValidator.sanitize_text(text_with_ctrl)
        self.assertNotIn("\x00", result)

    def test_sanitize_text_preserves_newlines_tabs(self):
        """Newlines and tabs should be preserved."""
        text = "Line1\nLine2\tTabbed"
        result = InputValidator.sanitize_text(text)
        self.assertIn("\n", result)
        self.assertIn("\t", result)

    def test_sanitize_text_escapes_quotes(self):
        """Double quotes should be escaped for JSON."""
        text = 'My "Label"'
        result = InputValidator.sanitize_text(text)
        # Quotes should be escaped
        self.assertIn('\\"', result)

    def test_sanitize_text_escapes_backslashes(self):
        """Backslashes should be escaped."""
        text = "Path\\to\\file"
        result = InputValidator.sanitize_text(text)
        self.assertIn("\\\\", result)

    def test_sanitize_text_not_string(self):
        """Non-string input should raise error."""
        with self.assertRaises(ValidationError):
            InputValidator.sanitize_text(123)

    def test_sanitize_text_special_chars_allowed(self):
        """Special chars like !@#$% should be allowed."""
        text = "Alarm! @Home #1 $100 %50"
        result = InputValidator.sanitize_text(text)
        self.assertEqual(text, result)

    def test_sanitize_text_unicode_allowed(self):
        """Unicode characters should be allowed."""
        text = "Alarme élégante 你好"
        result = InputValidator.sanitize_text(text)
        self.assertEqual(text, result)

    def test_sanitize_text_empty_string(self):
        """Empty string should return empty string."""
        text = InputValidator.sanitize_text("")
        self.assertEqual(text, "")


class TestValidatorIntegration(unittest.TestCase):
    """Integration tests combining multiple validators."""

    def test_validate_create_alarm_params(self):
        """Test typical create_alarm parameter validation."""
        device_serial = InputValidator.validate_device_serial("ABC123DEF456")
        device_type = InputValidator.validate_device_type("ECHO_DOT")
        alarm_time = InputValidator.validate_alarm_time("14:30")
        label = InputValidator.sanitize_text("Work Alarm", max_len=100)

        self.assertEqual(device_serial, "ABC123DEF456")
        self.assertEqual(device_type, "ECHO_DOT")
        self.assertEqual(alarm_time, "14:30")
        self.assertEqual(label, "Work Alarm")

    def test_validate_with_all_invalid_inputs(self):
        """Test that validators catch all invalid inputs."""
        invalid_inputs = [
            ("", "device_serial"),  # Empty serial
            ("UNKNOWN", "device_type"),  # Unknown type
            ("25:00", "alarm_time"),  # Invalid time
            ("A" * 501, "text"),  # Text too long
        ]

        for invalid_input, field_type in invalid_inputs:
            with self.assertRaises(ValidationError):
                if field_type == "device_serial":
                    InputValidator.validate_device_serial(invalid_input)
                elif field_type == "device_type":
                    InputValidator.validate_device_type(invalid_input)
                elif field_type == "alarm_time":
                    InputValidator.validate_alarm_time(invalid_input)
                elif field_type == "text":
                    InputValidator.sanitize_text(invalid_input)


if __name__ == "__main__":
    unittest.main()
