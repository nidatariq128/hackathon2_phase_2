# Task: T-014 - Write Backend Integration Tests
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Pytest fixtures for integration tests.

Provides test database, client, and authentication fixtures.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator

import jwt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.database import get_session
from app.config import settings


# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Test secret (must match what's used in tests)
TEST_SECRET = "test-secret-key-at-least-32-characters-long"


@pytest.fixture(scope="session")
def test_secret():
    """Provide the test secret for JWT operations."""
    return TEST_SECRET


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_factory = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session


def create_test_jwt(
    user_id: str,
    email: str = "test@example.com",
    secret: str = TEST_SECRET,
    expires_in_seconds: int = 3600,
) -> str:
    """
    Create a JWT token for testing.

    Args:
        user_id: User ID to include in token
        email: User email
        secret: JWT signing secret
        expires_in_seconds: Token validity duration

    Returns:
        Encoded JWT token string
    """
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in_seconds),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def user_token():
    """Create a JWT token for test user."""
    return create_test_jwt(user_id="test-user-123")


@pytest.fixture
def other_user_token():
    """Create a JWT token for a different user."""
    return create_test_jwt(user_id="other-user-456", email="other@example.com")


@pytest.fixture
def expired_token():
    """Create an expired JWT token."""
    return create_test_jwt(
        user_id="test-user-123",
        expires_in_seconds=-3600,  # Expired 1 hour ago
    )


@pytest.fixture
def auth_headers(user_token):
    """Create authorization headers for test user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def other_user_headers(other_user_token):
    """Create authorization headers for other user."""
    return {"Authorization": f"Bearer {other_user_token}"}


@pytest_asyncio.fixture
async def client(test_session, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test client with mocked dependencies.

    Overrides:
    - Database session with test session
    - JWT secret with test secret
    """
    # Override the get_session dependency
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    # Mock the settings for JWT verification
    monkeypatch.setattr("app.auth.jwt.settings.BETTER_AUTH_SECRET", TEST_SECRET)
    monkeypatch.setattr("app.auth.jwt.settings.JWT_ALGORITHM", "HS256")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_no_auth(test_session, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test client without authentication setup.

    Used for testing unauthenticated requests.
    """
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    monkeypatch.setattr("app.auth.jwt.settings.BETTER_AUTH_SECRET", TEST_SECRET)
    monkeypatch.setattr("app.auth.jwt.settings.JWT_ALGORITHM", "HS256")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
