"""
Multiroom Schemas - Phase 3.5c.6

Data Transfer Objects (DTOs) for multiroom audio operations.

Classes:
- MultiRoomGroupDTO: Room group metadata
- CreateMultiRoomRequest: Request to create a group
- MultiRoomResponse: Response from multiroom operations

API Endpoints Covered:
- GET /api/multiroom/groups: List all room groups
- POST /api/multiroom/groups: Create a group
- DELETE /api/multiroom/groups/{groupId}: Delete group
"""

from typing import List, Optional

from pydantic import ConfigDict, Field

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class MultiRoomGroupDTO(DomainModel):
    """Data model for a multiroom group."""

    group_id: str = Field(..., alias="groupId")
    name: str
    device_serials: List[str] = Field(default_factory=list, alias="deviceSerials")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class CreateMultiRoomRequest(RequestDTO):
    """Request to create a multiroom group."""

    device_serials: List[str] = Field(..., alias="deviceSerials")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class MultiRoomResponse(ResponseDTO):
    """Response from multiroom operation."""

    success: bool
    group_id: Optional[str] = Field(None, alias="groupId")
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)
