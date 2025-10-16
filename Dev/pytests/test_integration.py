"""
Tests d'intégration pour Alexa Full Control.

Ces tests valident le comportement global du système en testant
l'intégration entre les différents managers et composants.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Imports des managers
from core.device_manager import DeviceManager
from core.dnd_manager import DNDManager
from core.notification_manager import NotificationManager
from core.state_machine import AlexaStateMachine, ConnectionState
from services.cache_service import CacheService


class TestIntegrationScenarios:
    """Tests de scénarios d'intégration complets."""

    @pytest.fixture
    def mock_auth(self):
        """Mock AlexaAuth pour les tests."""
        auth = Mock()
        auth.amazon_domain = "amazon.fr"
        auth.alexa_domain = "alexa.amazon.fr"
        return auth

    @pytest.fixture
    def mock_config(self):
        """Mock config pour les tests."""
        config = Mock()
        config.amazon_domain = "amazon.fr"
        config.alexa_domain = "alexa.amazon.fr"
        return config

    @pytest.fixture
    def state_machine(self):
        """State machine pour les tests."""
        sm = AlexaStateMachine()
        sm.set_initial_state(ConnectionState.AUTHENTICATED)
        return sm

    @pytest.fixture
    def cache_service(self):
        """Cache service pour les tests."""
        return CacheService()

    @pytest.fixture
    def device_manager(self, mock_auth, state_machine, cache_service):
        """DeviceManager configuré pour les tests."""
        return DeviceManager(
            auth=mock_auth,
            state_machine=state_machine,
            cache_service=cache_service,
            cache_ttl=300
        )

    @pytest.fixture
    def dnd_manager(self, mock_auth, mock_config, state_machine):
        """DNDManager configuré pour les tests."""
        return DNDManager(
            auth=mock_auth,
            config=mock_config,
            state_machine=state_machine
        )

    @pytest.fixture
    def notification_manager(self, mock_auth, mock_config, state_machine):
        """NotificationManager configuré pour les tests."""
        return NotificationManager(
            auth=mock_auth,
            config=mock_config,
            state_machine=state_machine
        )

    def test_device_discovery_and_dnd_integration(self, device_manager, dnd_manager):
        """Test intégration : découverte appareils + configuration DND."""
        # Mock des données d'appareils
        mock_devices = [
            {
                "accountName": "Salon",
                "serialNumber": "SERIAL123",
                "deviceType": "A3S5BH2HU6VAYF",
                "online": True
            },
            {
                "accountName": "Cuisine",
                "serialNumber": "SERIAL456",
                "deviceType": "A3S5BH2HU6VAYF",
                "online": True
            }
        ]

        # Mock de l'appel API pour get_devices
        with patch.object(device_manager, '_api_call') as mock_api:
            mock_api.return_value = {"devices": mock_devices}

            # Récupération des appareils
            devices = device_manager.get_devices(force_refresh=True)
            assert len(devices) == 2
            assert devices[0]["accountName"] == "Salon"

            # Recherche d'un appareil
            salon = device_manager.find_device_by_name("Salon")
            assert salon is not None
            assert salon["serialNumber"] == "SERIAL123"

            # Configuration DND sur cet appareil
            with patch.object(dnd_manager, '_api_call') as mock_dnd_api:
                mock_dnd_api.return_value = {"status": "success"}

                success = dnd_manager.enable_dnd("SERIAL123", "A3S5BH2HU6VAYF")
                assert success is True

                # Vérification du statut DND
                mock_dnd_api.return_value = {
                    "doNotDisturbDeviceStatusList": [
                        {
                            "deviceSerialNumber": "SERIAL123",
                            "enabled": True
                        }
                    ]
                }

                status = dnd_manager.get_dnd_status("SERIAL123")
                assert status is not None
                assert status["enabled"] is True

    def test_notification_workflow_integration(self, device_manager, notification_manager):
        """Test intégration : workflow complet de notifications."""
        # Mock des appareils
        mock_devices = [
            {
                "accountName": "Bureau",
                "serialNumber": "SERIAL789",
                "deviceType": "A3S5BH2HU6VAYF",
                "online": True
            }
        ]

        with patch.object(device_manager, '_api_call') as mock_device_api:
            mock_device_api.return_value = {"devices": mock_devices}

            # Récupération de l'appareil
            devices = device_manager.get_devices(force_refresh=True)
            bureau = devices[0]

            # Envoi d'une notification
            with patch.object(notification_manager, '_api_call') as mock_notif_api:
                mock_notif_api.return_value = {"notificationId": "notif123"}

                success = notification_manager.send_notification(
                    bureau["serialNumber"],
                    "Test notification",
                    "Titre test"
                )
                assert success is True

                # Liste des notifications
                mock_notif_api.return_value = {
                    "notifications": [
                        {
                            "id": "notif123",
                            "deviceSerialNumber": "SERIAL789",
                            "notification": "Test notification",
                            "title": "Titre test"
                        }
                    ]
                }

                notifications = notification_manager.list_notifications()
                assert len(notifications) == 1
                assert notifications[0]["notification"] == "Test notification"

                # Marquage comme lu
                mock_notif_api.return_value = {"status": "READ"}
                read_success = notification_manager.mark_as_read("notif123")
                assert read_success is True

                # Suppression de la notification
                mock_notif_api.return_value = {"deleted": True}
                delete_success = notification_manager.delete_notification("notif123")
                assert delete_success is True

    def test_error_resilience_integration(self, device_manager, dnd_manager, notification_manager):
        """Test intégration : résilience aux erreurs."""
        # Test avec connexion perdue
        device_manager.state_machine.transition_to(ConnectionState.DISCONNECTED)

        # Les appels devraient échouer gracieusement
        devices = device_manager.get_devices()
        assert devices is None

        dnd_success = dnd_manager.enable_dnd("SERIAL123", "TYPE")
        assert dnd_success is False

        notif_success = notification_manager.send_notification("SERIAL", "test")
        assert notif_success is False

        # Test avec API en erreur
        device_manager.state_machine.set_initial_state(ConnectionState.AUTHENTICATED)

        with patch.object(device_manager, '_api_call') as mock_api:
            mock_api.return_value = None  # Simule erreur API

            devices = device_manager.get_devices(force_refresh=True)
            assert devices is None

    def test_cache_performance_integration(self, device_manager):
        """Test intégration : performance du cache."""
        import time

        mock_devices = [
            {
                "accountName": f"Device{i}",
                "serialNumber": f"SERIAL{i}",
                "deviceType": "A3S5BH2HU6VAYF",
                "online": True
            } for i in range(10)
        ]

        with patch.object(device_manager, '_api_call') as mock_api:
            mock_api.return_value = {"devices": mock_devices}

            # Premier appel (devrait aller à l'API)
            start_time = time.time()
            devices1 = device_manager.get_devices(force_refresh=True)
            api_time = time.time() - start_time

            # Deuxième appel (devrait utiliser le cache)
            start_time = time.time()
            devices2 = device_manager.get_devices()
            cache_time = time.time() - start_time

            # Vérification des données
            assert len(devices1) == 10
            assert devices1 == devices2

            # Le cache devrait être plus rapide (au moins 10x plus rapide en théorie)
            # En pratique, on vérifie juste que c'est raisonnable
            assert cache_time < api_time or cache_time < 0.001  # Moins de 1ms pour le cache

    def test_cross_manager_data_consistency(self, device_manager, dnd_manager, notification_manager):
        """Test intégration : cohérence des données entre managers."""
        # Mock des appareils
        mock_devices = [
            {
                "accountName": "TestDevice",
                "serialNumber": "SERIAL999",
                "deviceType": "A3S5BH2HU6VAYF",
                "online": True
            }
        ]

        with patch.object(device_manager, '_api_call') as mock_device_api:
            mock_device_api.return_value = {"devices": mock_devices}

            # Récupération via DeviceManager
            devices = device_manager.get_devices(force_refresh=True)
            device = devices[0]

            # Utilisation du serial dans DNDManager
            with patch.object(dnd_manager, '_api_call') as mock_dnd_api:
                mock_dnd_api.return_value = {"status": "success"}

                dnd_success = dnd_manager.enable_dnd(
                    device["serialNumber"],
                    device["deviceType"]
                )
                assert dnd_success is True

                # Utilisation du même serial dans NotificationManager
                with patch.object(notification_manager, '_api_call') as mock_notif_api:
                    mock_notif_api.return_value = {"notificationId": "notif999"}

                    notif_success = notification_manager.send_notification(
                        device["serialNumber"],
                        "Test cross-manager"
                    )
                    assert notif_success is True

    def test_bulk_operations_integration(self, notification_manager):
        """Test intégration : opérations en masse."""
        # Mock de notifications multiples
        mock_notifications = [
            {
                "id": f"notif{i}",
                "deviceSerialNumber": "SERIAL_BULK",
                "notification": f"Notification {i}"
            } for i in range(5)
        ]

        with patch.object(notification_manager, '_api_call') as mock_api:
            # Mock pour list_notifications
            def mock_api_call(*args, **kwargs):
                method, url = args
                if method == 'get' and '/api/notifications' in url:
                    return {"notifications": mock_notifications}
                elif method == 'delete' and '/api/notifications/' in url:
                    return {"deleted": True}
                return None

            mock_api.side_effect = mock_api_call            # Liste des notifications
            notifications = notification_manager.list_notifications(limit=100)
            assert len(notifications) == 5

            # Suppression en masse
            bulk_success = notification_manager.clear_notifications("SERIAL_BULK")
            assert bulk_success is True

            # Vérification que delete_notification a été appelée 5 fois
            # 1 appel pour list_notifications (test) + 1 appel pour list_notifications (clear) + 5 appels pour delete_notification
            assert mock_api.call_count == 7


