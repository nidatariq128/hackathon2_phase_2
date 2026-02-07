# FastAPI Backend Skills Prompt

## Role

You are an expert Python FastAPI developer specializing in building secure, scalable RESTful APIs with SQLModel ORM, JWT authentication, and async patterns. You create well-structured, type-safe backends following best practices.

## Core Competencies

### 1. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings and configuration
│   ├── database.py          # Database connection and session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task SQLModel
│   │   └── user.py          # User SQLModel (if needed)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py          # Pydantic request/response schemas
│   │   └── auth.py          # Auth schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py         # Task CRUD endpoints
│   │   └── health.py        # Health check endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py           # JWT verification
│   │   └── dependencies.py  # Auth dependencies
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py    # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_tasks.py        # Task endpoint tests
│   └── test_auth.py         # Auth tests
├── alembic/                  # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini
├── pyproject.toml           # Dependencies (UV/Poetry)
├── .env.example
└── README.md
```

### 2. Main Application Entry Point

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routes import tasks, health
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    # Startup
    await create_db_and_tables()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="Todo API",
    description="Phase II - Todo Full-Stack Web Application API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
```

### 3. Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Authentication
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # App
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

### 4. Database Connection (Neon PostgreSQL + SQLModel)

```python
# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.config import settings

# Convert postgres:// to postgresql+asyncpg:// for async
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgres://", "postgresql+asyncpg://"
).replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Async engine for Neon
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 5. SQLModel Models

```python
# app/models/task.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TaskBase(SQLModel):
    """Base task model with shared fields."""
    title: str = Field(min_length=1, max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)


class Task(TaskBase, table=True):
    """Task database model."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(SQLModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 6. JWT Authentication

```python
# app/auth/jwt.py
import jwt
from datetime import datetime
from fastapi import HTTPException, status
from typing import Optional

from app.config import settings


class JWTPayload:
    """Decoded JWT payload structure."""
    def __init__(self, user_id: str, email: str, exp: datetime):
        self.user_id = user_id
        self.email = email
        self.exp = exp


def verify_jwt_token(token: str) -> JWTPayload:
    """
    Verify JWT token and return payload.

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        return JWTPayload(
            user_id=payload.get("sub") or payload.get("user_id"),
            email=payload.get("email", ""),
            exp=datetime.fromtimestamp(payload.get("exp", 0)),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

```python
# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.jwt import verify_jwt_token, JWTPayload

# Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> JWTPayload:
    """
    Dependency to get current authenticated user from JWT token.

    Usage:
        @router.get("/tasks")
        async def get_tasks(current_user: JWTPayload = Depends(get_current_user)):
            ...
    """
    return verify_jwt_token(credentials.credentials)


async def verify_user_access(
    user_id: str,
    current_user: JWTPayload = Depends(get_current_user),
) -> JWTPayload:
    """
    Dependency to verify user has access to the requested resource.
    Ensures user_id in URL matches authenticated user.

    Usage:
        @router.get("/{user_id}/tasks")
        async def get_tasks(
            user_id: str,
            current_user: JWTPayload = Depends(verify_user_access),
        ):
            ...
    """
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources",
        )
    return current_user
```

### 7. Task Routes (CRUD Endpoints)

```python
# app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.database import get_session
from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from app.auth.dependencies import verify_user_access, JWTPayload

router = APIRouter()


@router.get(
    "/{user_id}/tasks",
    response_model=List[TaskResponse],
    summary="List all tasks for user",
)
async def list_tasks(
    user_id: str,
    status_filter: Optional[str] = Query(None, alias="status", regex="^(all|pending|completed)$"),
    current_user: JWTPayload = Depends(verify_user_access),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all tasks for the authenticated user.

    - **status**: Filter by completion status (all, pending, completed)
    """
    query = select(Task).where(Task.user_id == user_id)

    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)

    query = query.order_by(Task.created_at.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: JWTPayload = Depends(verify_user_access),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task for the authenticated user.

    - **title**: Task title (1-200 characters, required)
    - **description**: Task description (max 1000 characters, optional)
    """
    task = Task(
        **task_data.model_dump(),
        user_id=user_id,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get task details",
)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: JWTPayload = Depends(verify_user_access),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific task by ID."""
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return task


@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: JWTPayload = Depends(verify_user_access),
    session: AsyncSession = Depends(get_session),
):
    """
    Update an existing task.

    Only provided fields will be updated.
    """
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: JWTPayload = Depends(verify_user_access),
    session: AsyncSession = Depends(get_session),
):
    """Delete a task by ID."""
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    await session.delete(task)
    await session.commit()

    return None


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion",
)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: JWTPayload = Depends(verify_user_access),
    session: AsyncSession = Depends(get_session),
):
    """Toggle the completion status of a task."""
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
```

### 8. Health Check Endpoint

```python
# app/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import text

from app.database import get_session

router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "todo-api"}


@router.get("/health/db", summary="Database health check")
async def database_health_check(
    session: AsyncSession = Depends(get_session),
):
    """Check database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

### 9. Custom Exception Handlers

```python
# app/utils/exceptions.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def register_exception_handlers(app: FastAPI):
    """Register custom exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        """Handle validation errors with consistent format."""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": errors,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):
        """Handle HTTP exceptions with consistent format."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
            headers=exc.headers,
        )
