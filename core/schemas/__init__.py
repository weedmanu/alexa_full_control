"""
Schemas package - Pydantic DTOs for type-safe API contracts.

This package provides comprehensive Pydantic v2 DTOs for all API endpoints.
Each module contains domain-specific request/response schemas.

Modules:
    base: Base classes (BaseDTOModel, RequestDTO, ResponseDTO)
    device_schemas: Device-related DTOs
    music_schemas: Music/Playback DTOs
    auth_schemas: Authentication DTOs
    routine_schemas: Routine/Automation DTOs
    alarm_schemas: Alarm DTOs
    timer_schemas: Timer DTOs
    reminder_schemas: Reminder DTOs
    dnd_schemas: Do Not Disturb DTOs
    multiroom_schemas: Multiroom Audio DTOs
    lists_schemas: Lists/Shopping DTOs
    notification_schemas: Notification DTOs
    calendar_schemas: Calendar DTOs
    smart_home_schemas: Smart Home DTOs
    bluetooth_schemas: Bluetooth DTOs
    validators: Custom Pydantic validators

Phase: 3 - Type-Safe Data Contracts
Date: 17 octobre 2025
"""

# Import base classes for convenience
from core.schemas.base import (
    APIErrorDTO,
    APISuccessResponse,
    BaseDTOModel,
    DomainModel,
    RequestDTO,
    ResponseDTO,
    ValidationErrorDetail,
)

__all__ = [
    # Base classes
    "BaseDTOModel",
    "RequestDTO",
    "ResponseDTO",
    "DomainModel",
    "APIErrorDTO",
    "APISuccessResponse",
    "ValidationErrorDetail",
]
