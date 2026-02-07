# Feature: Task CRUD Operations

## Overview

**Feature Name**: Task CRUD Operations
**Phase**: II - Full-Stack Web Application
**Priority**: High (Core Feature)
**Status**: Draft

## Problem Statement

Users need a web-based interface to manage their personal todo tasks. The system must allow users to create, read, update, and delete tasks while ensuring complete data isolation between users.

## User Stories

### US-001: Create Task
**As a** logged-in user
**I want to** create a new task with a title and optional description
**So that** I can track items I need to complete

**Acceptance Criteria:**
- [ ] User can enter a title (required, 1-200 characters)
- [ ] User can enter a description (optional, max 1000 characters)
- [ ] Task is created with `completed: false` by default
- [ ] Task is associated with the authenticated user
- [ ] User receives confirmation of successful creation
- [ ] User is redirected to task list after creation
- [ ] Validation errors are displayed for invalid input

### US-002: View Task List
**As a** logged-in user
**I want to** see all my tasks in a list
**So that** I can have an overview of what I need to do

**Acceptance Criteria:**
- [ ] User sees only their own tasks (not other users')
- [ ] Each task displays: title, completion status, created date
- [ ] Tasks are sorted by creation date (newest first)
- [ ] Completed tasks are visually distinct (e.g., strikethrough)
- [ ] Empty state shown when no tasks exist
- [ ] Loading state shown while fetching tasks

### US-003: View Task Details
**As a** logged-in user
**I want to** view the full details of a specific task
**So that** I can see all information including description

**Acceptance Criteria:**
- [ ] User can click on a task to view details
- [ ] Detail view shows: title, description, status, created_at, updated_at
- [ ] User can navigate back to task list
- [ ] 404 page shown if task doesn't exist
- [ ] 403 error if trying to view another user's task

### US-004: Update Task
**As a** logged-in user
**I want to** edit an existing task's title and description
**So that** I can correct or add information

**Acceptance Criteria:**
- [ ] User can edit title (required, 1-200 characters)
- [ ] User can edit description (optional, max 1000 characters)
- [ ] `updated_at` timestamp is automatically updated
- [ ] User receives confirmation of successful update
- [ ] Validation errors are displayed for invalid input
- [ ] User cannot edit another user's task

### US-005: Delete Task
**As a** logged-in user
**I want to** delete a task I no longer need
**So that** I can keep my task list clean

**Acceptance Criteria:**
- [ ] User can delete a task from list view or detail view
- [ ] Confirmation dialog shown before deletion
- [ ] Task is permanently removed from database
- [ ] User receives confirmation of successful deletion
- [ ] User cannot delete another user's task

### US-006: Mark Task as Complete/Incomplete
**As a** logged-in user
**I want to** toggle a task's completion status
**So that** I can track my progress

**Acceptance Criteria:**
- [ ] User can toggle completion with a single click/tap
- [ ] Completed tasks show visual indicator (checkbox, strikethrough)
- [ ] `updated_at` timestamp is automatically updated
- [ ] Toggle is immediate (optimistic update preferred)
- [ ] User cannot toggle another user's task

## Functional Requirements

### FR-001: Task Data Model
```
Task {
  id: integer (auto-generated, primary key)
  user_id: string (foreign key to users, required)
  title: string (1-200 characters, required)
  description: string (max 1000 characters, nullable)
  completed: boolean (default: false)
  created_at: timestamp (auto-generated)
  updated_at: timestamp (auto-updated)
}
```

### FR-002: API Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/{user_id}/tasks` | List all tasks | Yes |
| POST | `/api/{user_id}/tasks` | Create new task | Yes |
| GET | `/api/{user_id}/tasks/{id}` | Get task by ID | Yes |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Yes |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | Yes |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | Yes |

### FR-003: Query Parameters
| Endpoint | Parameter | Values | Description |
|----------|-----------|--------|-------------|
| GET /tasks | status | all, pending, completed | Filter by completion status |

### FR-004: Request/Response Schemas

**Create Task Request:**
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)"
}
```

**Update Task Request:**
```json
{
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 1000 chars)"
}
```

**Task Response:**
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-16T10:00:00Z",
  "updated_at": "2026-01-16T10:00:00Z"
}
```

**Error Response:**
```json
{
  "detail": "Task not found",
  "status_code": 404
}
```

## Non-Functional Requirements

### NFR-001: Performance
- API response time < 200ms for single task operations
- List endpoint < 500ms for up to 100 tasks
- Frontend renders task list within 1 second

### NFR-002: Security
- All endpoints require valid JWT token
- User can only access their own tasks
- Input sanitization to prevent XSS
- SQL injection prevention via ORM

### NFR-003: Usability
- Mobile-responsive design
- Clear visual feedback for all actions
- Accessible (WCAG 2.1 AA compliance)
- Intuitive navigation

### NFR-004: Reliability
- Graceful error handling with user-friendly messages
- No data loss on network failures (show retry option)
- Optimistic updates with rollback on failure

## UI Components

### TaskList Component
- Displays list of tasks
- Shows loading spinner while fetching
- Shows empty state when no tasks
- Supports filtering by status
- Each task item is clickable

### TaskCard Component
- Displays single task summary
- Checkbox for completion toggle
- Delete button with confirmation
- Click to navigate to detail

### TaskForm Component
- Used for create and edit
- Title input (required)
- Description textarea (optional)
- Submit and Cancel buttons
- Validation error display

### TaskDetail Component
- Full task information display
- Edit and Delete buttons
- Back to list navigation
- Completion toggle

## Pages/Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/dashboard/tasks` | TaskList | Main task list page |
| `/dashboard/tasks/new` | TaskForm | Create new task |
| `/dashboard/tasks/[id]` | TaskDetail | View task details |
| `/dashboard/tasks/[id]/edit` | TaskForm | Edit existing task |

## Error Handling

| Error Code | Scenario | User Message |
|------------|----------|--------------|
| 400 | Invalid input | "Please check your input and try again" |
| 401 | Not authenticated | Redirect to login |
| 403 | Access denied | "You don't have permission to access this task" |
| 404 | Task not found | "Task not found" |
| 422 | Validation error | Show field-specific errors |
| 500 | Server error | "Something went wrong. Please try again later" |

## Testing Requirements

### Unit Tests
- [ ] Task model validation
- [ ] TaskForm component
- [ ] TaskCard component
- [ ] API client functions

### Integration Tests
- [ ] Create task flow (frontend → API → database)
- [ ] List tasks with filtering
- [ ] Update task flow
- [ ] Delete task flow
- [ ] Toggle completion flow

### E2E Tests
- [ ] Complete CRUD workflow
- [ ] User isolation (user A cannot see user B's tasks)
- [ ] Authentication required for all operations
- [ ] Error handling displays correct messages

## Dependencies

### Backend
- FastAPI
- SQLModel
- asyncpg (Neon PostgreSQL)
- PyJWT

### Frontend
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (for JWT)

## Out of Scope (Phase II)

- Task priorities
- Task categories/tags
- Due dates and reminders
- Task search
- Task sorting options
- Recurring tasks
- Bulk operations

## Success Metrics

- [ ] All 5 CRUD operations functional
- [ ] User isolation verified (security test)
- [ ] API response times within NFR limits
- [ ] All acceptance criteria met
- [ ] Zero critical bugs in testing

---

**Created**: 2026-01-16
**Last Updated**: 2026-01-16
**Author**: Claude Code (Spec-Driven Development)
