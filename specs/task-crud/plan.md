# Task CRUD Operations - Implementation Plan

## Overview

**Feature**: Task CRUD Operations
**Phase**: II - Full-Stack Web Application
**Spec Reference**: `specs/task-crud/spec.md`
**Status**: Planning

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js 16+)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  TaskList   │  │  TaskForm   │  │ TaskDetail  │  │  TaskCard   │        │
│  │    Page     │  │    Page     │  │    Page     │  │  Component  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┴────────────────┴────────────────┘               │
│                                   │                                         │
│                          ┌────────▼────────┐                               │
│                          │   API Client    │                               │
│                          │  (lib/api.ts)   │                               │
│                          │  + JWT Token    │                               │
│                          └────────┬────────┘                               │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │ HTTP + Bearer Token
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND (FastAPI)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         JWT Middleware                               │   │
│  │                    (Verify Token + Extract User)                     │   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐   │
│  │                          Task Router                                 │   │
│  │   GET /{user_id}/tasks          POST /{user_id}/tasks               │   │
│  │   GET /{user_id}/tasks/{id}     PUT /{user_id}/tasks/{id}           │   │
│  │   DELETE /{user_id}/tasks/{id}  PATCH /{user_id}/tasks/{id}/complete│   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼───────────────────────────────────┐   │
│  │                         SQLModel ORM                                 │   │
│  │                      (Task Model + Queries)                          │   │
│  └─────────────────────────────────┬───────────────────────────────────┘   │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Neon PostgreSQL       │
                        │   (tasks table)         │
                        └─────────────────────────┘
```

## Implementation Phases

### Phase 1: Backend Foundation
1. Database setup and Task model
2. JWT authentication middleware
3. Task CRUD API endpoints
4. API testing

### Phase 2: Frontend Foundation
1. Project setup and API client
2. TypeScript types
3. Task components
4. Task pages/routes

### Phase 3: Integration & Testing
1. Frontend-backend integration
2. Error handling
3. E2E testing
4. Polish and optimization

## Detailed Component Design

### 1. Database Layer

#### 1.1 Task Model (SQLModel)
```python
# Location: backend/app/models/task.py

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### 1.2 Database Indexes
- `idx_tasks_user_id` on `user_id` - for user filtering
- `idx_tasks_completed` on `completed` - for status filtering
- `idx_tasks_created_at` on `created_at` - for sorting

### 2. Authentication Layer

#### 2.1 JWT Verification Flow
```
Request → Extract Bearer Token → Decode JWT → Validate Signature
        → Check Expiration → Extract user_id → Compare with URL param
        → Allow/Deny
```

#### 2.2 Auth Dependencies
```python
# Location: backend/app/auth/dependencies.py

async def get_current_user(credentials) -> JWTPayload:
    """Extract and verify JWT from Authorization header."""

async def verify_user_access(user_id, current_user) -> JWTPayload:
    """Ensure URL user_id matches token user_id."""
```

### 3. API Layer

#### 3.1 Endpoint Design

| Endpoint | Method | Handler | Description |
|----------|--------|---------|-------------|
| `/{user_id}/tasks` | GET | `list_tasks()` | List with optional status filter |
| `/{user_id}/tasks` | POST | `create_task()` | Create new task |
| `/{user_id}/tasks/{id}` | GET | `get_task()` | Get single task |
| `/{user_id}/tasks/{id}` | PUT | `update_task()` | Update task fields |
| `/{user_id}/tasks/{id}` | DELETE | `delete_task()` | Delete task |
| `/{user_id}/tasks/{id}/complete` | PATCH | `toggle_complete()` | Toggle status |

#### 3.2 Request/Response Schemas
```python
# Location: backend/app/models/task.py

class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskResponse(SQLModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

### 4. Frontend Layer

#### 4.1 API Client Design
```typescript
// Location: frontend/lib/api.ts

