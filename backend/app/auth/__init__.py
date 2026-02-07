# Task: T-001 - Initialize Backend Project Structure
# Spec: specs/task-crud/spec.md
"""
Authentication package.

Contains JWT verification and auth dependencies.
"""

from app.auth.jwt import (
    JWTPayload,
    JWTError,
    TokenExpiredError,
    InvalidTokenError,
    verify_jwt_token,
    decode_jwt_token,
    create_test_token,
)

from app.auth.dependencies import (
    get_current_user,
    get_current_user_optional,
    verify_user_access,
    CurrentUser,
    OptionalUser,
    security,
)

__all__ = [
    # JWT
    "JWTPayload",
    "JWTError",
    "TokenExpiredError",
    "InvalidTokenError",
    "verify_jwt_token",
    "decode_jwt_token",
    "create_test_token",
    # Dependencies
    "get_current_user",
    "get_current_user_optional",
    "verify_user_access",
    "CurrentUser",
    "OptionalUser",
    "security",
]
