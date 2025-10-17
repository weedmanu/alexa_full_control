"""
Base classes and common types for all DTOs.

Provides consistent configuration, validation patterns,
and reusable types across all schemas.

This module forms the foundation of the Phase 3 DTO layer,
ensuring all domain-specific schemas inherit common features:
- Whitespace stripping on strings
- Strict field validation (no extra fields)
- Field name aliasing (camelCase ↔ snake_case)
- Immutability for Request/Response DTOs
- JSON Schema generation with examples

Module Organization:
    - BaseDTOModel: Base for all DTOs with Pydantic v2 config
    - RequestDTO: For API request data (frozen)
    - ResponseDTO: For API response data (frozen)
    - DomainModel: For reusable domain objects (not frozen)
    - APIErrorDTO: Standard error response format
    - APISuccessResponse: Generic success wrapper with data
    - ValidationErrorDetail: Field-level validation errors

Example:
    Creating a simple DTO:
    
    >>> from pydantic import Field
    >>> class Device(ResponseDTO):
    ...     serial_number: str = Field(..., alias='serialNumber')
    ...     online: bool
    >>> 
    >>> api_data = {'serialNumber': 'ABC123', 'online': True}
    >>> device = Device(**api_data)
    >>> print(device.serial_number)
    ABC123

Author: Phase 3 - DTO Layer
Date: 17 octobre 2025
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")  # Generic type variable for APISuccessResponse


class BaseDTOModel(BaseModel):
    """
    Base class for all DTOs with common Pydantic v2 configuration.

    Features:
    --------
    - **String Whitespace Stripping**: Automatically trim whitespace from strings
    - **Strict Field Validation**: Reject unknown/extra fields
    - **Field Name Aliasing**: Support both camelCase (API) and snake_case (Python)
    - **JSON Schema Support**: Auto-generate OpenAPI/JSON Schema
    - **Examples**: Include examples for documentation

    Configuration:
    --------
    - str_strip_whitespace=True: "  hello  " → "hello"
    - extra='forbid': Unknown fields raise ValidationError
    - populate_by_name=True: Accept both field names and aliases
    - use_enum_values=True: Use enum values, not enum instances
    - validate_assignment=False: Don't validate on attribute assignment
    - validate_default=False: Don't validate default values

    Example:
        >>> class MyDTO(BaseDTOModel):
        ...     name: str = Field(..., alias='firstName')
        >>>
        >>> MyDTO(firstName='  John  ')  # Input: camelCase with spaces
        MyDTO(name='John')  # Output: snake_case, trimmed
    """

    model_config = ConfigDict(
        # String transformation
        str_strip_whitespace=True,  # Automatically trim whitespace
        str_to_lower=False,  # Keep case as-is
        # Field validation
        extra="forbid",  # Reject unknown fields (strict mode)
        populate_by_name=True,  # Accept both snake_case and camelCase
        # Enum handling
        use_enum_values=True,  # Use enum values, not enum names
        # Validation behavior
        validate_default=False,  # Don't validate defaults
        validate_assignment=False,  # Optimize: no post-init validation
        # JSON Schema generation
        json_schema_extra={
            "examples": [],  # Override in subclasses
        },
    )

    @field_validator("*", mode="before")
    @classmethod
    def validate_none_strings(cls, v: Any) -> Any:
        """
        Prevent None strings like 'None', 'null', 'undefined'.

        Some APIs might return these as strings instead of actual None.
        This validator catches them and converts to actual None.
        """
        if isinstance(v, str) and v.lower() in ("none", "null", "undefined", ""):
            return None
        return v


class RequestDTO(BaseDTOModel):
    """
    Base class for all API request DTOs.

    Properties:
    ----------
    - **Immutable**: frozen=True prevents modification after creation
    - **Type-Safe**: All fields must match declared types
    - **Validated**: Input validation before API call
    - **Documentation**: Docstrings and examples for IDE support

    Usage:
    -----
    Request DTOs represent data being SENT to the API.
    They should be immutable (frozen) to prevent accidental modifications.

    Example:
        >>> class CreateDeviceRequest(RequestDTO):
        ...     name: str
        ...     device_type: str
        >>>
        >>> request = CreateDeviceRequest(name='Salon', device_type='ECHO_DOT')
        >>> request.name = 'Kitchen'  # ❌ FrozenInstanceError
    """

    model_config = ConfigDict(
        frozen=True,  # Immutable - prevents modification
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class ResponseDTO(BaseDTOModel):
    """
    Base class for all API response DTOs.

    Properties:
    ----------
    - **Immutable**: frozen=True prevents accidental modification of API data
    - **Type-Safe**: All response fields validated against schema
    - **Timestamped**: Auto-set created_at field for audit trails
    - **Read-Only**: Once parsed, response data cannot be changed

    Usage:
    -----
    Response DTOs represent data RECEIVED from the API.
    They are immutable to prevent code from accidentally modifying API data.

    Example:
        >>> class GetDevicesResponse(ResponseDTO):
        ...     devices: List[Device]
        >>>
        >>> response = GetDevicesResponse(devices=[...])
        >>> response.devices.append(...)  # ❌ FrozenInstanceError
    """

    # Auto-set timestamp when response was created
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        frozen=True,  # Immutable - read-only API data
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class DomainModel(BaseDTOModel):
    """
    Base class for reusable domain-specific models.

    Properties:
    ----------
    - **Mutable**: NOT frozen, allows use in different contexts
    - **Shareable**: Can be used in both request and response DTOs
    - **Flexible**: Not all domain models need to be immutable
    - **Composable**: Can be nested in Request/Response DTOs

    Usage:
    -----
    Domain models represent business entities that might appear
    in both API requests and responses.

    Example:
        >>> class Device(DomainModel):
        ...     serial_number: str
        ...     online: bool
        >>>
        >>> # Can be used in requests
        >>> class PairDeviceRequest(RequestDTO):
        ...     device: Device
        >>>
        >>> # And in responses
        >>> class PairedDevicesResponse(ResponseDTO):
        ...     devices: List[Device]
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable - allows manipulation
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class APIErrorDTO(BaseDTOModel):
    """
    Standard API error response format.

    Represents errors returned from API endpoints.
    Provides structured error information for proper handling.

    Attributes:
    -----------
    success : bool
        Always False for error responses (marker field)
    error : str
        Human-readable error message
    error_code : str, optional
        Machine-readable error code (e.g., 'AUTH_ERROR', 'NOT_FOUND')
    details : dict, optional
        Additional error context/metadata
    field_errors : dict, optional
        Field-level validation errors {field_name: error_message}

    Example:
        >>> error = APIErrorDTO(
        ...     error="Device not found",
        ...     error_code="NOT_FOUND",
        ...     details={"device_id": "UNKNOWN123"}
        ... )
        >>> print(f"{error.error_code}: {error.error}")
        NOT_FOUND: Device not found
    """

    success: bool = False  # Always False for errors
    error: str  # Main error message
    error_code: Optional[str] = None  # Machine-readable code
    details: Optional[Dict[str, Any]] = None  # Additional context
    field_errors: Optional[Dict[str, str]] = None  # Field-level errors

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "success": False,
                    "error": "Device not found",
                    "error_code": "NOT_FOUND",
                    "details": {"device_id": "UNKNOWN123"},
                }
            ]
        },
    )


