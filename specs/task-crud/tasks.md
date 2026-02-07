# Task CRUD Operations - Implementation Tasks

## Overview

**Feature**: Task CRUD Operations
**Spec Reference**: `specs/task-crud/spec.md`
**Plan Reference**: `specs/task-crud/plan.md`
**Total Tasks**: 32
**Status**: Ready for Implementation

---

## Phase 1: Backend Foundation

### T-001: Initialize Backend Project Structure
**Priority**: Critical | **Estimate**: 30 min | **Dependencies**: None

**Description**: Set up the FastAPI backend project with UV package manager and required dependencies.

**Acceptance Criteria**:
- [ ] Create `backend/` directory structure as per plan
- [ ] Initialize with `pyproject.toml` containing all dependencies
- [ ] Create `.env.example` with required environment variables
- [ ] Create `backend/app/__init__.py` and sub-packages
- [ ] Verify `uv sync` installs all dependencies

**Files to Create**:
- `backend/pyproject.toml`
- `backend/.env.example`
- `backend/app/__init__.py`
- `backend/app/models/__init__.py`
- `backend/app/routes/__init__.py`
- `backend/app/auth/__init__.py`

---

### T-002: Implement Configuration Management
**Priority**: Critical | **Estimate**: 20 min | **Dependencies**: T-001

**Description**: Create Pydantic Settings for environment-based configuration.

**Acceptance Criteria**:
- [ ] Create `config.py` with Settings class
- [ ] Load DATABASE_URL from environment
- [ ] Load BETTER_AUTH_SECRET from environment
- [ ] Load CORS_ORIGINS as list
- [ ] Use `@lru_cache` for singleton settings
- [ ] Validate settings load correctly

**Files to Create**:
- `backend/app/config.py`

**Test Cases**:
- Settings loads from `.env` file
- Missing required env var raises error

---

### T-003: Set Up Database Connection
**Priority**: Critical | **Estimate**: 30 min | **Dependencies**: T-002

**Description**: Configure async SQLModel connection to Neon PostgreSQL.

**Acceptance Criteria**:
- [ ] Create async engine with `asyncpg`
- [ ] Configure connection pooling
- [ ] Create async session factory
- [ ] Implement `get_session` dependency
- [ ] Implement `create_db_and_tables` function
- [ ] Handle connection URL conversion for async

**Files to Create**:
- `backend/app/database.py`

**Test Cases**:
- Database connection succeeds
- Session yields and commits correctly
- Rollback on exception

---

### T-004: Create Task SQLModel
**Priority**: Critical | **Estimate**: 30 min | **Dependencies**: T-003

**Description**: Define Task model and Pydantic schemas for request/response.

**Acceptance Criteria**:
- [ ] Create `Task` table model with all fields
- [ ] Add field validations (title length, description length)
- [ ] Create `TaskCreate` schema (title required, description optional)
- [ ] Create `TaskUpdate` schema (all fields optional)
- [ ] Create `TaskResponse` schema with `from_attributes`
- [ ] Add indexes on `user_id`, `completed`, `created_at`

**Files to Create**:
- `backend/app/models/task.py`

**Test Cases**:
- Task model validates title length (1-200)
- Task model validates description length (max 1000)
- TaskCreate rejects empty title
- TaskUpdate allows partial updates

---

### T-005: Implement JWT Verification
**Priority**: Critical | **Estimate**: 30 min | **Dependencies**: T-002

**Description**: Create JWT token verification using PyJWT with Better Auth secret.

**Acceptance Criteria**:
- [ ] Create `JWTPayload` class for decoded token data
- [ ] Implement `verify_jwt_token` function
- [ ] Handle `ExpiredSignatureError` → 401
- [ ] Handle `InvalidTokenError` → 401
- [ ] Extract `user_id` from `sub` or `user_id` claim
- [ ] Return structured payload on success

**Files to Create**:
- `backend/app/auth/jwt.py`

