# Todo API - Backend

Phase II - Todo Full-Stack Web Application Backend

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT (Better Auth compatible)
- **Python**: 3.11+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package init
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task model and schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py         # Task CRUD endpoints
│   │   └── health.py        # Health check endpoints
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
│   └── test_tasks.py        # Task endpoint tests
├── pyproject.toml           # Dependencies and config
├── .env.example             # Environment template
└── README.md                # This file
```

## Setup

### 1. Install UV (if not installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
cd backend
uv sync
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values:
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - BETTER_AUTH_SECRET: Shared secret with frontend
```

### 4. Run Development Server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task by ID |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

## Authentication

All `/api/*` endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

The JWT must be signed with the same `BETTER_AUTH_SECRET` as the frontend.

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_tasks.py
```

## Linting

```bash
# Check code style
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (shared with frontend) |
| `JWT_ALGORITHM` | No | JWT algorithm (default: HS256) |
| `CORS_ORIGINS` | No | Allowed CORS origins (default: ["http://localhost:3000"]) |
| `DEBUG` | No | Enable debug mode (default: false) |

---

**Task Reference**: T-001
**Spec Reference**: `specs/task-crud/spec.md`