class APISuccessResponse(BaseDTOModel, Generic[T]):
    """
    Generic success response wrapper for API responses.

    Type-safe generic wrapper that can contain any response data type.
    Useful for consistent response handling across the application.

    Type Parameters:
    ----------------
    T : TypeVar
        The type of data contained in the response

    Attributes:
    -----------
    success : bool
        Always True for success responses
    data : T
        The actual response data (typed, validated)
    message : str, optional
        Optional success message
    timestamp : datetime, optional
        Response timestamp

    Example:
        >>> # Generic usage with specific type
        >>> response: APISuccessResponse[GetDevicesResponse]
        >>> response = APISuccessResponse(
        ...     data=GetDevicesResponse(devices=[...]),
        ...     message="Successfully retrieved devices"
        ... )
        >>> devices = response.data.devices  # Fully typed!
    """

    success: bool = True  # Always True for success
    data: T  # Generic response data
    message: Optional[str] = None  # Optional success message
    timestamp: Optional[datetime] = None  # Optional timestamp

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )


class ValidationErrorDetail(BaseDTOModel):
    """
    Detailed field-level validation error information.

    Provides structured information about individual field validation failures.
    Useful for generating user-friendly error messages.

    Attributes:
    -----------
    field : str
        The field name that failed validation
    message : str
        Human-readable error message
    value : Any, optional
        The invalid value that caused the error
    code : str
        Machine-readable error code (e.g., 'required', 'type_error', 'value_error')

    Error Codes:
    -----------
    - 'required': Required field is missing
    - 'type_error': Value type doesn't match expected type
    - 'value_error': Value fails custom validation
    - 'string_pattern': String doesn't match pattern
    - 'string_min_length': String too short
    - 'string_max_length': String too long
    - 'number_less_than_equal': Number exceeds maximum
    - 'number_greater_than_equal': Number below minimum

    Example:
        >>> error = ValidationErrorDetail(
        ...     field='duration',
        ...     message='Value must be between 1 and 3600',
        ...     value=4000,
        ...     code='value_error'
        ... )
        >>> print(f"{error.field}: {error.message}")
        duration: Value must be between 1 and 3600
    """

    field: str  # Field that failed validation
    message: str  # Error message
    value: Optional[Any] = None  # The invalid value
    code: str  # Error code

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "field": "duration",
                    "message": "Value must be between 1 and 3600",
                    "value": 4000,
                    "code": "value_error",
                }
            ]
        },
    )


# Utility type aliases for common DTO patterns
class EmptyRequest(RequestDTO):
    """Utility: For GET requests that have no body"""

    pass


class SimpleSuccessResponse(ResponseDTO):
    """Utility: For simple success-only responses"""

    success: bool = Field(default=True)


__all__ = [
    "BaseDTOModel",
    "RequestDTO",
    "ResponseDTO",
    "DomainModel",
    "APIErrorDTO",
    "APISuccessResponse",
    "ValidationErrorDetail",
    "T",  # Type variable for generics
]
