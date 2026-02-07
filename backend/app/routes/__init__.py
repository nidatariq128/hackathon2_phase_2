# Task: T-001 - Initialize Backend Project Structure
# Spec: specs/task-crud/spec.md
"""
API routes package.

Contains FastAPI routers for API endpoints.
"""

from app.routes.tasks import router as tasks_router
from app.routes.health import router as health_router

__all__ = [
    "tasks_router",
    "health_router",
]