**Test Cases**:
- Valid token returns payload
- Expired token raises 401
- Invalid signature raises 401
- Malformed token raises 401

---

### T-006: Create Auth Dependencies
**Priority**: Critical | **Estimate**: 20 min | **Dependencies**: T-005

**Description**: Create FastAPI dependencies for authentication and authorization.

**Acceptance Criteria**:
- [ ] Implement `get_current_user` dependency using HTTPBearer
- [ ] Implement `verify_user_access` dependency
- [ ] Compare URL `user_id` with token `user_id`
- [ ] Raise 403 if user IDs don't match
- [ ] Return `JWTPayload` for use in route handlers

**Files to Create**:
- `backend/app/auth/dependencies.py`

**Test Cases**:
- Missing Authorization header → 401
- Valid token extracts user
- User ID mismatch → 403

---

### T-007: Implement List Tasks Endpoint
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-004, T-006

**Description**: Create GET endpoint to list all tasks for authenticated user.

**Acceptance Criteria**:
- [ ] Route: `GET /{user_id}/tasks`
- [ ] Require JWT authentication
- [ ] Verify user access (URL matches token)
- [ ] Filter tasks by `user_id`
- [ ] Support `status` query param (all, pending, completed)
- [ ] Order by `created_at` descending
- [ ] Return list of `TaskResponse`

**Files to Create/Modify**:
- `backend/app/routes/tasks.py`

**Test Cases**:
- Returns only user's tasks
- Filter by status=pending works
- Filter by status=completed works
- Empty list returns []
- Unauthorized returns 401

---

### T-008: Implement Create Task Endpoint
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-007

**Description**: Create POST endpoint to create a new task.

**Acceptance Criteria**:
- [ ] Route: `POST /{user_id}/tasks`
- [ ] Require JWT authentication
- [ ] Verify user access
- [ ] Accept `TaskCreate` body
- [ ] Set `user_id` from authenticated user
- [ ] Set `completed` to false by default
- [ ] Return 201 with created `TaskResponse`

**Files to Modify**:
- `backend/app/routes/tasks.py`

**Test Cases**:
- Valid data creates task
- Missing title returns 422
- Title too long returns 422
- Description too long returns 422
- Returns correct user_id

---

### T-009: Implement Get Task Endpoint
**Priority**: High | **Estimate**: 20 min | **Dependencies**: T-007

**Description**: Create GET endpoint to retrieve a single task by ID.

**Acceptance Criteria**:
- [ ] Route: `GET /{user_id}/tasks/{task_id}`
- [ ] Require JWT authentication
- [ ] Verify user access
- [ ] Query by `task_id` AND `user_id`
- [ ] Return 404 if not found
- [ ] Return `TaskResponse` if found

**Files to Modify**:
- `backend/app/routes/tasks.py`

**Test Cases**:
- Existing task returns data
- Non-existent task returns 404
- Other user's task returns 404 (not 403 - don't leak existence)

---

### T-010: Implement Update Task Endpoint
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-009

**Description**: Create PUT endpoint to update an existing task.

**Acceptance Criteria**:
- [ ] Route: `PUT /{user_id}/tasks/{task_id}`
- [ ] Require JWT authentication
- [ ] Verify user access
- [ ] Accept `TaskUpdate` body
- [ ] Update only provided fields
- [ ] Update `updated_at` timestamp
- [ ] Return 404 if not found
- [ ] Return updated `TaskResponse`

**Files to Modify**:
- `backend/app/routes/tasks.py`

**Test Cases**:
- Update title only works
- Update description only works
- Update both fields works
- Non-existent task returns 404
- Invalid data returns 422

---

### T-011: Implement Delete Task Endpoint
**Priority**: High | **Estimate**: 20 min | **Dependencies**: T-009

**Description**: Create DELETE endpoint to remove a task.

