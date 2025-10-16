#!/usr/bin/env python3
"""
Tests unitaires pour AlarmManager après refactorisation.
"""

import unittest
from unittest.mock import Mock, patch
from core.alarms.alarm_manager import AlarmManager
from core.state_machine import AlexaStateMachine


class TestAlarmManagerRefactored(unittest.TestCase):
    """Tests pour valider la refactorisation d'AlarmManager."""

    def setUp(self):
        """Configuration commune aux tests."""
        self.http_client = Mock()
        self.http_client.csrf = "test_csrf"
        self.config = Mock()
        self.config.alexa_domain = "alexa.amazon.fr"
        self.config.amazon_domain = "amazon.fr"
        self.state_machine = AlexaStateMachine()

        # Mock du cache service
        self.cache_service = Mock()

        self.manager = AlarmManager(
            auth=Mock(),
            config=self.config,
            state_machine=self.state_machine,
            cache_service=self.cache_service,
            http_client=self.http_client,
        )

        # Mock du breaker
        self.manager.breaker = Mock()

    def test_create_alarm_uses_api_call(self):
        """Test que create_alarm utilise _api_call."""
        with patch.object(self.manager, "_check_connection", return_value=True):
            # Mock _api_call pour retourner un succès
            self.manager._api_call = Mock(return_value={"id": "alarm123"})

            result = self.manager.create_alarm(
                device_serial="SERIAL123", device_type="TYPE_A", alarm_time="14:30", label="Test Alarm"
            )

            # Vérifier que _api_call a été appelé avec les bons paramètres
            self.manager._api_call.assert_called_once()
            call_args = self.manager._api_call.call_args
            self.assertEqual(call_args[0][0], "post")  # method
            self.assertEqual(call_args[0][1], "/api/alarms")  # endpoint
            self.assertIn("json", call_args[1])  # payload

            # Vérifier le résultat
            self.assertEqual(result, {"id": "alarm123"})

    def test_update_alarm_uses_api_call(self):
        """Test que update_alarm utilise _api_call."""
        with patch.object(self.manager, "_check_connection", return_value=True):
            self.manager._api_call = Mock(return_value={"status": "updated"})

            result = self.manager.update_alarm(
                device_serial="SERIAL123",
                device_type="TYPE_A",
                alarm_id="alarm123",
                time="15:00",
                label="Updated Alarm",
            )

            self.manager._api_call.assert_called_once()
            call_args = self.manager._api_call.call_args
            self.assertEqual(call_args[0][0], "put")
            self.assertEqual(call_args[0][1], "/api/alarms/alarm123")

            self.assertTrue(result)

    def test_set_alarm_enabled_uses_api_call(self):
        """Test que set_alarm_enabled utilise _api_call."""
        with patch.object(self.manager, "_check_connection", return_value=True):
            self.manager._api_call = Mock(return_value={"status": "enabled"})

            result = self.manager.set_alarm_enabled(
                device_serial="SERIAL123", device_type="TYPE_A", alarm_id="alarm123", enabled=True
            )

            self.manager._api_call.assert_called_once()
            call_args = self.manager._api_call.call_args
            self.assertEqual(call_args[0][0], "put")
            self.assertEqual(call_args[0][1], "/api/alarms/alarm123")
            self.assertEqual(call_args[1]["json"], {"enabled": True})

            self.assertTrue(result)

    def test_refresh_alarms_cache_uses_api_call(self):
        """Test que _refresh_alarms_cache utilise _api_call."""
        mock_response = {
            "notifications": [
                {"type": "Alarm", "id": "alarm1"},
                {"type": "Reminder", "id": "reminder1"},
                {"type": "Alarm", "id": "alarm2"},
            ]
        }
        self.manager._api_call = Mock(return_value=mock_response)

        result = self.manager._refresh_alarms_cache()

        self.manager._api_call.assert_called_once_with("get", "/api/notifications")

        # Vérifier que seules les alarmes sont retournées
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "alarm1")
        self.assertEqual(result[1]["id"], "alarm2")

    def test_api_call_failure_returns_none(self):
        """Test que les méthodes retournent None/False en cas d'échec d'API."""
        with patch.object(self.manager, "_check_connection", return_value=True):
            self.manager._api_call = Mock(return_value=None)

            # Test create_alarm
            result = self.manager.create_alarm("SERIAL", "TYPE", "14:30")
            self.assertIsNone(result)

            # Test update_alarm
            result = self.manager.update_alarm("SERIAL", "TYPE", "alarm123", time="15:00")
            self.assertFalse(result)

            # Test set_alarm_enabled
            result = self.manager.set_alarm_enabled("SERIAL", "TYPE", "alarm123", True)
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
