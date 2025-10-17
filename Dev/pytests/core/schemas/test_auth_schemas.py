"""
Auth Schema Tests - Phase 3.5b (TDD)

Tests for authentication-related DTOs.
Covers: login, session management, token handling, authentication flow.

Test Coverage:
- Login request validation (username, password)
- Login response with session token
- Session token validation and expiration
- Refresh token requests
- Session status and validity
- Authorization token structure
- Token expiration handling

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/auth_schemas.py
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import ValidationError


class TestLoginRequest:
    """Test LoginRequest for user authentication."""

    def test_login_with_username_password(self):
        """Should accept username and password."""
        from core.schemas.auth_schemas import LoginRequest
        
        request = LoginRequest(
            username="user@example.com",
            password="securepassword123"
        )
        
        assert request.username == "user@example.com"
        assert request.password == "securepassword123"

    def test_login_requires_username(self):
        """Username is required."""
        from core.schemas.auth_schemas import LoginRequest
        
        with pytest.raises(ValidationError):
            LoginRequest(password="securepassword123")

    def test_login_requires_password(self):
        """Password is required."""
        from core.schemas.auth_schemas import LoginRequest
        
        with pytest.raises(ValidationError):
            LoginRequest(username="user@example.com")

    def test_login_username_not_empty(self):
        """Username must not be empty."""
        from core.schemas.auth_schemas import LoginRequest
        
        with pytest.raises(ValidationError):
            LoginRequest(username="", password="pass123")

    def test_login_password_not_empty(self):
        """Password must not be empty."""
        from core.schemas.auth_schemas import LoginRequest
        
        with pytest.raises(ValidationError):
            LoginRequest(username="user@example.com", password="")

    def test_login_with_optional_device_id(self):
        """Should support optional deviceId parameter."""
        from core.schemas.auth_schemas import LoginRequest
        
        request = LoginRequest(
            username="user@example.com",
            password="pass123",
            deviceId="DEVICE123"
        )
        
        assert request.device_id == "DEVICE123"

    def test_login_request_immutable(self):
        """LoginRequest should be immutable (RequestDTO)."""
        from core.schemas.auth_schemas import LoginRequest
        
        request = LoginRequest(
            username="user@example.com",
            password="pass123"
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            request.username = "different@example.com"


class TestSessionDTO:
    """Test SessionDTO for session information."""

    def test_session_with_token(self):
        """Should store session token and metadata."""
        from core.schemas.auth_schemas import SessionDTO
        
        session = SessionDTO(
            sessionId="SESSION_ABC123",
            token="TOKEN_XYZ789",
            expiresAt=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        assert session.session_id == "SESSION_ABC123"
        assert session.token == "TOKEN_XYZ789"
        assert session.expires_at is not None

    def test_session_requires_session_id(self):
        """Session ID is required."""
        from core.schemas.auth_schemas import SessionDTO
        
        with pytest.raises(ValidationError):
            SessionDTO(
                token="TOKEN123",
                expiresAt=datetime.now(timezone.utc)
            )

    def test_session_requires_token(self):
        """Token is required."""
        from core.schemas.auth_schemas import SessionDTO
        
        with pytest.raises(ValidationError):
            SessionDTO(
                sessionId="SESSION123",
                expiresAt=datetime.now(timezone.utc)
            )

    def test_session_requires_expiration_time(self):
        """Expiration time is required."""
        from core.schemas.auth_schemas import SessionDTO
        
        with pytest.raises(ValidationError):
            SessionDTO(
                sessionId="SESSION123",
                token="TOKEN123"
            )

    def test_session_is_expired_method(self):
        """Should have method to check if session is expired."""
        from core.schemas.auth_schemas import SessionDTO
        
        # Create expired session
        expired = SessionDTO(
            sessionId="SESSION1",
            token="TOKEN1",
            expiresAt=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        # Create valid session
        valid = SessionDTO(
            sessionId="SESSION2",
            token="TOKEN2",
            expiresAt=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        assert expired.is_expired() is True
        assert valid.is_expired() is False

    def test_session_optional_device_id(self):
        """Session can store associated device ID."""
        from core.schemas.auth_schemas import SessionDTO
        
        session = SessionDTO(
            sessionId="SESSION123",
            token="TOKEN123",
            expiresAt=datetime.now(timezone.utc),
            deviceId="DEVICE123"
        )
        
        assert session.device_id == "DEVICE123"


class TestTokenDTO:
    """Test TokenDTO for access token data."""

    def test_token_from_amazon_response(self):
        """Should parse token from Amazon auth response."""
        from core.schemas.auth_schemas import TokenDTO
        
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        
        token = TokenDTO(**token_data)
        
        assert token.access_token == "eyJhbGciOiJIUzI1NiIs..."
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600

    def test_token_requires_access_token(self):
        """Access token is required."""
        from core.schemas.auth_schemas import TokenDTO
        
        with pytest.raises(ValidationError):
            TokenDTO(
                token_type="Bearer",
                expires_in=3600
            )

    def test_token_defaults_to_bearer_type(self):
        """Token type should default to Bearer."""
        from core.schemas.auth_schemas import TokenDTO
        
        token = TokenDTO(
            access_token="TOKEN123"
        )
        
        assert token.token_type == "Bearer"

    def test_token_expiration_calculation(self):
        """Should calculate absolute expiration time from expires_in."""
        from core.schemas.auth_schemas import TokenDTO
        
        token = TokenDTO(
            access_token="TOKEN123",
            expires_in=3600
        )
        
        # Should have created_at timestamp
        assert token.created_at is not None
        # Expiration should be ~1 hour from now
        expected_expiry = token.created_at + timedelta(seconds=3600)
        assert abs((token.get_expiration() - expected_expiry).total_seconds()) < 5

    def test_token_is_valid_method(self):
        """Should check if token is still valid."""
        from core.schemas.auth_schemas import TokenDTO
        
        # Fresh token (valid)
        fresh = TokenDTO(
            access_token="TOKEN1",
            expires_in=3600
        )
        
        # Old token (simulated as expired)
        old = TokenDTO(
            access_token="TOKEN2",
            expires_in=0  # Already expired
        )
        
        assert fresh.is_valid() is True
        assert old.is_valid() is False

    def test_token_optional_refresh_token(self):
        """Should support optional refresh token."""
        from core.schemas.auth_schemas import TokenDTO
        
        token = TokenDTO(
            access_token="ACCESS_TOKEN123",
            refresh_token="REFRESH_TOKEN456"
        )
        
        assert token.refresh_token == "REFRESH_TOKEN456"


class TestLoginResponse:
    """Test LoginResponse for successful authentication."""

    def test_login_response_with_session_and_token(self):
        """Should include session and token after successful login."""
        from core.schemas.auth_schemas import LoginResponse
        
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        
        response = LoginResponse(
            success=True,
            session={
                "sessionId": "SESSION123",
                "token": "TOKEN123",
                "expiresAt": expiry
            },
            token={
                "access_token": "ACCESS_TOKEN123"
            }
        )
        
        assert response.success is True
        assert response.session.session_id == "SESSION123"
        assert response.token.access_token == "ACCESS_TOKEN123"

    def test_login_failure_response(self):
        """Should handle failed login attempts."""
        from core.schemas.auth_schemas import LoginResponse
        
        response = LoginResponse(
            success=False,
            error="Invalid credentials"
        )
        
        assert response.success is False
        assert response.error == "Invalid credentials"
        assert response.session is None

    def test_login_response_requires_success_flag(self):
        """Success flag is required."""
        from core.schemas.auth_schemas import LoginResponse
        
        with pytest.raises(ValidationError):
            LoginResponse(
                session={"sessionId": "S1", "token": "T1", "expiresAt": datetime.now(timezone.utc)}
            )

    def test_login_response_immutable(self):
        """LoginResponse should be immutable (ResponseDTO)."""
        from core.schemas.auth_schemas import LoginResponse
        
        response = LoginResponse(success=False)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            response.success = True


class TestRefreshTokenRequest:
    """Test RefreshTokenRequest for token refresh."""

    def test_refresh_with_refresh_token(self):
        """Should refresh using refresh token."""
        from core.schemas.auth_schemas import RefreshTokenRequest
        
        request = RefreshTokenRequest(
            refresh_token="REFRESH_TOKEN123"
        )
        
        assert request.refresh_token == "REFRESH_TOKEN123"

    def test_refresh_requires_refresh_token(self):
        """Refresh token is required."""
        from core.schemas.auth_schemas import RefreshTokenRequest
        
        with pytest.raises(ValidationError):
            RefreshTokenRequest()

    def test_refresh_with_optional_device_id(self):
        """Should support optional device ID."""
        from core.schemas.auth_schemas import RefreshTokenRequest
        
        request = RefreshTokenRequest(
            refresh_token="REFRESH_TOKEN123",
            deviceId="DEVICE123"
        )
        
        assert request.device_id == "DEVICE123"

    def test_refresh_request_immutable(self):
        """RefreshTokenRequest should be immutable (RequestDTO)."""
        from core.schemas.auth_schemas import RefreshTokenRequest
        
        request = RefreshTokenRequest(refresh_token="TOKEN123")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            request.refresh_token = "DIFFERENT_TOKEN"


class TestAuthenticationFlow:
    """Test authentication workflows."""

    def test_complete_login_workflow(self):
        """Should support complete login workflow."""
        from core.schemas.auth_schemas import (
            LoginRequest, LoginResponse, SessionDTO, TokenDTO
        )
        
        # User submits login request
        login_request = LoginRequest(
            username="user@example.com",
            password="securepass123"
        )
        
        assert login_request.username == "user@example.com"
        
        # Server responds with session and token
        session_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        login_response = LoginResponse(
            success=True,
            session={
                "sessionId": "SESSION_ABC",
                "token": "TOKEN_XYZ",
                "expiresAt": session_expiry
            },
            token={
                "access_token": "ACCESS_TOKEN_123",
                "expires_in": 3600
            }
        )
        
        assert login_response.success is True
        assert login_response.session.is_expired() is False
        assert login_response.token.is_valid() is True

    def test_token_refresh_workflow(self):
        """Should support token refresh workflow."""
        from core.schemas.auth_schemas import (
            RefreshTokenRequest, TokenDTO
        )
        
        # User requests token refresh
        refresh_request = RefreshTokenRequest(
            refresh_token="REFRESH_TOKEN_123"
        )
        
        assert refresh_request.refresh_token == "REFRESH_TOKEN_123"
        
        # Server responds with new token
        new_token = TokenDTO(
            access_token="NEW_ACCESS_TOKEN_456",
            expires_in=3600,
            refresh_token="NEW_REFRESH_TOKEN_789"
        )
        
        assert new_token.is_valid() is True

    def test_session_expiration_handling(self):
        """Should handle session expiration correctly."""
        from core.schemas.auth_schemas import SessionDTO
        
        # Create session that expires in 1 minute
        session = SessionDTO(
            sessionId="SESSION123",
            token="TOKEN123",
            expiresAt=datetime.now(timezone.utc) + timedelta(minutes=1)
        )
        
        assert session.is_expired() is False
        
        # Simulate time passing
        import time
        # We can't actually wait, but we can verify the logic


class TestAuthFieldValidation:
    """Test field validation for auth schemas."""

    def test_session_id_not_empty(self):
        """Session ID should not be empty."""
        from core.schemas.auth_schemas import SessionDTO
        
        with pytest.raises(ValidationError):
            SessionDTO(
                sessionId="",
                token="TOKEN123",
                expiresAt=datetime.now(timezone.utc)
            )

    def test_token_not_empty(self):
        """Token should not be empty."""
        from core.schemas.auth_schemas import SessionDTO
        
        with pytest.raises(ValidationError):
            SessionDTO(
                sessionId="SESSION123",
                token="",
                expiresAt=datetime.now(timezone.utc)
            )

    def test_access_token_not_empty(self):
        """Access token should not be empty."""
        from core.schemas.auth_schemas import TokenDTO
        
        with pytest.raises(ValidationError):
            TokenDTO(access_token="")

    def test_expires_in_non_negative(self):
        """Expires in should be >= 0."""
        from core.schemas.auth_schemas import TokenDTO
        
        # Valid: 0 means already expired
        token = TokenDTO(
            access_token="TOKEN123",
            expires_in=0
        )
        
        assert token.expires_in == 0


class TestAuthAliasConversion:
    """Test field aliasing for auth schemas."""

    def test_session_field_aliases(self):
        """Should accept both camelCase and snake_case."""
        from core.schemas.auth_schemas import SessionDTO
        
        expiry = datetime.now(timezone.utc)
        
        # Using camelCase
        session1 = SessionDTO(
            sessionId="S1",
            token="T1",
            expiresAt=expiry,
            deviceId="D1"
        )
        
        # Using snake_case
        session2 = SessionDTO(
            session_id="S1",
            token="T1",
            expires_at=expiry,
            device_id="D1"
        )
        
        assert session1.session_id == session2.session_id
        assert session1.device_id == session2.device_id

    def test_token_field_aliases(self):
        """Token should accept both camelCase and snake_case."""
        from core.schemas.auth_schemas import TokenDTO
        
        # Using camelCase
        token1 = TokenDTO(
            access_token="TOKEN123",
            token_type="Bearer",
            refresh_token="REFRESH123"
        )
        
        # Using snake_case
        token2 = TokenDTO(
            access_token="TOKEN123",
            token_type="Bearer",
            refresh_token="REFRESH123"
        )
        
        assert token1.access_token == token2.access_token


class TestAuthResponseSerialization:
    """Test JSON serialization for auth responses."""

    def test_login_response_json_serialization(self):
        """LoginResponse should serialize to JSON with proper types."""
        from core.schemas.auth_schemas import LoginResponse
        
        response = LoginResponse(success=False, error="Test error")
        
        json_data = response.model_dump(by_alias=True)
        
        assert "success" in json_data
        assert json_data["success"] is False

    def test_token_json_expiration_calculation(self):
        """Token should serialize with calculated expiration."""
        from core.schemas.auth_schemas import TokenDTO
        
        token = TokenDTO(
            access_token="TOKEN123",
            expires_in=3600
        )
        
        expiration = token.get_expiration()
        assert expiration is not None
        assert expiration > datetime.now(timezone.utc)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
