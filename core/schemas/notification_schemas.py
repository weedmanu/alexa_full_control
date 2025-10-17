"""
Notification Schemas - Phase 3.5c.7

Data Transfer Objects (DTOs) for notification operations.

Classes:
- NotificationDTO: Notification metadata
- NotificationResponse: Response from notification operations

API Endpoints Covered:
- GET /api/notifications: List notifications
- POST /api/notifications: Send notification
"""

from typing import Optional

from pydantic import ConfigDict, Field

from core.schemas.base import DomainModel, ResponseDTO


class NotificationDTO(DomainModel):
    """Data model for a notification."""

    notification_id: str = Field(..., alias="notificationId")
    title: str
    message: str
    source: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class NotificationResponse(ResponseDTO):
    """Response from notification operation."""

    success: bool
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)
