# Task: T-004 - Create Task SQLModel
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Task model and schemas for the Todo API.

Defines the Task database model and Pydantic schemas for
request validation and response serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel, Index


class TaskBase(SQLModel):
    """
    Base Task model with shared fields.

    Used as a base class for other Task schemas to avoid
    duplicating field definitions.
    """

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional, max 1000 characters)",
    )


class Task(TaskBase, table=True):
    """
    Task database model.

    Represents a todo task in the database with user ownership,
    completion status, and timestamps.

    Attributes:
        id: Auto-generated primary key
        user_id: Foreign key to user (from Better Auth)
        title: Task title (1-200 characters, required)
        description: Task description (max 1000 characters, optional)
        completed: Whether the task is completed (default: False)
        created_at: When the task was created (auto-set)
        updated_at: When the task was last updated (auto-set)
    """

    __tablename__ = "tasks"

    # Table indexes for query optimization
    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_completed", "completed"),
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_tasks_user_completed", "user_id", "completed"),
    )

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique task identifier",
    )
    user_id: str = Field(
        index=True,
        description="User ID from Better Auth",
    )
    completed: bool = Field(
        default=False,
        index=True,
        description="Whether the task is completed",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was last updated",
    )


class TaskCreate(SQLModel):
    """
    Schema for creating a new task.

    Used to validate POST request body when creating a task.
    Only includes fields that can be set by the user.

    Attributes:
        title: Task title (required, 1-200 characters)
        description: Task description (optional, max 1000 characters)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, butter",
            }
        }
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional, max 1000 characters)",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean title."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v is not None:
            v = v.strip()
            if not v:
                return None  # Convert empty string to None
        return v


class TaskUpdate(SQLModel):
    """
    Schema for updating an existing task.

    Used to validate PUT request body when updating a task.
    All fields are optional - only provided fields will be updated.

    Attributes:
        title: New task title (optional, 1-200 characters if provided)
        description: New task description (optional, max 1000 characters)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries and fruits",
                "description": "Milk, eggs, bread, butter, apples, bananas",
            }
        }
    )

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New task title (1-200 characters)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="New task description (max 1000 characters)",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean title if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None  # Convert empty string to None
        return v


class TaskResponse(TaskBase):
    """
    Schema for task response.

    Used to serialize Task objects in API responses.
    Includes all task fields for the client.

    Attributes:
        id: Task ID
        user_id: User ID who owns the task
        title: Task title
        description: Task description
        completed: Completion status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": "user_abc123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, butter",
                "completed": False,
                "created_at": "2026-01-16T10:00:00Z",
                "updated_at": "2026-01-16T10:00:00Z",
            }
        }
    )

    id: int = Field(description="Unique task identifier")
    user_id: str = Field(description="User ID who owns the task")
    completed: bool = Field(description="Whether the task is completed")
    created_at: datetime = Field(description="When the task was created")
    updated_at: datetime = Field(description="When the task was last updated")


class TaskListResponse(SQLModel):
    """
    Schema for listing multiple tasks.

    Used when returning a list of tasks with optional metadata.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "user_id": "user_abc123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-01-16T10:00:00Z",
                        "updated_at": "2026-01-16T10:00:00Z",
                    }
                ],
                "total": 1,
            }
        }
    )

    tasks: list[TaskResponse] = Field(description="List of tasks")
    total: int = Field(description="Total number of tasks")
