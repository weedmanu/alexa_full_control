"""
Notification Schema Tests - Phase 3.5c.7 (TDD)

Tests for notification DTOs.
Covers: notification delivery, notification status.

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/notification_schemas.py
"""

import pytest
from datetime import datetime, timezone
from typing import Optional
from pydantic import ValidationError


class TestNotificationDTO:
    """Test NotificationDTO."""

    def test_notification_required_fields(self):
        """Should accept notification_id, title, message."""
        from core.schemas.notification_schemas import NotificationDTO
        
        notif = NotificationDTO(
            notification_id="notif123",
            title="Alert",
            message="Test message"
        )
        
        assert notif.notification_id == "notif123"
        assert notif.title == "Alert"

    def test_notification_requires_id(self):
        """ID is required."""
        from core.schemas.notification_schemas import NotificationDTO
        
        with pytest.raises(ValidationError):
            NotificationDTO(title="Alert", message="Test")

    def test_notification_requires_title(self):
        """Title is required."""
        from core.schemas.notification_schemas import NotificationDTO
        
        with pytest.raises(ValidationError):
            NotificationDTO(notification_id="notif123", message="Test")

    def test_notification_requires_message(self):
        """Message is required."""
        from core.schemas.notification_schemas import NotificationDTO
        
        with pytest.raises(ValidationError):
            NotificationDTO(notification_id="notif123", title="Alert")

    def test_notification_is_immutable(self):
        """NotificationDTO should be frozen."""
        from core.schemas.notification_schemas import NotificationDTO
        
        notif = NotificationDTO(notification_id="notif123", title="Alert", message="Test")
        
        with pytest.raises(Exception):
            notif.title = "Warning"


class TestNotificationResponse:
    """Test NotificationResponse."""

    def test_notification_response_success(self):
        """Should accept success flag."""
        from core.schemas.notification_schemas import NotificationResponse
        
        response = NotificationResponse(success=True)
        
        assert response.success is True
        assert response.created_at is not None

    def test_notification_response_with_error(self):
        """Should accept error information."""
        from core.schemas.notification_schemas import NotificationResponse
        
        response = NotificationResponse(
            success=False,
            error="Failed to send"
        )
        
        assert response.success is False

    def test_notification_response_requires_success(self):
        """Success field is required."""
        from core.schemas.notification_schemas import NotificationResponse
        
        with pytest.raises(ValidationError):
            NotificationResponse()

    def test_notification_response_auto_sets_created_at(self):
        """Created_at should be auto-set."""
        from core.schemas.notification_schemas import NotificationResponse
        
        before = datetime.now(timezone.utc)
        response = NotificationResponse(success=True)
        after = datetime.now(timezone.utc)
        
        assert response.created_at is not None
        assert before <= response.created_at <= after


class TestNotificationWorkflow:
    """Test notification workflows."""

    def test_notification_list_parsing(self):
        """Should parse list of notifications."""
        from core.schemas.notification_schemas import NotificationDTO
        
        notif_data = [
            {"notificationId": "notif1", "title": "Alert 1", "message": "Msg 1"},
            {"notificationId": "notif2", "title": "Alert 2", "message": "Msg 2"}
        ]
        
        notifs = [NotificationDTO(**n) for n in notif_data]
        
        assert len(notifs) == 2
        assert notifs[0].notification_id == "notif1"

    def test_notification_field_aliasing(self):
        """Should support camelCase field aliasing."""
        from core.schemas.notification_schemas import NotificationDTO
        
        notif_data = {
            "notificationId": "notif123",
            "title": "Alert",
            "message": "Test message"
        }
        
        notif = NotificationDTO(**notif_data)
        
        assert notif.notification_id == "notif123"
