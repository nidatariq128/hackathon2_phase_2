# Task: T-013 - Create Main FastAPI Application
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Health check endpoints.

Provides endpoints for monitoring application and database health.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel

from app.database import get_session


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str


class DatabaseHealthResponse(BaseModel):
    """Database health check response model."""
    status: str
    database: str
    error: str | None = None


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Basic health check endpoint to verify the API is running.",
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns:
        HealthResponse with status "healthy" if the API is running.
    """
    return HealthResponse(
        status="healthy",
        service="todo-api",
    )


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    summary="Database health check",
    description="Check database connectivity.",
    tags=["Health"],
)
async def database_health_check(
    session: AsyncSession = Depends(get_session),
) -> DatabaseHealthResponse:
    """
    Check database connectivity.

    Executes a simple query to verify the database connection is working.

    Returns:
        DatabaseHealthResponse with connection status.
    """
    try:
        await session.execute(text("SELECT 1"))
        return DatabaseHealthResponse(
            status="healthy",
            database="connected",
        )
    except Exception as e:
        return DatabaseHealthResponse(
            status="unhealthy",
            database="disconnected",
            error=str(e),
        )