class TaskAPI {
  async list(userId: string, status?: string): Promise<Task[]>
  async create(userId: string, data: CreateTaskInput): Promise<Task>
  async get(userId: string, taskId: number): Promise<Task>
  async update(userId: string, taskId: number, data: UpdateTaskInput): Promise<Task>
  async delete(userId: string, taskId: number): Promise<void>
  async toggleComplete(userId: string, taskId: number): Promise<Task>
}
```

#### 4.2 Component Hierarchy
```
app/
├── (dashboard)/
│   └── tasks/
│       ├── page.tsx           → TaskListPage (Server Component)
│       │   └── TaskList       → Client Component (interactivity)
│       │       └── TaskCard   → Client Component (toggle, delete)
│       ├── new/
│       │   └── page.tsx       → CreateTaskPage
│       │       └── TaskForm   → Client Component (form handling)
│       └── [id]/
│           ├── page.tsx       → TaskDetailPage (Server Component)
│           │   └── TaskDetail → Client Component (actions)
│           └── edit/
│               └── page.tsx   → EditTaskPage
│                   └── TaskForm → Client Component
```

#### 4.3 Component Specifications

**TaskList Component**
- Props: `initialTasks: Task[]`
- State: `tasks`, `filter`, `isLoading`
- Features: Filter tabs, empty state, loading spinner

**TaskCard Component**
- Props: `task: Task`, `onToggle`, `onDelete`
- State: `isToggling`, `isDeleting`
- Features: Checkbox, delete button, click navigation

**TaskForm Component**
- Props: `task?: Task`, `onSubmit`, `isLoading`
- State: Form fields, validation errors
- Features: Title input, description textarea, submit/cancel

**TaskDetail Component**
- Props: `task: Task`
- State: `isDeleting`
- Features: Full info display, edit/delete buttons, toggle

### 5. Data Flow

#### 5.1 Create Task Flow
```
User fills form → Submit → TaskForm.onSubmit()
    → api.create(userId, data)
    → POST /api/{user_id}/tasks (with JWT)
    → Backend validates → Insert to DB
    → Return TaskResponse
    → revalidatePath('/dashboard/tasks')
    → redirect('/dashboard/tasks')
```

#### 5.2 Toggle Complete Flow
```
User clicks checkbox → TaskCard.onToggle()
    → Optimistic UI update (toggle locally)
    → api.toggleComplete(userId, taskId)
    → PATCH /api/{user_id}/tasks/{id}/complete
    → Backend toggles → Update DB
    → Return updated Task
    → Confirm UI state (or rollback on error)
```

#### 5.3 Delete Task Flow
```
User clicks delete → Show confirmation dialog
    → User confirms → TaskCard.onDelete()
    → api.delete(userId, taskId)
    → DELETE /api/{user_id}/tasks/{id}
    → Backend deletes → 204 No Content
    → Remove from local state
    → Show success toast
```

## File Structure

### Backend
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, routers, middleware
│   ├── config.py               # Settings from env vars
│   ├── database.py             # Async engine, session factory
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py             # Task model + schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py            # Task CRUD endpoints
│   │   └── health.py           # Health check
│   └── auth/
│       ├── __init__.py
│       ├── jwt.py              # JWT decode/verify
│       └── dependencies.py     # FastAPI dependencies
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures
│   └── test_tasks.py           # Task endpoint tests
├── pyproject.toml
├── .env.example
└── README.md
```

### Frontend
```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home (redirect to dashboard)
│   └── (dashboard)/
│       ├── layout.tsx          # Dashboard layout (auth check)
│       └── tasks/
│           ├── page.tsx        # Task list page
│           ├── loading.tsx     # Loading state
│           ├── new/
│           │   └── page.tsx    # Create task page
│           └── [id]/
│               ├── page.tsx    # Task detail page
│               └── edit/
│                   └── page.tsx # Edit task page
├── components/
│   ├── tasks/
│   │   ├── TaskList.tsx
│   │   ├── TaskCard.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskDetail.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Card.tsx
│       └── Dialog.tsx
├── lib/
│   ├── api.ts                  # API client
│   └── utils.ts                # Helper functions
├── types/
│   └── index.ts                # TypeScript types
├── package.json
├── tailwind.config.ts
└── next.config.ts
```

## API Contracts

### List Tasks
```
GET /api/{user_id}/tasks?status=pending
Authorization: Bearer <jwt_token>

Response 200:
[
  {
    "id": 1,
    "user_id": "user-123",
    "title": "Buy groceries",
    "description": "Milk, eggs",
    "completed": false,
    "created_at": "2026-01-16T10:00:00Z",
    "updated_at": "2026-01-16T10:00:00Z"
  }
]

Response 401: { "detail": "Not authenticated" }
Response 403: { "detail": "Access denied" }
```

### Create Task
```
POST /api/{user_id}/tasks
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

Response 201:
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-16T10:00:00Z",
  "updated_at": "2026-01-16T10:00:00Z"
}

Response 422: { "detail": "Validation error", "errors": [...] }
```

