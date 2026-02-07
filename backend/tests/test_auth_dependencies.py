# Task: T-006 - Create Auth Dependencies
# Spec: specs/task-crud/spec.md
"""
Tests for authentication dependencies.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.jwt import JWTPayload
from app.auth.dependencies import (
    get_current_user,
    get_current_user_optional,
    verify_user_access,
    CurrentUser,
    OptionalUser,
)


# Test secret for JWT tests
TEST_SECRET = "a" * 32


@pytest.fixture
def mock_settings():
    """Mock settings for tests."""
    with patch("app.auth.jwt.settings") as mock:
        mock.BETTER_AUTH_SECRET = TEST_SECRET
        mock.JWT_ALGORITHM = "HS256"
        yield mock


@pytest.fixture
def valid_jwt_payload():
    """Create a valid JWTPayload for testing."""
    return JWTPayload(
        user_id="user_123",
        email="test@example.com",
        exp=datetime.utcnow() + timedelta(hours=1),
        iat=datetime.utcnow(),
    )


@pytest.fixture
def valid_credentials(mock_settings):
    """Create valid HTTP credentials with a real token."""
    import jwt

    payload = {
        "sub": "user_123",
        "email": "test@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")

    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


@pytest.fixture
def expired_credentials(mock_settings):
    """Create expired HTTP credentials."""
    import jwt

    payload = {
        "sub": "user_123",
        "email": "test@example.com",
        "iat": datetime.utcnow() - timedelta(hours=2),
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")

    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


@pytest.fixture
def other_user_credentials(mock_settings):
    """Create credentials for a different user."""
    import jwt

    payload = {
        "sub": "other_user_456",
        "email": "other@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")

    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_payload(self, valid_credentials, mock_settings):
        """Test that valid token returns JWTPayload."""
        result = await get_current_user(valid_credentials)

        assert isinstance(result, JWTPayload)
        assert result.user_id == "user_123"
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self, expired_credentials, mock_settings):
        """Test that expired token raises 401."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(expired_credentials)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self, mock_settings):
        """Test that invalid token raises 401."""
        invalid_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here",
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(invalid_credentials)

        assert exc_info.value.status_code == 401


class TestGetCurrentUserOptional:
    """Tests for get_current_user_optional dependency."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_payload(self, valid_credentials, mock_settings):
        """Test that valid token returns JWTPayload."""
        result = await get_current_user_optional(valid_credentials)

        assert isinstance(result, JWTPayload)
        assert result.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_no_token_returns_none(self, mock_settings):
        """Test that no token returns None."""
        result = await get_current_user_optional(None)

        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self, mock_settings):
        """Test that invalid token still raises 401."""
        invalid_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here",
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_optional(invalid_credentials)

        assert exc_info.value.status_code == 401


class TestVerifyUserAccess:
    """Tests for verify_user_access dependency."""

    @pytest.mark.asyncio
    async def test_matching_user_id_succeeds(self, valid_jwt_payload):
        """Test that matching user_id allows access."""
        result = await verify_user_access(
            user_id="user_123",
            current_user=valid_jwt_payload,
        )

        assert result == valid_jwt_payload
        assert result.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_mismatched_user_id_raises_403(self, valid_jwt_payload):
        """Test that mismatched user_id raises 403."""
        with pytest.raises(HTTPException) as exc_info:
            await verify_user_access(
                user_id="different_user",
                current_user=valid_jwt_payload,
            )

        assert exc_info.value.status_code == 403
        assert "access denied" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_empty_user_id_raises_403(self, valid_jwt_payload):
        """Test that empty user_id raises 403."""
        with pytest.raises(HTTPException) as exc_info:
            await verify_user_access(
                user_id="",
                current_user=valid_jwt_payload,
            )

        assert exc_info.value.status_code == 403


class TestVerifyUserAccessIntegration:
    """Integration tests for verify_user_access with real tokens."""

    @pytest.mark.asyncio
    async def test_full_flow_matching_user(self, valid_credentials, mock_settings):
        """Test full authentication and authorization flow with matching user."""
        # First, authenticate
        current_user = await get_current_user(valid_credentials)

        # Then, verify access
        result = await verify_user_access(
            user_id="user_123",
            current_user=current_user,
        )

        assert result.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_full_flow_different_user(self, valid_credentials, mock_settings):
        """Test full flow rejects access to different user's resources."""
        # Authenticate as user_123
        current_user = await get_current_user(valid_credentials)

        # Try to access user_456's resources
        with pytest.raises(HTTPException) as exc_info:
            await verify_user_access(
                user_id="user_456",
                current_user=current_user,
            )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_user_isolation(
        self,
        valid_credentials,
        other_user_credentials,
        mock_settings,
    ):
        """Test that users are properly isolated."""
        # User 123 authenticates
        user_123 = await get_current_user(valid_credentials)
        assert user_123.user_id == "user_123"

        # User 456 authenticates
        user_456 = await get_current_user(other_user_credentials)
        assert user_456.user_id == "other_user_456"

        # User 123 can access their own resources
        result = await verify_user_access(user_id="user_123", current_user=user_123)
        assert result.user_id == "user_123"

        # User 123 cannot access user 456's resources
        with pytest.raises(HTTPException) as exc_info:
            await verify_user_access(user_id="other_user_456", current_user=user_123)
        assert exc_info.value.status_code == 403

        # User 456 can access their own resources
        result = await verify_user_access(
            user_id="other_user_456",
            current_user=user_456,
        )
        assert result.user_id == "other_user_456"

        # User 456 cannot access user 123's resources
        with pytest.raises(HTTPException) as exc_info:
            await verify_user_access(user_id="user_123", current_user=user_456)
        assert exc_info.value.status_code == 403


class TestTypeAliases:
    """Tests for type aliases."""

    def test_current_user_type_alias_exists(self):
        """Test that CurrentUser type alias is defined."""
        assert CurrentUser is not None

    def test_optional_user_type_alias_exists(self):
        """Test that OptionalUser type alias is defined."""
        assert OptionalUser is not None
