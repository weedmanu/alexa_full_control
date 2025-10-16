import unittest
from unittest.mock import Mock, patch
import requests
from core.base_manager import BaseManager
from core.state_machine import AlexaStateMachine

class TestBaseManagerHeaders(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock()
        self.http_client.csrf = "test_csrf_token"
        self.config = Mock()
        self.config.amazon_domain = "amazon.fr"
        self.state_machine = AlexaStateMachine()

        self.manager = BaseManager(
            http_client=self.http_client,
            config=self.config,
            state_machine=self.state_machine
        )

    def test_get_api_headers_basic(self):
        """Test headers de base."""
        headers = self.manager._get_api_headers()

        self.assertEqual(headers["Content-Type"], "application/json; charset=UTF-8")
        self.assertIn("alexa.amazon.fr", headers["Referer"])
        self.assertEqual(headers["csrf"], "test_csrf_token")

    def test_get_api_headers_with_extra(self):
        """Test headers avec extra."""
        headers = self.manager._get_api_headers({"X-Custom": "value"})

        self.assertEqual(headers["X-Custom"], "value")
        self.assertEqual(headers["csrf"], "test_csrf_token")

    def test_get_api_headers_csrf_missing(self):
        """Test headers sans csrf."""
        # Recréer le manager avec un client sans csrf
        http_client_no_csrf = Mock()
        http_client_no_csrf.csrf = None
        manager_no_csrf = BaseManager(
            http_client=http_client_no_csrf,
            config=self.config,
            state_machine=self.state_machine
        )
        headers = manager_no_csrf._get_api_headers()

        self.assertIsNone(headers["csrf"])

if __name__ == '__main__':
    unittest.main()