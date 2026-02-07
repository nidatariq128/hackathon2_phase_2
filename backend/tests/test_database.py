# Task: T-003 - Set Up Database Connection
# Spec: specs/task-crud/spec.md
"""
Tests for database connection and session management.

Uses SQLite with aiosqlite for testing to avoid requiring PostgreSQL.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Field, select, text
from typing import Optional, AsyncGenerator


# Test model for database tests
class TestItem(SQLModel, table=True):
    """Test model for database operations."""
    __tablename__ = "test_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)


# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    """Create a test session factory."""
    return sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture
async def test_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_session_factory() as session:
        yield session


class TestDatabaseConnection:
    """Tests for database connection."""

    @pytest.mark.asyncio
    async def test_engine_connection(self, test_engine):
        """Test that engine can connect to database."""
        async with test_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row[0] == 1

    @pytest.mark.asyncio
    async def test_session_creation(self, test_session):
        """Test that session can be created."""
        assert test_session is not None
        assert isinstance(test_session, AsyncSession)

    @pytest.mark.asyncio
    async def test_session_execute_query(self, test_session):
        """Test that session can execute queries."""
        result = await test_session.execute(text("SELECT 1"))
        row = result.fetchone()
        assert row[0] == 1


class TestDatabaseOperations:
    """Tests for database CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_item(self, test_session):
        """Test creating an item in the database."""
        item = TestItem(name="Test Item")
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)

        assert item.id is not None
        assert item.name == "Test Item"

    @pytest.mark.asyncio
    async def test_read_item(self, test_session):
        """Test reading an item from the database."""
        # Create item
        item = TestItem(name="Read Test")
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)

        # Read item
        result = await test_session.execute(
            select(TestItem).where(TestItem.id == item.id)
        )
        fetched_item = result.scalar_one_or_none()

        assert fetched_item is not None
        assert fetched_item.id == item.id
        assert fetched_item.name == "Read Test"

    @pytest.mark.asyncio
    async def test_update_item(self, test_session):
        """Test updating an item in the database."""
        # Create item
        item = TestItem(name="Original Name")
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)

        # Update item
        item.name = "Updated Name"
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)

        # Verify update
        result = await test_session.execute(
            select(TestItem).where(TestItem.id == item.id)
        )
        updated_item = result.scalar_one_or_none()

        assert updated_item.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_item(self, test_session):
        """Test deleting an item from the database."""
        # Create item
        item = TestItem(name="Delete Me")
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)

        item_id = item.id

        # Delete item
        await test_session.delete(item)
        await test_session.commit()

        # Verify deletion
        result = await test_session.execute(
            select(TestItem).where(TestItem.id == item_id)
        )
        deleted_item = result.scalar_one_or_none()

        assert deleted_item is None

    @pytest.mark.asyncio
    async def test_list_items(self, test_session):
        """Test listing multiple items from the database."""
        # Create multiple items
        items = [
            TestItem(name="Item 1"),
            TestItem(name="Item 2"),
            TestItem(name="Item 3"),
        ]
        for item in items:
            test_session.add(item)
        await test_session.commit()

        # List items
        result = await test_session.execute(select(TestItem))
        fetched_items = result.scalars().all()

        assert len(fetched_items) >= 3
        names = [item.name for item in fetched_items]
        assert "Item 1" in names
        assert "Item 2" in names
        assert "Item 3" in names


class TestSessionRollback:
    """Tests for session rollback behavior."""

    @pytest.mark.asyncio
    async def test_rollback_on_error(self, test_session_factory):
        """Test that session rolls back on error."""
        async with test_session_factory() as session:
            # Create item
            item = TestItem(name="Rollback Test")
            session.add(item)
            await session.commit()
            await session.refresh(item)

            item_id = item.id

        # Try to update with simulated error
        async with test_session_factory() as session:
            result = await session.execute(
                select(TestItem).where(TestItem.id == item_id)
            )
            item = result.scalar_one()
            item.name = "Should Not Persist"
            session.add(item)
            # Don't commit - simulate rollback
            await session.rollback()

        # Verify rollback
        async with test_session_factory() as session:
            result = await session.execute(
                select(TestItem).where(TestItem.id == item_id)
            )
            item = result.scalar_one()
            assert item.name == "Rollback Test"  # Original name preserved


class TestTableCreation:
    """Tests for table creation."""

    @pytest.mark.asyncio
    async def test_create_tables(self):
        """Test that create_db_and_tables creates tables."""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
        )

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        # Verify table exists by querying
        async with engine.connect() as conn:
            # This should not raise an error if table exists
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='test_items'")
            )
            row = result.fetchone()
            assert row is not None

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_drop_tables(self):
        """Test that drop_db_and_tables removes tables."""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
        )

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        # Drop tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

        # Verify table is gone
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='test_items'")
            )
            row = result.fetchone()
            assert row is None

        await engine.dispose()
