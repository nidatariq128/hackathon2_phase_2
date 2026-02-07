# Task: T-006 - Create Auth Dependencies
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
FastAPI authentication dependencies.

Provides dependency injection functions for authenticating
and authorizing API requests using JWT tokens.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import JWTPayload, verify_jwt_token


# HTTPBearer security scheme for Swagger UI
# auto_error=True means it will raise 401 if no token is provided
security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token from Better Auth",
    auto_error=True,
)

# Optional security scheme (doesn't raise error if no token)
optional_security = HTTPBearer(
    scheme_name="JWT",
    description="Optional JWT token",
    auto_error=False,
)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> JWTPayload:
    """
    Dependency to get the current authenticated user from JWT token.

    Extracts the JWT token from the Authorization header,
    verifies it, and returns the decoded payload.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        JWTPayload: Decoded JWT payload with user information

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Usage:
        @router.get("/protected")
        async def protected_route(
            current_user: JWTPayload = Depends(get_current_user)
        ):
            return {"user_id": current_user.user_id}
    """
    return verify_jwt_token(credentials.credentials)


async def get_current_user_optional(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(optional_security)
    ],
) -> JWTPayload | None:
    """
    Dependency to optionally get the current user.

    Returns None if no token is provided, otherwise verifies
    the token and returns the payload.

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        JWTPayload | None: Decoded payload or None if no token

    Raises:
        HTTPException: 401 if token is provided but invalid

    Usage:
        @router.get("/maybe-protected")
        async def maybe_protected(
            current_user: JWTPayload | None = Depends(get_current_user_optional)
        ):
            if current_user:
                return {"user_id": current_user.user_id}
            return {"message": "anonymous"}
    """
    if credentials is None:
        return None
    return verify_jwt_token(credentials.credentials)


async def verify_user_access(
    user_id: str,
    current_user: Annotated[JWTPayload, Depends(get_current_user)],
) -> JWTPayload:
    """
    Dependency to verify user has access to the requested resource.

    Ensures the user_id in the URL path matches the authenticated
    user's ID from the JWT token. This prevents users from
    accessing other users' resources.

    Args:
        user_id: User ID from URL path parameter
        current_user: Authenticated user from JWT token

    Returns:
        JWTPayload: The authenticated user's payload (if authorized)

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user

    Usage:
        @router.get("/{user_id}/tasks")
        async def get_user_tasks(
            user_id: str,
            current_user: JWTPayload = Depends(verify_user_access)
        ):
            # current_user.user_id == user_id is guaranteed
            return await get_tasks_for_user(user_id)
    """
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources",
        )
    return current_user


def require_user_access(user_id: str):
    """
    Factory function to create a dependency that verifies user access.

    Alternative to verify_user_access when you need more control
    over how the user_id is obtained.

    Args:
        user_id: The user ID to check against

    Returns:
        Dependency function that verifies access

    Usage:
        @router.get("/special/{user_id}")
        async def special_route(
            user_id: str,
            current_user: JWTPayload = Depends(require_user_access(user_id))
        ):
            ...
    """
    async def _verify(
        current_user: Annotated[JWTPayload, Depends(get_current_user)],
    ) -> JWTPayload:
        if current_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources",
            )
        return current_user

    return _verify


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[JWTPayload, Depends(get_current_user)]
OptionalUser = Annotated[JWTPayload | None, Depends(get_current_user_optional)]


class AuthDependencies:
    """
    Class-based authentication dependencies for more complex scenarios.

    Provides additional methods for role-based access control
    and other authentication patterns.
    """

    @staticmethod
    async def get_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> JWTPayload:
        """Get current authenticated user."""
        return verify_jwt_token(credentials.credentials)

    @staticmethod
    def verify_ownership(user_id: str):
        """
        Create a dependency that verifies resource ownership.

        Args:
            user_id: The user ID that should own the resource

        Returns:
            Dependency function
        """
        async def _check(
            current_user: Annotated[JWTPayload, Depends(get_current_user)],
        ) -> JWTPayload:
            if current_user.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this resource",
                )
            return current_user

        return _check