### Get Task
```
GET /api/{user_id}/tasks/{task_id}
Authorization: Bearer <jwt_token>

Response 200: { Task object }
Response 404: { "detail": "Task not found" }
```

### Update Task
```
PUT /api/{user_id}/tasks/{task_id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
  "title": "Updated title",
  "description": "Updated description"
}

Response 200: { Updated Task object }
Response 404: { "detail": "Task not found" }
```

### Delete Task
```
DELETE /api/{user_id}/tasks/{task_id}
Authorization: Bearer <jwt_token>

Response 204: (No content)
Response 404: { "detail": "Task not found" }
```

### Toggle Complete
```
PATCH /api/{user_id}/tasks/{task_id}/complete
Authorization: Bearer <jwt_token>

Response 200: { Task with toggled completed status }
Response 404: { "detail": "Task not found" }
```

## Error Handling Strategy

### Backend Errors
| Exception | Status | Response |
|-----------|--------|----------|
| `jwt.ExpiredSignatureError` | 401 | `{"detail": "Token expired"}` |
| `jwt.InvalidTokenError` | 401 | `{"detail": "Invalid token"}` |
| User mismatch | 403 | `{"detail": "Access denied"}` |
| Task not found | 404 | `{"detail": "Task not found"}` |
| Validation error | 422 | `{"detail": "Validation error", "errors": [...]}` |
| Database error | 500 | `{"detail": "Internal server error"}` |

### Frontend Error Handling
```typescript
// Error boundary for unexpected errors
// Toast notifications for API errors
// Form validation errors inline
// 401 → redirect to login
// 403 → show access denied message
// 404 → show not found page
// 500 → show generic error with retry
```

## Security Considerations

### Authentication
- JWT token required on all endpoints
- Token verified on every request
- Token expiration enforced
- Shared secret between frontend and backend

### Authorization
- User ID in URL must match JWT user_id
- All database queries filtered by user_id
- No cross-user data access possible

### Input Validation
- Title: 1-200 characters, required
- Description: max 1000 characters, optional
- All inputs sanitized via Pydantic

### Data Protection
- No sensitive data in responses
- SQL injection prevented via SQLModel ORM
- XSS prevented via React escaping

## Testing Strategy

### Backend Unit Tests
- [ ] JWT verification (valid, expired, invalid)
- [ ] Task model validation
- [ ] User access verification

### Backend Integration Tests
- [ ] Create task with valid data
- [ ] Create task with invalid data (422)
- [ ] List tasks with filters
- [ ] Get task by ID (found, not found)
- [ ] Update task (valid, invalid, not found)
- [ ] Delete task (found, not found)
- [ ] Toggle completion
- [ ] User isolation (403 on other user's task)

### Frontend Unit Tests
- [ ] TaskCard renders correctly
- [ ] TaskForm validation
- [ ] API client methods

### E2E Tests
- [ ] Complete CRUD workflow
- [ ] Authentication flow integration
- [ ] Error handling displays

## Performance Considerations

### Backend
- Async database operations
- Connection pooling
- Indexed queries
- Pagination (future enhancement)

### Frontend
- Server Components for initial data fetch
- Optimistic updates for better UX
- Loading states for all async operations
- Minimal client-side JavaScript

## Dependencies

### Backend (pyproject.toml)
```toml
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlmodel>=0.0.14",
    "asyncpg>=0.29.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "pydantic-settings>=2.1.0",
    "pyjwt>=2.8.0",
]
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "better-auth": "latest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "@types/react": "^19.0.0"
  }
}
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| JWT secret mismatch | Auth fails | Document shared secret setup clearly |
| Database connection issues | App down | Health check endpoint, connection pooling |
| Large task lists | Slow response | Add pagination in future phase |
| Optimistic update failures | Data inconsistency | Rollback mechanism, error toasts |

## Definition of Done

- [ ] All 6 API endpoints implemented and tested
- [ ] All 4 frontend components implemented
- [ ] All 4 pages/routes functional
- [ ] JWT authentication working end-to-end
- [ ] User isolation verified
- [ ] All acceptance criteria from spec met
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] No critical or high-severity bugs
- [ ] Code reviewed and approved

---

**Created**: 2026-01-16
**Last Updated**: 2026-01-16
**Spec Reference**: `specs/task-crud/spec.md`
**Author**: Claude Code (Spec-Driven Development)
