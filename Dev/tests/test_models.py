
import unittest
from datetime import datetime

from models.command import DeviceCommand, CommandAction, CommandResult

class TestCommandModel(unittest.TestCase):

    def test_device_command_creation(self):
        command = DeviceCommand(
            device_id="123",
            action=CommandAction.SET_BRIGHTNESS,
            parameters={"brightness": 50}
        )
        self.assertEqual(command.device_id, "123")
        self.assertEqual(command.action, CommandAction.SET_BRIGHTNESS)
        self.assertEqual(command.parameters, {"brightness": 50})
        self.assertIsInstance(command.timestamp, datetime)

    def test_device_command_to_alexa_format(self):
        command = DeviceCommand(
            device_id="123",
            action=CommandAction.SET_BRIGHTNESS,
            parameters={"brightness": 50}
        )
        alexa_format = command.to_alexa_format()

        self.assertEqual(alexa_format['deviceId'], "123")
        self.assertEqual(alexa_format['action'], "SET_BRIGHTNESS")
        self.assertEqual(alexa_format['parameters'], {"brightness": 50})
        self.assertIn('timestamp', alexa_format)

    def test_command_result_success(self):
        result = CommandResult.success_result("Command executed", {"status": "ok"})
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Command executed")
        self.assertEqual(result.data, {"status": "ok"})
        self.assertIsNone(result.error_code)

    def test_command_result_error(self):
        result = CommandResult.error_result("Command failed", "E-101", {"details": "timeout"})
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Command failed")
        self.assertEqual(result.error_code, "E-101")
        self.assertEqual(result.data, {"details": "timeout"})

if __name__ == '__main__':
    unittest.main()
