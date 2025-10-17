"""
List Schemas - Phase 3.5c.8

Data Transfer Objects (DTOs) for shopping list operations.

Classes:
- ListDTO: List metadata and items
- CreateListRequest: Request to create a list
- ListResponse: Response from list operations

API Endpoints Covered:
- GET /api/lists: List all shopping lists
- POST /api/lists: Create a new list
- PUT /api/lists/{listId}: Update list
- DELETE /api/lists/{listId}: Delete list
"""

from typing import List as ListType
from typing import Optional

from pydantic import ConfigDict, Field

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class ListDTO(DomainModel):
    """Data model for a shopping list."""

    list_id: str = Field(..., alias="listId")
    name: str
    items: ListType[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class CreateListRequest(RequestDTO):
    """Request to create a shopping list."""

    device_serial_number: str = Field(..., alias="deviceSerialNumber")
    name: str

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)


class ListResponse(ResponseDTO):
    """Response from list operation."""

    success: bool
    list_id: Optional[str] = Field(None, alias="listId")
    error: Optional[str] = None
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True, frozen=True, extra="forbid", str_strip_whitespace=True)