**Acceptance Criteria**:
- [ ] Route: `DELETE /{user_id}/tasks/{task_id}`
- [ ] Require JWT authentication
- [ ] Verify user access
- [ ] Query by `task_id` AND `user_id`
- [ ] Return 404 if not found
- [ ] Return 204 No Content on success

**Files to Modify**:
- `backend/app/routes/tasks.py`

**Test Cases**:
- Existing task is deleted
- Task no longer exists after deletion
- Non-existent task returns 404

---

### T-012: Implement Toggle Complete Endpoint
**Priority**: High | **Estimate**: 20 min | **Dependencies**: T-009

**Description**: Create PATCH endpoint to toggle task completion status.

**Acceptance Criteria**:
- [ ] Route: `PATCH /{user_id}/tasks/{task_id}/complete`
- [ ] Require JWT authentication
- [ ] Verify user access
- [ ] Toggle `completed` field (true↔false)
- [ ] Update `updated_at` timestamp
- [ ] Return 404 if not found
- [ ] Return updated `TaskResponse`

**Files to Modify**:
- `backend/app/routes/tasks.py`

**Test Cases**:
- Incomplete task becomes complete
- Complete task becomes incomplete
- Non-existent task returns 404

---

### T-013: Create Main FastAPI Application
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-007 through T-012

**Description**: Set up main FastAPI app with routers, middleware, and lifecycle.

**Acceptance Criteria**:
- [ ] Create FastAPI app with metadata
- [ ] Add CORS middleware with configured origins
- [ ] Include task router with `/api` prefix
- [ ] Add health check endpoint
- [ ] Implement lifespan for DB table creation
- [ ] Register exception handlers

**Files to Create**:
- `backend/app/main.py`
- `backend/app/routes/health.py`

**Test Cases**:
- App starts without errors
- CORS headers present
- Health endpoint returns 200

---

### T-014: Write Backend Integration Tests
**Priority**: High | **Estimate**: 45 min | **Dependencies**: T-013

**Description**: Create comprehensive integration tests for all task endpoints.

**Acceptance Criteria**:
- [ ] Set up test fixtures with mock auth
- [ ] Test all 6 endpoints with valid data
- [ ] Test authentication failures (401)
- [ ] Test authorization failures (403)
- [ ] Test not found scenarios (404)
- [ ] Test validation errors (422)
- [ ] Test user isolation

**Files to Create**:
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `backend/tests/test_tasks.py`

**Test Cases**:
- Full CRUD workflow passes
- User A cannot access User B's tasks
- All error codes return correctly

---

## Phase 2: Frontend Foundation

### T-015: Initialize Frontend Project Structure
**Priority**: Critical | **Estimate**: 30 min | **Dependencies**: None

**Description**: Set up Next.js 16+ project with App Router, TypeScript, and Tailwind CSS.

**Acceptance Criteria**:
- [ ] Create `frontend/` with Next.js 16+
- [ ] Configure TypeScript strict mode
- [ ] Set up Tailwind CSS
- [ ] Create folder structure as per plan
- [ ] Add `.env.example` with API URL
- [ ] Verify `npm run dev` works

