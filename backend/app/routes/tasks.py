# Task: T-007, T-008 - Implement Task Endpoints
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Task CRUD API endpoints.

Provides RESTful endpoints for managing user tasks.
All endpoints require JWT authentication and verify user ownership.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth import JWTPayload, verify_user_access
from app.database import get_session
from app.models import Task, TaskCreate, TaskResponse, TaskUpdate


router = APIRouter()


class TaskStatus(str, Enum):
    """Filter options for task status."""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


@router.get(
    "/{user_id}/tasks",
    response_model=List[TaskResponse],
    summary="List all tasks for user",
    description="Retrieve all tasks for the authenticated user with optional filtering by status.",
    responses={
        200: {
            "description": "List of tasks",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "user_id": "user_123",
                            "title": "Buy groceries",
                            "description": "Milk, eggs, bread",
                            "completed": False,
                            "created_at": "2026-01-16T10:00:00Z",
                            "updated_at": "2026-01-16T10:00:00Z",
                        }
                    ]
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied - cannot access other user's tasks"},
    },
)
async def list_tasks(
    user_id: str,
    current_user: Annotated[JWTPayload, Depends(verify_user_access)],
    session: Annotated[AsyncSession, Depends(get_session)],
    status_filter: Annotated[
        Optional[TaskStatus],
        Query(
            alias="status",
            description="Filter tasks by completion status",
            examples=["all", "pending", "completed"],
        ),
    ] = None,
) -> List[Task]:
    """
    Get all tasks for the authenticated user.

    Args:
        user_id: User ID from URL path (must match authenticated user)
        current_user: Authenticated user from JWT token
        session: Database session
        status_filter: Optional filter by task status (all, pending, completed)

    Returns:
        List of tasks belonging to the user

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Build base query filtering by user_id
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter if provided
    if status_filter == TaskStatus.PENDING:
        query = query.where(Task.completed == False)  # noqa: E712
    elif status_filter == TaskStatus.COMPLETED:
        query = query.where(Task.completed == True)  # noqa: E712
    # TaskStatus.ALL or None means no additional filtering

    # Order by created_at descending (newest first)
    query = query.order_by(Task.created_at.desc())

    # Execute query
    result = await session.execute(query)
    tasks = result.scalars().all()

    return list(tasks)


@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user.",
    responses={
        201: {
            "description": "Task created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": "user_123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-01-16T10:00:00Z",
                        "updated_at": "2026-01-16T10:00:00Z",
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied - cannot create tasks for other users"},
        422: {"description": "Validation error - invalid input data"},
    },
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: Annotated[JWTPayload, Depends(verify_user_access)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Task:
    """
    Create a new task for the authenticated user.

    Args:
        user_id: User ID from URL path (must match authenticated user)
        task_data: Task data from request body (title required, description optional)
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        The newly created task

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 422 if validation fails (title empty, too long, etc.)
    """
    # Create new task with user_id from URL (already verified to match token)
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks are always incomplete
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Add to session and commit
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get task details",
    description="Retrieve a specific task by ID for the authenticated user.",
    responses={
        200: {
            "description": "Task details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": "user_123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-01-16T10:00:00Z",
                        "updated_at": "2026-01-16T10:00:00Z",
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied - cannot access other user's tasks"},
        404: {"description": "Task not found"},
    },
)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: Annotated[JWTPayload, Depends(verify_user_access)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Task:
    """
    Get a specific task by ID.

    Args:
        user_id: User ID from URL path (must match authenticated user)
        task_id: Task ID from URL path
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        The requested task

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found or belongs to different user
    """
    # Query by task_id AND user_id to ensure user ownership
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return task


@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update an existing task's title and/or description.",
    responses={
        200: {
            "description": "Task updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": "user_123",
                        "title": "Buy groceries and fruits",
                        "description": "Milk, eggs, bread, apples",
                        "completed": False,
                        "created_at": "2026-01-16T10:00:00Z",
                        "updated_at": "2026-01-16T11:00:00Z",
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied - cannot update other user's tasks"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error - invalid input data"},
    },
)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: Annotated[JWTPayload, Depends(verify_user_access)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Task:
    """
    Update an existing task.

    Only provided fields will be updated. Omitted fields remain unchanged.

    Args:
        user_id: User ID from URL path (must match authenticated user)
        task_id: Task ID from URL path
        task_data: Fields to update (all optional)
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        The updated task

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
        HTTPException: 422 if validation fails
    """
    # Query by task_id AND user_id to ensure user ownership
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Update only provided fields (exclude_unset=True)
    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    # Always update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task by ID.",
    responses={
        204: {"description": "Task deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied - cannot delete other user's tasks"},
        404: {"description": "Task not found"},
    },
)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: Annotated[JWTPayload, Depends(verify_user_access)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """
    Delete a task by ID.

    Permanently removes the task from the database.

    Args:
        user_id: User ID from URL path (must match authenticated user)
        task_id: Task ID from URL path
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Query by task_id AND user_id to ensure user ownership
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Delete the task
    await session.delete(task)
    await session.commit()

    return None


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion",
    description="Toggle the completion status of a task (complete ↔ incomplete).",
    responses={
        200: {
            "description": "Task completion status toggled",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": "user_123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": True,
                        "created_at": "2026-01-16T10:00:00Z",
                        "updated_at": "2026-01-16T11:00:00Z",
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied - cannot modify other user's tasks"},
        404: {"description": "Task not found"},
    },
)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: Annotated[JWTPayload, Depends(verify_user_access)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Task:
    """
    Toggle the completion status of a task.

    If the task is incomplete, it will be marked as complete.
    If the task is complete, it will be marked as incomplete.

    Args:
        user_id: User ID from URL path (must match authenticated user)
        task_id: Task ID from URL path
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        The task with toggled completion status

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Query by task_id AND user_id to ensure user ownership
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Toggle the completed status
    task.completed = not task.completed

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    # Commit changes
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
