# Task: T-005 - Implement JWT Verification
# Spec: specs/task-crud/spec.md
"""
Tests for JWT token verification.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
from fastapi import HTTPException

from app.auth.jwt import (
    JWTPayload,
    TokenExpiredError,
    InvalidTokenError,
    decode_jwt_token,
    extract_user_id,
    parse_jwt_payload,
    verify_jwt_token,
    create_test_token,
)


# Test secret for JWT tests
TEST_SECRET = "a" * 32  # 32 character secret


@pytest.fixture
def mock_settings():
    """Mock settings for JWT tests."""
    with patch("app.auth.jwt.settings") as mock:
        mock.BETTER_AUTH_SECRET = TEST_SECRET
        mock.JWT_ALGORITHM = "HS256"
        yield mock


@pytest.fixture
def valid_token(mock_settings):
    """Create a valid JWT token for testing."""
    payload = {
        "sub": "user_123",
        "email": "test@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


@pytest.fixture
def expired_token(mock_settings):
    """Create an expired JWT token for testing."""
    payload = {
        "sub": "user_123",
        "email": "test@example.com",
        "iat": datetime.utcnow() - timedelta(hours=2),
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


class TestJWTPayload:
    """Tests for JWTPayload dataclass."""

    def test_jwt_payload_creation(self):
        """Test creating a JWTPayload."""
        exp = datetime.utcnow() + timedelta(hours=1)
        payload = JWTPayload(
            user_id="user_123",
            email="test@example.com",
            exp=exp,
        )

        assert payload.user_id == "user_123"
        assert payload.email == "test@example.com"
        assert payload.exp == exp
        assert payload.iat is None
        assert payload.raw is None

    def test_jwt_payload_is_expired_false(self):
        """Test is_expired returns False for valid token."""
        exp = datetime.utcnow() + timedelta(hours=1)
        payload = JWTPayload(
            user_id="user_123",
            email="test@example.com",
            exp=exp,
        )

        assert payload.is_expired() is False

    def test_jwt_payload_is_expired_true(self):
        """Test is_expired returns True for expired token."""
        exp = datetime.utcnow() - timedelta(hours=1)
        payload = JWTPayload(
            user_id="user_123",
            email="test@example.com",
            exp=exp,
        )

        assert payload.is_expired() is True

    def test_jwt_payload_repr(self):
        """Test JWTPayload string representation."""
        payload = JWTPayload(
            user_id="user_123",
            email="test@example.com",
            exp=datetime.utcnow(),
        )

        repr_str = repr(payload)
        assert "user_123" in repr_str
        assert "test@example.com" in repr_str


class TestDecodeJWTToken:
    """Tests for decode_jwt_token function."""

    def test_decode_valid_token(self, mock_settings, valid_token):
        """Test decoding a valid token."""
        payload = decode_jwt_token(valid_token)

        assert payload["sub"] == "user_123"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_decode_expired_token_raises_error(self, mock_settings, expired_token):
        """Test that expired token raises TokenExpiredError."""
        with pytest.raises(TokenExpiredError) as exc_info:
            decode_jwt_token(expired_token)

        assert "expired" in str(exc_info.value).lower()

    def test_decode_invalid_signature_raises_error(self, mock_settings):
        """Test that invalid signature raises InvalidTokenError."""
        # Create token with different secret
        payload = {
            "sub": "user_123",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        wrong_secret_token = jwt.encode(payload, "wrong_secret_key_32_chars_long!!", algorithm="HS256")

        with pytest.raises(InvalidTokenError) as exc_info:
            decode_jwt_token(wrong_secret_token)

        assert "signature" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_decode_malformed_token_raises_error(self, mock_settings):
        """Test that malformed token raises InvalidTokenError."""
        with pytest.raises(InvalidTokenError):
            decode_jwt_token("not.a.valid.token")

    def test_decode_empty_token_raises_error(self, mock_settings):
        """Test that empty token raises InvalidTokenError."""
        with pytest.raises(InvalidTokenError):
            decode_jwt_token("")


class TestExtractUserId:
    """Tests for extract_user_id function."""

    def test_extract_user_id_from_sub(self):
        """Test extracting user_id from 'sub' claim."""
        payload = {"sub": "user_123", "email": "test@example.com"}
        user_id = extract_user_id(payload)

        assert user_id == "user_123"

    def test_extract_user_id_from_user_id_claim(self):
        """Test extracting user_id from 'user_id' claim."""
        payload = {"user_id": "user_456", "email": "test@example.com"}
        user_id = extract_user_id(payload)

        assert user_id == "user_456"

    def test_extract_user_id_from_userId_claim(self):
        """Test extracting user_id from 'userId' claim (camelCase)."""
        payload = {"userId": "user_789", "email": "test@example.com"}
        user_id = extract_user_id(payload)

        assert user_id == "user_789"

    def test_extract_user_id_from_id_claim(self):
        """Test extracting user_id from 'id' claim."""
        payload = {"id": "user_abc", "email": "test@example.com"}
        user_id = extract_user_id(payload)

        assert user_id == "user_abc"

    def test_extract_user_id_prefers_sub(self):
        """Test that 'sub' is preferred over other claims."""
        payload = {
            "sub": "user_sub",
            "user_id": "user_other",
            "email": "test@example.com",
        }
        user_id = extract_user_id(payload)

        assert user_id == "user_sub"

    def test_extract_user_id_missing_raises_error(self):
        """Test that missing user_id raises InvalidTokenError."""
        payload = {"email": "test@example.com"}

        with pytest.raises(InvalidTokenError) as exc_info:
            extract_user_id(payload)

        assert "No user ID found" in str(exc_info.value)

    def test_extract_user_id_converts_to_string(self):
        """Test that numeric user_id is converted to string."""
        payload = {"sub": 12345}
        user_id = extract_user_id(payload)

        assert user_id == "12345"
        assert isinstance(user_id, str)


class TestParseJWTPayload:
    """Tests for parse_jwt_payload function."""

    def test_parse_complete_payload(self):
        """Test parsing a complete JWT payload."""
        now = datetime.utcnow()
        exp = now + timedelta(hours=1)
        raw_payload = {
            "sub": "user_123",
            "email": "test@example.com",
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }

        payload = parse_jwt_payload(raw_payload)

        assert payload.user_id == "user_123"
        assert payload.email == "test@example.com"
        assert payload.iat is not None
        assert payload.exp is not None
        assert payload.raw == raw_payload

    def test_parse_payload_without_email(self):
        """Test parsing payload without email defaults to empty string."""
        exp = datetime.utcnow() + timedelta(hours=1)
        raw_payload = {
            "sub": "user_123",
            "exp": int(exp.timestamp()),
        }

        payload = parse_jwt_payload(raw_payload)

        assert payload.email == ""

    def test_parse_payload_without_iat(self):
        """Test parsing payload without iat is None."""
        exp = datetime.utcnow() + timedelta(hours=1)
        raw_payload = {
            "sub": "user_123",
            "exp": int(exp.timestamp()),
        }

        payload = parse_jwt_payload(raw_payload)

        assert payload.iat is None

    def test_parse_payload_missing_exp_raises_error(self):
        """Test that missing exp raises InvalidTokenError."""
        raw_payload = {"sub": "user_123"}

        with pytest.raises(InvalidTokenError) as exc_info:
            parse_jwt_payload(raw_payload)

        assert "expiration" in str(exc_info.value).lower()


class TestVerifyJWTToken:
    """Tests for verify_jwt_token function."""

    def test_verify_valid_token(self, mock_settings, valid_token):
        """Test verifying a valid token."""
        payload = verify_jwt_token(valid_token)

        assert isinstance(payload, JWTPayload)
        assert payload.user_id == "user_123"
        assert payload.email == "test@example.com"

    def test_verify_token_with_bearer_prefix(self, mock_settings, valid_token):
        """Test verifying token with 'Bearer ' prefix."""
        token_with_prefix = f"Bearer {valid_token}"
        payload = verify_jwt_token(token_with_prefix)

        assert payload.user_id == "user_123"

    def test_verify_expired_token_raises_401(self, mock_settings, expired_token):
        """Test that expired token raises 401 HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(expired_token)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    def test_verify_invalid_token_raises_401(self, mock_settings):
        """Test that invalid token raises 401 HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token("invalid.token.here")

        assert exc_info.value.status_code == 401
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    def test_verify_wrong_signature_raises_401(self, mock_settings):
        """Test that wrong signature raises 401 HTTPException."""
        payload = {
            "sub": "user_123",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        wrong_secret_token = jwt.encode(payload, "wrong_secret_key_32_chars_long!!", algorithm="HS256")

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(wrong_secret_token)

        assert exc_info.value.status_code == 401

    def test_verify_empty_token_raises_401(self, mock_settings):
        """Test that empty token raises 401 HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token("")

        assert exc_info.value.status_code == 401


class TestCreateTestToken:
    """Tests for create_test_token helper function."""

    def test_create_test_token(self, mock_settings):
        """Test creating a test token."""
        token = create_test_token(user_id="test_user")

        # Verify token can be decoded
        payload = verify_jwt_token(token)

        assert payload.user_id == "test_user"
        assert payload.email == "test@example.com"

    def test_create_test_token_custom_email(self, mock_settings):
        """Test creating a test token with custom email."""
        token = create_test_token(
            user_id="test_user",
            email="custom@example.com",
        )

        payload = verify_jwt_token(token)

        assert payload.email == "custom@example.com"

    def test_create_test_token_custom_expiry(self, mock_settings):
        """Test creating a test token with custom expiry."""
        token = create_test_token(
            user_id="test_user",
            expires_in_seconds=60,  # 1 minute
        )

        payload = verify_jwt_token(token)

        # Token should expire within 2 minutes
        time_until_expiry = payload.exp - datetime.utcnow()
        assert time_until_expiry.total_seconds() <= 120