**Files to Create**:
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/tailwind.config.ts`
- `frontend/next.config.ts`
- `frontend/.env.example`

---

### T-016: Create TypeScript Types
**Priority**: High | **Estimate**: 20 min | **Dependencies**: T-015

**Description**: Define TypeScript interfaces for Task and API responses.

**Acceptance Criteria**:
- [ ] Create `Task` interface matching backend response
- [ ] Create `CreateTaskInput` interface
- [ ] Create `UpdateTaskInput` interface
- [ ] Create `ApiError` interface
- [ ] Export all types from index

**Files to Create**:
- `frontend/types/index.ts`

---

### T-017: Implement API Client
**Priority**: Critical | **Estimate**: 45 min | **Dependencies**: T-016

**Description**: Create centralized API client with JWT token handling.

**Acceptance Criteria**:
- [ ] Create `ApiClient` class
- [ ] Implement `getAuthHeaders` for JWT
- [ ] Implement `list(userId, status?)` method
- [ ] Implement `create(userId, data)` method
- [ ] Implement `get(userId, taskId)` method
- [ ] Implement `update(userId, taskId, data)` method
- [ ] Implement `delete(userId, taskId)` method
- [ ] Implement `toggleComplete(userId, taskId)` method
- [ ] Handle errors with appropriate exceptions

**Files to Create**:
- `frontend/lib/api.ts`

---

### T-018: Create UI Base Components
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-015

**Description**: Create reusable UI components with Tailwind styling.

**Acceptance Criteria**:
- [ ] Create `Button` component (variants: primary, secondary, danger)
- [ ] Create `Input` component with label and error state
- [ ] Create `Textarea` component with label and error state
- [ ] Create `Card` component for task display
- [ ] Create `Spinner` loading component
- [ ] All components are accessible

**Files to Create**:
- `frontend/components/ui/Button.tsx`
- `frontend/components/ui/Input.tsx`
- `frontend/components/ui/Textarea.tsx`
- `frontend/components/ui/Card.tsx`
- `frontend/components/ui/Spinner.tsx`

---

### T-019: Create TaskCard Component
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-018

**Description**: Create TaskCard component for displaying a single task in the list.

**Acceptance Criteria**:
- [ ] Display task title and completion status
- [ ] Show checkbox for completion toggle
- [ ] Show delete button
- [ ] Completed tasks have strikethrough styling
- [ ] Click navigates to detail page
- [ ] Handle loading states for toggle/delete
- [ ] Emit events: `onToggle`, `onDelete`

**Files to Create**:
- `frontend/components/tasks/TaskCard.tsx`

---

### T-020: Create TaskList Component
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-019

**Description**: Create TaskList component for displaying all tasks with filtering.

**Acceptance Criteria**:
- [ ] Accept `initialTasks` prop
- [ ] Display filter tabs (All, Pending, Completed)
- [ ] Render TaskCard for each task
- [ ] Show empty state when no tasks
- [ ] Show loading spinner while fetching
- [ ] Handle toggle and delete actions
- [ ] Update local state on mutations

**Files to Create**:
- `frontend/components/tasks/TaskList.tsx`

---

### T-021: Create TaskForm Component
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-018

**Description**: Create TaskForm component for creating and editing tasks.

**Acceptance Criteria**:
- [ ] Title input (required, max 200 chars)
- [ ] Description textarea (optional, max 1000 chars)
- [ ] Client-side validation with error messages
- [ ] Submit and Cancel buttons
- [ ] Loading state during submission
- [ ] Pre-fill values when editing (optional `task` prop)
- [ ] Call `onSubmit` with form data

**Files to Create**:
- `frontend/components/tasks/TaskForm.tsx`

---

### T-022: Create TaskDetail Component
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-018

**Description**: Create TaskDetail component for displaying full task information.

**Acceptance Criteria**:
- [ ] Display all task fields
- [ ] Format dates nicely
- [ ] Show completion status with toggle button
- [ ] Edit button links to edit page
- [ ] Delete button with confirmation
- [ ] Back to list link
- [ ] Handle loading states

**Files to Create**:
- `frontend/components/tasks/TaskDetail.tsx`

---

### T-023: Create Dashboard Layout
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-015

**Description**: Create dashboard layout with navigation and auth check.

**Acceptance Criteria**:
- [ ] Create `(dashboard)` route group
- [ ] Add layout with header/navigation
- [ ] Show user info in header
- [ ] Add logout functionality
- [ ] Protect routes (redirect if not authenticated)
- [ ] Responsive design

**Files to Create**:
- `frontend/app/(dashboard)/layout.tsx`

---

### T-024: Create Task List Page
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-020, T-023

**Description**: Create the main task list page with Server Component data fetching.

**Acceptance Criteria**:
- [ ] Route: `/dashboard/tasks`
- [ ] Fetch tasks on server side
- [ ] Pass tasks to TaskList component
- [ ] Add "New Task" button linking to create page
- [ ] Create `loading.tsx` for Suspense
- [ ] Handle fetch errors gracefully

**Files to Create**:
- `frontend/app/(dashboard)/tasks/page.tsx`
- `frontend/app/(dashboard)/tasks/loading.tsx`

---

### T-025: Create New Task Page
**Priority**: High | **Estimate**: 20 min | **Dependencies**: T-021, T-023

**Description**: Create page for creating a new task.

**Acceptance Criteria**:
- [ ] Route: `/dashboard/tasks/new`
- [ ] Render TaskForm component
- [ ] Handle form submission via API
- [ ] Redirect to task list on success
- [ ] Show error messages on failure
- [ ] Cancel button returns to list

**Files to Create**:
- `frontend/app/(dashboard)/tasks/new/page.tsx`

---

### T-026: Create Task Detail Page
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-022, T-023

**Description**: Create page for viewing task details.

**Acceptance Criteria**:
- [ ] Route: `/dashboard/tasks/[id]`
- [ ] Fetch task by ID on server side
- [ ] Pass task to TaskDetail component
- [ ] Handle 404 (task not found)
- [ ] Handle 403 (access denied)
- [ ] Create `loading.tsx`

**Files to Create**:
- `frontend/app/(dashboard)/tasks/[id]/page.tsx`
- `frontend/app/(dashboard)/tasks/[id]/loading.tsx`

---

### T-027: Create Edit Task Page
**Priority**: High | **Estimate**: 20 min | **Dependencies**: T-021, T-026

**Description**: Create page for editing an existing task.

**Acceptance Criteria**:
- [ ] Route: `/dashboard/tasks/[id]/edit`
- [ ] Fetch task by ID
- [ ] Pre-fill TaskForm with existing data
- [ ] Handle form submission (update API)
- [ ] Redirect to detail page on success
- [ ] Show error messages on failure

**Files to Create**:
- `frontend/app/(dashboard)/tasks/[id]/edit/page.tsx`

---

## Phase 3: Integration & Testing

### T-028: Integrate Frontend with Backend
**Priority**: Critical | **Estimate**: 45 min | **Dependencies**: T-014, T-027

**Description**: Connect frontend to backend API and verify all flows work.

**Acceptance Criteria**:
- [ ] Configure API URL in environment
- [ ] Test create task flow end-to-end
- [ ] Test list tasks flow end-to-end
- [ ] Test update task flow end-to-end
- [ ] Test delete task flow end-to-end
- [ ] Test toggle completion flow end-to-end
- [ ] Verify JWT token is sent correctly

**Files to Modify**:
- `frontend/.env.local`
- `frontend/lib/api.ts` (if needed)

---

### T-029: Implement Error Handling UI
**Priority**: High | **Estimate**: 30 min | **Dependencies**: T-028

**Description**: Add comprehensive error handling throughout the frontend.

**Acceptance Criteria**:
- [ ] Create `error.tsx` for dashboard routes
- [ ] Create `not-found.tsx` for 404 pages
- [ ] Add toast notifications for success/error
- [ ] Handle 401 → redirect to login
- [ ] Handle 403 → show access denied
- [ ] Handle 500 → show generic error with retry

**Files to Create**:
- `frontend/app/(dashboard)/error.tsx`
- `frontend/app/(dashboard)/tasks/[id]/not-found.tsx`
- `frontend/components/ui/Toast.tsx`

---

### T-030: Write Frontend Unit Tests
**Priority**: Medium | **Estimate**: 45 min | **Dependencies**: T-028

**Description**: Create unit tests for frontend components.

**Acceptance Criteria**:
- [ ] Test TaskCard renders correctly
- [ ] Test TaskCard toggle functionality
- [ ] Test TaskForm validation
- [ ] Test TaskForm submission
- [ ] Test API client methods (mocked)
- [ ] All tests pass

**Files to Create**:
- `frontend/__tests__/components/TaskCard.test.tsx`
- `frontend/__tests__/components/TaskForm.test.tsx`
- `frontend/__tests__/lib/api.test.ts`

---

### T-031: Write E2E Tests
**Priority**: Medium | **Estimate**: 45 min | **Dependencies**: T-028

**Description**: Create end-to-end tests for critical user flows.

**Acceptance Criteria**:
- [ ] Test complete CRUD workflow
- [ ] Test authentication flow
- [ ] Test error handling displays
- [ ] Test user isolation (if possible)
- [ ] All E2E tests pass

**Files to Create**:
- `frontend/e2e/tasks.spec.ts`

---

### T-032: Final Polish and Documentation
**Priority**: Medium | **Estimate**: 30 min | **Dependencies**: T-031

**Description**: Final cleanup, optimization, and documentation.

**Acceptance Criteria**:
- [ ] Remove console.logs and debug code
- [ ] Verify all TypeScript types are correct
- [ ] Run linters (Ruff, ESLint) and fix issues
- [ ] Update README with setup instructions
- [ ] Document API endpoints
- [ ] Verify responsive design works
- [ ] Performance check (no unnecessary re-renders)

**Files to Modify**:
- `backend/README.md`
- `frontend/README.md`
- Root `README.md`

---

## Task Summary

| Phase | Tasks | Priority Breakdown |
|-------|-------|-------------------|
| Phase 1: Backend | T-001 to T-014 (14 tasks) | 6 Critical, 8 High |
| Phase 2: Frontend | T-015 to T-027 (13 tasks) | 2 Critical, 11 High |
| Phase 3: Integration | T-028 to T-032 (5 tasks) | 1 Critical, 2 High, 2 Medium |
| **Total** | **32 tasks** | |

## Dependency Graph

```
T-001 ──┬── T-002 ── T-003 ── T-004 ──┬── T-007 ── T-008
        │                             │      │
        │                             │      ├── T-009 ──┬── T-010
        │                             │      │          ├── T-011
        └── T-005 ── T-006 ───────────┘      │          └── T-012
                                             │
                                             └── T-013 ── T-014 ──┐
                                                                  │