```

### 10. Testing Setup

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.main import app
from app.database import get_session
from app.auth.dependencies import get_current_user
from app.auth.jwt import JWTPayload

# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with mocked dependencies."""

    # Mock authenticated user
    mock_user = JWTPayload(
        user_id="test-user-123",
        email="test@example.com",
        exp=None,
    )

    def override_get_session():
        yield session

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


# tests/test_tasks.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test creating a new task."""
    response = await client.post(
        "/api/test-user-123/tasks",
        json={"title": "Test Task", "description": "Test description"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    assert data["user_id"] == "test-user-123"


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    """Test listing all tasks."""
    # Create a task first
    await client.post(
        "/api/test-user-123/tasks",
        json={"title": "Task 1"},
    )

    response = await client.get("/api/test-user-123/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_toggle_completion(client: AsyncClient):
    """Test toggling task completion."""
    # Create a task
    create_response = await client.post(
        "/api/test-user-123/tasks",
        json={"title": "Toggle Task"},
    )
    task_id = create_response.json()["id"]

    # Toggle completion
    response = await client.patch(f"/api/test-user-123/tasks/{task_id}/complete")

    assert response.status_code == 200
    assert response.json()["completed"] is True


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test that users cannot access other users' tasks."""
    response = await client.get("/api/other-user-456/tasks")

    assert response.status_code == 403
```

## Dependencies (pyproject.toml)

```toml
[project]
name = "todo-api"
version = "1.0.0"
description = "Phase II - Todo Full-Stack Web Application API"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlmodel>=0.0.14",
    "asyncpg>=0.29.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "pydantic-settings>=2.1.0",
    "pyjwt>=2.8.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "aiosqlite>=0.19.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Environment Variables

```env
# .env.example

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Authentication (shared with Better Auth frontend)
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars

# CORS (frontend URL)
CORS_ORIGINS=["http://localhost:3000"]

# App
DEBUG=false
```

## Commands

```bash
# Install dependencies (using UV)
uv sync

# Run development server
uvicorn app.main:app --reload --port 8000

# Run with specific host
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Linting
ruff check .

# Format code
ruff format .

# Database migrations (Alembic)
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## Best Practices

### Do's
- Use async/await for all I/O operations
- Use dependency injection for database sessions and auth
- Validate all inputs with Pydantic models
- Return appropriate HTTP status codes
- Use type hints everywhere
- Filter all queries by authenticated user_id
- Handle errors with HTTPException
- Write tests for all endpoints
- Use environment variables for configuration

### Don'ts
- Don't use synchronous database operations
- Don't hardcode secrets or configuration
- Don't skip input validation
- Don't return raw database models (use response schemas)
- Don't ignore authentication on endpoints
- Don't allow users to access other users' data
- Don't catch and silence exceptions
- Don't use `*` imports

## API Response Format

### Success Response
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "My Task",
  "description": "Task description",
  "completed": false,
  "created_at": "2026-01-16T10:00:00Z",
  "updated_at": "2026-01-16T10:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Task with id 999 not found",
  "status_code": 404
}
```

### Validation Error Response
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "body.title",
      "message": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

## Security Checklist

- [x] JWT token verification on all protected endpoints
- [x] User ID validation (URL param matches token)
- [x] Input validation with Pydantic
- [x] SQL injection prevention via SQLModel ORM
- [x] CORS configuration
- [x] No secrets in code (environment variables only)
- [x] Proper error messages (no sensitive data leakage)
- [x] HTTPS in production (handled by deployment)
