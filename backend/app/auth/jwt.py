# Task: T-005 - Implement JWT Verification
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
JWT token verification for Better Auth integration.

Verifies JWT tokens issued by Better Auth on the frontend
using the shared BETTER_AUTH_SECRET.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import jwt
from fastapi import HTTPException, status

from app.config import settings


@dataclass
class JWTPayload:
    """
    Decoded JWT payload structure.

    Contains the essential user information extracted from the JWT token.

    Attributes:
        user_id: The unique user identifier (from 'sub' or 'user_id' claim)
        email: User's email address (if present in token)
        exp: Token expiration datetime
        iat: Token issued at datetime (optional)
        raw: Raw payload dictionary for accessing additional claims
    """

    user_id: str
    email: str
    exp: datetime
    iat: Optional[datetime] = None
    raw: Optional[dict[str, Any]] = None

    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.utcnow() > self.exp

    def __repr__(self) -> str:
        return f"JWTPayload(user_id={self.user_id!r}, email={self.email!r})"


class JWTError(Exception):
    """Base exception for JWT-related errors."""

    pass


class TokenExpiredError(JWTError):
    """Raised when the JWT token has expired."""

    pass


class InvalidTokenError(JWTError):
    """Raised when the JWT token is invalid."""

    pass


def decode_jwt_token(token: str) -> dict[str, Any]:
    """
    Decode a JWT token without raising HTTP exceptions.

    Args:
        token: The JWT token string to decode

    Returns:
        Decoded payload dictionary

    Raises:
        TokenExpiredError: If the token has expired
        InvalidTokenError: If the token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["exp"],
            },
        )
        return payload

    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError(f"Token has expired: {e}") from e

    except jwt.InvalidSignatureError as e:
        raise InvalidTokenError(f"Invalid token signature: {e}") from e

    except jwt.DecodeError as e:
        raise InvalidTokenError(f"Token decode error: {e}") from e

    except jwt.InvalidTokenError as e:
        raise InvalidTokenError(f"Invalid token: {e}") from e


def extract_user_id(payload: dict[str, Any]) -> str:
    """
    Extract user ID from JWT payload.

    Checks multiple possible claim names for user ID:
    - 'sub' (standard JWT subject claim)
    - 'user_id' (custom claim)
    - 'userId' (camelCase variant)
    - 'id' (simple id claim)

    Args:
        payload: Decoded JWT payload dictionary

    Returns:
        User ID string

    Raises:
        InvalidTokenError: If no user ID claim is found
    """
    # Try different possible claim names for user ID
    user_id_claims = ["sub", "user_id", "userId", "id"]

    for claim in user_id_claims:
        user_id = payload.get(claim)
        if user_id is not None:
            return str(user_id)

    raise InvalidTokenError(
        f"No user ID found in token. Expected one of: {user_id_claims}"
    )


def parse_jwt_payload(payload: dict[str, Any]) -> JWTPayload:
    """
    Parse decoded JWT payload into JWTPayload object.

    Args:
        payload: Decoded JWT payload dictionary

    Returns:
        JWTPayload object with extracted data

    Raises:
        InvalidTokenError: If required claims are missing
    """
    # Extract user ID
    user_id = extract_user_id(payload)

    # Extract email (optional, default to empty string)
    email = payload.get("email", "")

    # Extract expiration (required)
    exp_timestamp = payload.get("exp")
    if exp_timestamp is None:
        raise InvalidTokenError("Token missing expiration claim")
    exp = datetime.utcfromtimestamp(exp_timestamp)

    # Extract issued at (optional)
    iat = None
    iat_timestamp = payload.get("iat")
    if iat_timestamp is not None:
        iat = datetime.utcfromtimestamp(iat_timestamp)

    return JWTPayload(
        user_id=user_id,
        email=email,
        exp=exp,
        iat=iat,
        raw=payload,
    )


def verify_jwt_token(token: str) -> JWTPayload:
    """
    Verify JWT token and return payload.

    This is the main function to use for JWT verification.
    It decodes the token, validates it, and returns a structured payload.

    Args:
        token: The JWT token string (without 'Bearer ' prefix)

    Returns:
        JWTPayload object containing user information

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or expired
    """
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        # Decode and validate token
        payload = decode_jwt_token(token)

        # Parse into structured payload
        return parse_jwt_payload(payload)

    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_test_token(
    user_id: str,
    email: str = "test@example.com",
    expires_in_seconds: int = 3600,
) -> str:
    """
    Create a test JWT token for testing purposes.

    WARNING: Only use this for testing, not in production.

    Args:
        user_id: User ID to include in token
        email: User email to include in token
        expires_in_seconds: Token validity duration in seconds

    Returns:
        Encoded JWT token string
    """
    from datetime import timedelta

    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in_seconds),
    }

    return jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