class TestPerformanceOptimizations:
    """Tests des optimisations de performance apportées."""

    def test_base_headers_precomputation(self):
        """Test que les headers de base sont pré-calculés."""
        from core.base_manager import BaseManager
        from unittest.mock import Mock

        mock_http_client = Mock()
        mock_config = Mock()
        mock_config.amazon_domain = "amazon.fr"
        mock_state_machine = Mock()

        manager = BaseManager(
            http_client=mock_http_client,
            config=mock_config,
            state_machine=mock_state_machine
        )

        # Vérification que les headers de base sont pré-calculés
        assert hasattr(manager, '_base_headers')
        assert "Content-Type" in manager._base_headers
        assert "Referer" in manager._base_headers
        assert "Origin" in manager._base_headers

        # Vérification que l'URL contient le domaine correct
        assert "amazon.fr" in manager._base_headers["Referer"]

    def test_debug_mode_optimization(self):
        """Test que le mode debug optimise les logs."""
        from core.base_manager import BaseManager
        from unittest.mock import Mock
        import os

        # Test avec DEBUG=true
        os.environ["DEBUG"] = "true"
        manager_debug = BaseManager(
            http_client=Mock(),
            config=Mock(amazon_domain="amazon.fr"),
            state_machine=Mock()
        )
        assert manager_debug._debug_mode is True

        # Test avec DEBUG=false
        os.environ["DEBUG"] = "false"
        manager_prod = BaseManager(
            http_client=Mock(),
            config=Mock(amazon_domain="amazon.fr"),
            state_machine=Mock()
        )
        assert manager_prod._debug_mode is False

        # Nettoyage
        del os.environ["DEBUG"]

    def test_device_manager_url_precomputation(self):
        """Test que DeviceManager pré-calcule l'URL de base."""
        from unittest.mock import Mock

        mock_auth = Mock()
        mock_auth.amazon_domain = "amazon.fr"
        mock_config = Mock()
        mock_config.amazon_domain = "amazon.fr"

        manager = DeviceManager(
            auth=mock_auth,
            state_machine=Mock(),
            cache_service=Mock()
        )

        # Vérification que l'URL de base est pré-calculée
        assert hasattr(manager, '_base_url')
        assert manager._base_url == "https://amazon.fr"