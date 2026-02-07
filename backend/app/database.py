# Task: T-003 - Set Up Database Connection
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Database connection and session management.

Provides async database connection to Neon PostgreSQL using SQLModel and asyncpg.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.config import settings


# Create async engine with asyncpg driver
# Using NullPool for serverless environments (Neon) to avoid connection issues
# For non-serverless, you can use default pooling with pool_size and max_overflow
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,  # Log SQL statements in debug mode
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    # Use NullPool for serverless PostgreSQL (Neon)
    # This creates a new connection for each request
    poolclass=NullPool,
    # Enable SSL for Neon connections (asyncpg uses ssl=True instead of sslmode)
    connect_args={
        "ssl": "require",  # asyncpg SSL mode
        "server_settings": {
            "jit": "off"  # Disable JIT for better compatibility
        }
    },
)

# Alternative configuration for non-serverless environments:
# engine = create_async_engine(
#     settings.async_database_url,
#     echo=settings.DEBUG,
#     future=True,
#     pool_pre_ping=True,
#     pool_size=5,          # Number of connections to keep open
#     max_overflow=10,      # Additional connections when pool is exhausted
#     pool_timeout=30,      # Seconds to wait for connection
#     pool_recycle=1800,    # Recycle connections after 30 minutes
# )

# Async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (needed for async)
    autocommit=False,
    autoflush=False,
)


async def create_db_and_tables() -> None:
    """
    Create all database tables defined in SQLModel models.

    This function should be called on application startup to ensure
    all tables exist in the database.

    Note: In production, consider using Alembic migrations instead
    of auto-creating tables.
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered with SQLModel
        # This import is done here to avoid circular imports
        from app.models import task  # noqa: F401

        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db_and_tables() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data. Only use for testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Yields an async database session and handles commit/rollback
    based on whether an exception occurred.

    Usage:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session for the request

    Raises:
        Any exception from the request handler (after rollback)
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session_no_commit() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session without auto-commit.

    Use this when you need manual control over commits,
    such as in complex transactions or batch operations.

    Yields:
        AsyncSession: Database session for the request
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with async_session_factory() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
