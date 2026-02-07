# Task: T-013 - Create Main FastAPI Application
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Main FastAPI application entry point.

Configures the FastAPI application with:
- CORS middleware
- API routers
- Database lifecycle management
- Exception handlers
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables
from app.routes import tasks_router
from app.routes.health import router as health_router
from app.utils.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifecycle manager for FastAPI application.

    Handles startup and shutdown events:
    - Startup: Creates database tables if they don't exist
    - Shutdown: Cleanup (if needed)
    """
    # Startup
    print("Starting up Todo API...")
    await create_db_and_tables()
    print("Database tables created/verified.")

    yield

    # Shutdown
    print("Shutting down Todo API...")


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="""
## Phase II - Todo Full-Stack Web Application API

A RESTful API for managing user tasks with JWT authentication.

### Features
- **User Authentication**: JWT-based authentication via Better Auth
- **Task Management**: Full CRUD operations for tasks
- **User Isolation**: Each user can only access their own tasks

### Authentication
All `/api/*` endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Spec Reference
- Spec: `specs/task-crud/spec.md`
- Plan: `specs/task-crud/plan.md`
- Constitution: `.specify/memory/constitution.md`
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(
    health_router,
    tags=["Health"],
)

app.include_router(
    tasks_router,
    prefix="/api",
    tags=["Tasks"],
)


@app.get(
    "/",
    summary="API Root",
    description="Returns basic API information and links to documentation.",
    tags=["Root"],
)
async def root() -> dict:
    """
    API root endpoint.

    Returns basic API information and links to documentation.
    """
    return {
        "name": "Todo API",
        "version": "1.0.0",
        "description": "Phase II - Todo Full-Stack Web Application API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
