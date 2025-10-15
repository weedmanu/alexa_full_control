"""
Gestionnaire de notifications Alexa - Thread-safe.
"""

import threading
from typing import Dict, List, Optional

from loguru import logger

from .circuit_breaker import CircuitBreaker
from .state_machine import AlexaStateMachine


class NotificationManager:
    """Gestionnaire thread-safe des notifications Alexa."""

    def __init__(self, auth, config, state_machine=None):
        self.auth = auth
        self.config = config
        self.state_machine = state_machine or AlexaStateMachine()
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self._lock = threading.RLock()
        logger.info("NotificationManager initialisé")

        # Compatibility: provide http_client wrapper for legacy auth
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth

    def list_notifications(self, limit: int = 50) -> List[Dict]:
        """Liste les notifications."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return []
            try:
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/notifications",
                    params={"size": limit},
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                return response.json().get("notifications", [])
            except Exception as e:
                logger.error(f"Erreur liste notifications: {e}")
                return []

    def delete_notification(self, notification_id: str) -> bool:
        """Supprime une notification."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                response = self.breaker.call(
                    self.http_client.delete,
                    f"https://{self.config.alexa_domain}/api/notifications/{notification_id}",
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Notification {notification_id} supprimée")
                return True
            except Exception as e:
                logger.error(f"Erreur suppression notification: {e}")
                return False

    def mark_as_read(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/notifications/{notification_id}",
                    json={"status": "READ"},
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Erreur marquage notification: {e}")
                return False

    def send_notification(self, device_serial: str, message: str, title: Optional[str] = None) -> bool:
        """
        Envoie une notification à un appareil.

        Args:
            device_serial: Numéro de série de l'appareil
            message: Message de la notification
            title: Titre optionnel de la notification

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                payload = {
                    "deviceSerialNumber": device_serial,
                    "notification": message,
                }
                if title:
                    payload["title"] = title

                response = self.breaker.call(
                    self.http_client.put,
                    f"https://{self.config.alexa_domain}/api/notifications/createReminder",
                    json=payload,
                    headers={"csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=10,
                )
                response.raise_for_status()
                logger.success(f"Notification envoyée à {device_serial}")
                return True
            except Exception as e:
                logger.error(f"Erreur envoi notification: {e}")
                return False

    def clear_notifications(self, device_serial: str) -> bool:
        """
        Efface toutes les notifications d'un appareil.

        Args:
            device_serial: Numéro de série de l'appareil

        Returns:
            True si succès, False sinon
        """
        with self._lock:
            if not self.state_machine.can_execute_commands:
                return False
            try:
                # Récupérer toutes les notifications de l'appareil
                notifications = self.list_notifications(limit=100)
                device_notifications = [n for n in notifications if n.get("deviceSerialNumber") == device_serial]

                if not device_notifications:
                    logger.info(f"Aucune notification pour {device_serial}")
                    return True

                # Supprimer chaque notification
                success_count = 0
                for notif in device_notifications:
                    notif_id = notif.get("id") or notif.get("notificationId")
                    if notif_id and self.delete_notification(notif_id):
                        success_count += 1

                logger.success(
                    f"{success_count}/{len(device_notifications)} notifications supprimées pour {device_serial}"
                )
                return success_count > 0
            except Exception as e:
                logger.error(f"Erreur suppression notifications: {e}")
                return False
