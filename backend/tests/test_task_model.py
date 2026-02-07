# Task: T-004 - Create Task SQLModel
# Spec: specs/task-crud/spec.md
"""
Tests for Task model and schemas.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse


class TestTaskModel:
    """Tests for Task database model."""

    def test_task_creation_with_required_fields(self):
        """Test creating a task with required fields."""
        task = Task(
            user_id="user_123",
            title="Test Task",
        )

        assert task.user_id == "user_123"
        assert task.title == "Test Task"
        assert task.description is None
        assert task.completed is False
        assert task.id is None  # Not set until saved to DB

    def test_task_creation_with_all_fields(self):
        """Test creating a task with all fields."""
        task = Task(
            user_id="user_123",
            title="Test Task",
            description="Test description",
            completed=True,
        )

        assert task.user_id == "user_123"
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.completed is True

    def test_task_default_completed_is_false(self):
        """Test that completed defaults to False."""
        task = Task(
            user_id="user_123",
            title="Test Task",
        )

        assert task.completed is False

    def test_task_timestamps_auto_set(self):
        """Test that created_at and updated_at are auto-set."""
        before = datetime.utcnow()
        task = Task(
            user_id="user_123",
            title="Test Task",
        )
        after = datetime.utcnow()

        assert task.created_at is not None
        assert task.updated_at is not None
        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after

    def test_task_table_name(self):
        """Test that table name is correctly set."""
        assert Task.__tablename__ == "tasks"


class TestTaskCreate:
    """Tests for TaskCreate schema."""

    def test_valid_task_create(self):
        """Test creating a valid TaskCreate."""
        task_data = TaskCreate(
            title="Test Task",
            description="Test description",
        )

        assert task_data.title == "Test Task"
        assert task_data.description == "Test description"

    def test_task_create_title_only(self):
        """Test creating TaskCreate with title only."""
        task_data = TaskCreate(title="Test Task")

        assert task_data.title == "Test Task"
        assert task_data.description is None

    def test_task_create_missing_title_raises_error(self):
        """Test that missing title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("title",) for e in errors)

    def test_task_create_empty_title_raises_error(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")

        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_task_create_whitespace_title_raises_error(self):
        """Test that whitespace-only title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="   ")

        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_task_create_title_too_long_raises_error(self):
        """Test that title over 200 characters raises error."""
        long_title = "a" * 201

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)

        errors = exc_info.value.errors()
        assert any("200" in str(e) or "max_length" in str(e) for e in errors)

    def test_task_create_title_max_length_valid(self):
        """Test that title at exactly 200 characters is valid."""
        max_title = "a" * 200
        task_data = TaskCreate(title=max_title)

        assert len(task_data.title) == 200

    def test_task_create_description_too_long_raises_error(self):
        """Test that description over 1000 characters raises error."""
        long_desc = "a" * 1001

        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test", description=long_desc)

        errors = exc_info.value.errors()
        assert any("1000" in str(e) or "max_length" in str(e) for e in errors)

    def test_task_create_description_max_length_valid(self):
        """Test that description at exactly 1000 characters is valid."""
        max_desc = "a" * 1000
        task_data = TaskCreate(title="Test", description=max_desc)

        assert len(task_data.description) == 1000

    def test_task_create_title_trimmed(self):
        """Test that title is trimmed of whitespace."""
        task_data = TaskCreate(title="  Test Task  ")

        assert task_data.title == "Test Task"

    def test_task_create_description_trimmed(self):
        """Test that description is trimmed of whitespace."""
        task_data = TaskCreate(title="Test", description="  Test description  ")

        assert task_data.description == "Test description"

    def test_task_create_empty_description_becomes_none(self):
        """Test that empty description becomes None."""
        task_data = TaskCreate(title="Test", description="   ")

        assert task_data.description is None


class TestTaskUpdate:
    """Tests for TaskUpdate schema."""

    def test_task_update_all_fields(self):
        """Test updating all fields."""
        task_data = TaskUpdate(
            title="Updated Title",
            description="Updated description",
        )

        assert task_data.title == "Updated Title"
        assert task_data.description == "Updated description"

    def test_task_update_title_only(self):
        """Test updating title only."""
        task_data = TaskUpdate(title="Updated Title")

        assert task_data.title == "Updated Title"
        assert task_data.description is None

    def test_task_update_description_only(self):
        """Test updating description only."""
        task_data = TaskUpdate(description="Updated description")

        assert task_data.title is None
        assert task_data.description == "Updated description"

    def test_task_update_empty_is_valid(self):
        """Test that empty update is valid (no fields to update)."""
        task_data = TaskUpdate()

        assert task_data.title is None
        assert task_data.description is None

    def test_task_update_title_too_long_raises_error(self):
        """Test that title over 200 characters raises error."""
        long_title = "a" * 201

        with pytest.raises(ValidationError):
            TaskUpdate(title=long_title)

    def test_task_update_description_too_long_raises_error(self):
        """Test that description over 1000 characters raises error."""
        long_desc = "a" * 1001

        with pytest.raises(ValidationError):
            TaskUpdate(description=long_desc)

    def test_task_update_whitespace_title_raises_error(self):
        """Test that whitespace-only title raises validation error."""
        with pytest.raises(ValidationError):
            TaskUpdate(title="   ")

    def test_task_update_title_trimmed(self):
        """Test that title is trimmed of whitespace."""
        task_data = TaskUpdate(title="  Updated Title  ")

        assert task_data.title == "Updated Title"

    def test_task_update_empty_description_becomes_none(self):
        """Test that empty description becomes None."""
        task_data = TaskUpdate(description="   ")

        assert task_data.description is None

    def test_task_update_model_dump_excludes_unset(self):
        """Test that model_dump excludes unset fields."""
        task_data = TaskUpdate(title="Updated Title")
        data = task_data.model_dump(exclude_unset=True)

        assert "title" in data
        assert "description" not in data


class TestTaskResponse:
    """Tests for TaskResponse schema."""

    def test_task_response_from_task_model(self):
        """Test creating TaskResponse from Task model."""
        task = Task(
            id=1,
            user_id="user_123",
            title="Test Task",
            description="Test description",
            completed=False,
            created_at=datetime(2026, 1, 16, 10, 0, 0),
            updated_at=datetime(2026, 1, 16, 10, 0, 0),
        )

        response = TaskResponse.model_validate(task)

        assert response.id == 1
        assert response.user_id == "user_123"
        assert response.title == "Test Task"
        assert response.description == "Test description"
        assert response.completed is False
        assert response.created_at == datetime(2026, 1, 16, 10, 0, 0)
        assert response.updated_at == datetime(2026, 1, 16, 10, 0, 0)

    def test_task_response_serialization(self):
        """Test TaskResponse JSON serialization."""
        task = Task(
            id=1,
            user_id="user_123",
            title="Test Task",
            description="Test description",
            completed=True,
            created_at=datetime(2026, 1, 16, 10, 0, 0),
            updated_at=datetime(2026, 1, 16, 10, 0, 0),
        )

        response = TaskResponse.model_validate(task)
        json_data = response.model_dump()

        assert json_data["id"] == 1
        assert json_data["user_id"] == "user_123"
        assert json_data["title"] == "Test Task"
        assert json_data["description"] == "Test description"
        assert json_data["completed"] is True

    def test_task_response_from_dict(self):
        """Test creating TaskResponse from dictionary."""
        data = {
            "id": 1,
            "user_id": "user_123",
            "title": "Test Task",
            "description": None,
            "completed": False,
            "created_at": datetime(2026, 1, 16, 10, 0, 0),
            "updated_at": datetime(2026, 1, 16, 10, 0, 0),
        }

        response = TaskResponse.model_validate(data)

        assert response.id == 1
        assert response.user_id == "user_123"
        assert response.title == "Test Task"
        assert response.description is None
        assert response.completed is False


class TestTaskValidationEdgeCases:
    """Tests for edge cases in task validation."""

    def test_task_create_unicode_title(self):
        """Test that unicode characters are allowed in title."""
        task_data = TaskCreate(title="任务标题 📝")

        assert task_data.title == "任务标题 📝"

    def test_task_create_unicode_description(self):
        """Test that unicode characters are allowed in description."""
        task_data = TaskCreate(
            title="Test",
            description="Description with émojis 🎉 and ünïcödé",
        )

        assert "émojis" in task_data.description

    def test_task_create_newlines_in_description(self):
        """Test that newlines are allowed in description."""
        task_data = TaskCreate(
            title="Test",
            description="Line 1\nLine 2\nLine 3",
        )

        assert "\n" in task_data.description

    def test_task_create_special_characters_in_title(self):
        """Test that special characters are allowed in title."""
        task_data = TaskCreate(title="Task: Buy groceries! (urgent)")

        assert task_data.title == "Task: Buy groceries! (urgent)"

    def test_task_create_minimum_title(self):
        """Test that single character title is valid."""
        task_data = TaskCreate(title="A")

        assert task_data.title == "A"
