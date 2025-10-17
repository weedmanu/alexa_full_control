"""
Gestionnaire de notifications Alexa - Thread-safe.
"""

from typing import Any, Dict, List, Optional, cast

from loguru import logger

from .base_manager import BaseManager, create_http_client_from_auth
from .state_machine import AlexaStateMachine


class NotificationManager(BaseManager[Dict[str, Any]]):
    """Gestionnaire thread-safe des notifications Alexa."""

    def __init__(self, auth: Any, config: Any, state_machine: Optional[AlexaStateMachine] = None, api_service: Optional[Any] = None) -> None:
        # Créer le client HTTP depuis auth
        http_client = create_http_client_from_auth(auth)

        # Initialiser BaseManager
        super().__init__(
            http_client=http_client,
            config=config,
            state_machine=state_machine or AlexaStateMachine(),
        )

        # Attributs spécifiques à NotificationManager
        self.auth = auth
        # Optional AlexaAPIService for future centralized API calls
        self._api_service: Optional[Any] = api_service

        logger.info("NotificationManager initialisé")

    def list_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Liste les notifications."""
        if not self._check_connection():
            return []
        try:
            data = self._api_call("get", "/api/notifications", params={"size": limit}, timeout=10)
            if data is None:
                return []

            notifications = data.get("notifications", [])
            return cast(List[Dict[str, Any]], notifications) if isinstance(notifications, list) else []
        except Exception as e:
            self.logger.error(f"Erreur liste notifications: {e}")
            return []

    def delete_notification(self, notification_id: str) -> bool:
        """Supprime une notification."""
        if not self._check_connection():
            return False
        try:
            result = self._api_call("delete", f"/api/notifications/{notification_id}", timeout=10)
            if result is not None:
                self.logger.success(f"Notification {notification_id} supprimée")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur suppression notification: {e}")
            return False

    def mark_as_read(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        if not self._check_connection():
            return False
        try:
            result = self._api_call("put", f"/api/notifications/{notification_id}", json={"status": "READ"}, timeout=10)
            return result is not None
        except Exception as e:
            self.logger.error(f"Erreur marquage notification: {e}")
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
        if not self._check_connection():
            return False
        try:
            payload = {
                "deviceSerialNumber": device_serial,
                "notification": message,
            }
            if title:
                payload["title"] = title

            result = self._api_call("put", "/api/notifications/createReminder", json=payload, timeout=10)
            if result is not None:
                self.logger.success(f"Notification envoyée à {device_serial}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur envoi notification: {e}")
            return False

    def clear_notifications(self, device_serial: str) -> bool:
        """
        Efface toutes les notifications d'un appareil.

        Args:
            device_serial: Numéro de série de l'appareil

        Returns:
            True si succès, False sinon
        """
        if not self._check_connection():
            return False
        try:
            # Récupérer toutes les notifications de l'appareil
            notifications = self.list_notifications(limit=100)
            device_notifications = [n for n in notifications if n.get("deviceSerialNumber") == device_serial]

            if not device_notifications:
                self.logger.info(f"Aucune notification pour {device_serial}")
                return True

            # Supprimer chaque notification
            success_count = 0
            for notif in device_notifications:
                notif_id = notif.get("id") or notif.get("notificationId")
                if notif_id and self.delete_notification(notif_id):
                    success_count += 1

            self.logger.success(
                f"{success_count}/{len(device_notifications)} notifications supprimées pour {device_serial}"
            )
            return success_count > 0
        except Exception as e:
            self.logger.error(f"Erreur suppression notifications: {e}")
            return False
