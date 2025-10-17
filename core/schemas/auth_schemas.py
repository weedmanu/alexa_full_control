"""
Authentication-Related Data Transfer Objects (DTOs)

Phase 3.5b - Auth Schemas Implementation

Models:
- LoginRequest: User credentials for authentication
- LoginResponse: Response from authentication endpoint
- SessionDTO: Session information and metadata
- TokenDTO: Access token with expiration
- RefreshTokenRequest: Token refresh request

API Endpoints:
- POST /auth/login: User login
- POST /auth/refresh: Refresh access token
- GET /auth/session: Check session status

Authentication Flow:
1. Client sends LoginRequest (username, password)
2. Server validates and returns LoginResponse with SessionDTO + TokenDTO
3. Client uses TokenDTO access_token for API calls
4. When token expires, client sends RefreshTokenRequest
5. Server returns new TokenDTO

Field Mapping (camelCase → snake_case):
- sessionId → session_id
- expiresAt → expires_at
- deviceId → device_id
- access_token → access_token
- token_type → token_type
- refresh_token → refresh_token
- expires_in → expires_in

Example Amazon Auth Response:
{
    "sessionId": "SESSION_ABC123",
    "token": "TOKEN_XYZ789",
    "expiresAt": "2025-10-17T18:00:00Z",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600
}
"""

from typing import Optional
from datetime import datetime, timedelta, timezone
from pydantic import Field, field_validator

from core.schemas.base import (
    RequestDTO,
    ResponseDTO,
    DomainModel,
)


class LoginRequest(RequestDTO):
    """
    Authentication request with user credentials.
    
    Sent by client to authenticate with Alexa API.
    
    Attributes:
        username: User email or username
        password: User password (plaintext - should be sent over HTTPS)
        device_id: Optional device identifier for session binding
    
    Example:
        >>> request = LoginRequest(
        ...     username="user@example.com",
        ...     password="securepass123"
        ... )
    """

    username: str = Field(..., min_length=1, description="User email or username")
    password: str = Field(..., min_length=1, description="User password")
    device_id: Optional[str] = Field(None, alias="deviceId", description="Optional device ID")

    @field_validator("username", "password", mode="before")
    @classmethod
    def validate_not_empty_strings(cls, v: str) -> str:
        """Reject 'None' string values."""
        if v == "None":
            raise ValueError("Field cannot be 'None' string")
        return v


class SessionDTO(DomainModel):
    """
    Session information for authenticated user.
    
    Represents an authenticated session with expiration.
    Used to manage user sessions and their lifecycle.
    
    Attributes:
        session_id: Unique session identifier
        token: Session token for API calls
        expires_at: Absolute expiration timestamp
        device_id: Optional associated device
    
    Example:
        >>> session = SessionDTO(
        ...     sessionId="SESSION_ABC",
        ...     token="TOKEN_XYZ",
        ...     expiresAt=datetime.utcnow() + timedelta(hours=1)
        ... )
        >>> session.is_expired()
        False
    """

    session_id: str = Field(..., alias="sessionId", min_length=1)
    token: str = Field(..., min_length=1)
    expires_at: datetime = Field(..., alias="expiresAt")
    device_id: Optional[str] = Field(None, alias="deviceId")

    @field_validator("session_id", "token", mode="before")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Reject 'None' string values."""
        if v == "None":
            raise ValueError("Field cannot be 'None' string")
        return v

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) >= self.expires_at


class TokenDTO(ResponseDTO):
    """
    OAuth2-style access token with expiration.
    
    Represents an access token for API authentication.
    Tracks expiration time (absolute or relative).
    
    Attributes:
        access_token: The access token string (JWT or opaque)
        token_type: Token type (default: "Bearer")
        expires_in: Seconds until expiration (optional, relative)
        refresh_token: Token to refresh this token
    
    Example:
        >>> token = TokenDTO(
        ...     access_token="eyJhbGciOiJIUzI1NiIs...",
        ...     expires_in=3600
        ... )
        >>> token.is_valid()
        True
    """

    access_token: str = Field(..., min_length=1, description="OAuth2 access token")
    token_type: str = Field(default="Bearer", description="Token type (Bearer, etc)")
    expires_in: Optional[int] = Field(None, description="Seconds until expiration")
    refresh_token: Optional[str] = Field(None, description="Token for refreshing")

    @field_validator("access_token", mode="before")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Reject 'None' string values."""
        if v == "None":
            raise ValueError("Field cannot be 'None' string")
        return v

    def get_expiration(self) -> Optional[datetime]:
        """Calculate absolute expiration time."""
        if self.expires_in is None:
            return None
        # created_at is from ResponseDTO base class
        return self.created_at + timedelta(seconds=self.expires_in)

    def is_valid(self) -> bool:
        """Check if token is still valid (not expired)."""
        if self.expires_in is None:
            return True  # No expiration info, assume valid
        expiration = self.get_expiration()
        if expiration is None:
            return True
        # Add 5-second buffer for clock skew
        return datetime.now(timezone.utc) < (expiration - timedelta(seconds=5))


class LoginResponse(ResponseDTO):
    """
    Response from authentication endpoint.
    
    Contains session and token information after successful login.
    May contain error information if login failed.
    
    Attributes:
        success: Whether authentication was successful
        session: Session information (if success)
        token: Access token (if success)
        error: Error message (if failed)
        error_code: Machine-readable error code
    
    Example:
        >>> response = LoginResponse(
        ...     success=True,
        ...     session={"sessionId": "S1", "token": "T1", "expiresAt": ...},
        ...     token={"access_token": "TOKEN123"}
        ... )
    """

    success: bool = Field(..., description="Whether login was successful")
    session: Optional[SessionDTO] = Field(None, description="Session info if successful")
    token: Optional[TokenDTO] = Field(None, description="Access token if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")

    def is_authenticated(self) -> bool:
        """Check if login was successful and session is valid."""
        if not self.success or self.session is None:
            return False
        return not self.session.is_expired()

    def is_token_valid(self) -> bool:
        """Check if returned token is still valid."""
        if self.token is None:
            return False
        return self.token.is_valid()


class RefreshTokenRequest(RequestDTO):
    """
    Request to refresh an expired access token.
    
    Sent by client when access token has expired.
    Uses refresh_token to obtain a new access_token.
    
    Attributes:
        refresh_token: Token used to refresh access token
        device_id: Optional device identifier
    
    Example:
        >>> request = RefreshTokenRequest(
        ...     refresh_token="REFRESH_TOKEN_123"
        ... )
    """

    refresh_token: str = Field(..., min_length=1, description="Token to refresh access token")
    device_id: Optional[str] = Field(None, alias="deviceId", description="Optional device ID")

    @field_validator("refresh_token", mode="before")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Reject 'None' string values."""
        if v == "None":
            raise ValueError("Field cannot be 'None' string")
        return v


__all__ = [
    "LoginRequest",
    "LoginResponse",
    "SessionDTO",
    "TokenDTO",
    "RefreshTokenRequest",
]