T-015 ──┬── T-016 ── T-017                                       │
        │                                                         │
        ├── T-018 ──┬── T-019 ── T-020                           │
        │          ├── T-021                                      │
        │          └── T-022                                      │
        │                                                         │
        └── T-023 ──┬── T-024 ─────────────────────────────────┐ │
                    ├── T-025                                   │ │
                    ├── T-026 ── T-027                         │ │
                    │                                           │ │
                    └───────────────────────────────────────────┴─┴── T-028
                                                                        │
                                                              T-029 ────┤
                                                              T-030 ────┤
                                                              T-031 ────┤
                                                              T-032 ────┘
```

## Implementation Order (Recommended)

1. **Backend Foundation**: T-001 → T-002 → T-003 → T-004 → T-005 → T-006
2. **Backend API**: T-007 → T-008 → T-009 → T-010 → T-011 → T-012 → T-013 → T-014
3. **Frontend Setup**: T-015 → T-016 → T-017 → T-018
4. **Frontend Components**: T-019 → T-020 → T-021 → T-022
5. **Frontend Pages**: T-023 → T-024 → T-025 → T-026 → T-027
6. **Integration**: T-028 → T-029 → T-030 → T-031 → T-032

---

**Created**: 2026-01-16
**Last Updated**: 2026-01-16
**Spec Reference**: `specs/task-crud/spec.md`
**Plan Reference**: `specs/task-crud/plan.md`
**Author**: Claude Code (Spec-Driven Development)
