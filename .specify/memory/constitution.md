# Todo Full-Stack Web Application Constitution (Phase II)

## Project Overview

**Project Name**: Todo Full-Stack Web Application
**Phase**: II - Full-Stack Web Application
**Objective**: Transform the console app into a modern multi-user web application with persistent storage using Spec-Driven Development.

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All implementation MUST follow the Spec-Driven Development workflow:
- **Specify → Plan → Tasks → Implement**
- No code shall be written without a referenced Task ID
- Every code file must contain a comment linking to Task and Spec sections
- No manual coding allowed - refine specs until Claude Code generates correct output
- All changes must trace back to a validated specification

### II. Multi-User Architecture

- Every user has isolated data - users only see/modify their own tasks
- All API endpoints are scoped to authenticated user via `{user_id}` path parameter
- JWT tokens required for all API requests (except auth endpoints)
- User ownership enforced on every database operation
- Stateless authentication - backend verifies JWT without calling frontend

### III. Technology Stack (MANDATORY)

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Next.js (App Router) | 16+ |
| Backend | Python FastAPI | Latest |
| ORM | SQLModel | Latest |
| Database | Neon Serverless PostgreSQL | - |
| Authentication | Better Auth with JWT | Latest |
| Spec-Driven | Claude Code + Spec-Kit Plus | - |

Deviations from this stack require explicit justification and constitution amendment.

### IV. API Design Standards

**RESTful Conventions**:
- All routes under `/api/{user_id}/`
- Return JSON responses with consistent structure
- Use Pydantic models for request/response validation
- Handle errors with HTTPException and proper status codes

**Required Endpoints**:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/{user_id}/tasks | List all tasks |
| POST | /api/{user_id}/tasks | Create a new task |
| GET | /api/{user_id}/tasks/{id} | Get task details |
| PUT | /api/{user_id}/tasks/{id} | Update a task |
| DELETE | /api/{user_id}/tasks/{id} | Delete a task |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion |

**Security Requirements**:
- All endpoints require valid JWT token in `Authorization: Bearer <token>` header
- Requests without token receive 401 Unauthorized
- Invalid/expired tokens receive 401 Unauthorized
- User ID in URL must match JWT user ID

### V. Database Schema Standards

**Tasks Table**:
```sql
tasks (
  id: integer PRIMARY KEY,
  user_id: string NOT NULL REFERENCES users(id),
  title: string NOT NULL (1-200 chars),
  description: text NULLABLE (max 1000 chars),
  completed: boolean DEFAULT false,
  created_at: timestamp DEFAULT now(),
  updated_at: timestamp DEFAULT now()
)
```

**Required Indexes**:
- `tasks.user_id` - for filtering by user
- `tasks.completed` - for status filtering

**Data Integrity**:
- All queries must filter by authenticated user_id
- Foreign key constraints enforced
- No orphaned records allowed

### VI. Frontend Architecture

**Patterns**:
- Use Server Components by default
- Client Components only when interactivity required
- API calls through centralized `/lib/api.ts` client
- JWT token attached to every API request header

**Structure**:
```
frontend/
├── app/              # Pages and layouts (App Router)
├── components/       # Reusable UI components
├── lib/
│   └── api.ts       # API client with JWT handling
└── ...
```

**Styling**:
- Tailwind CSS only - no inline styles
- Responsive design required
- Follow existing component patterns

### VII. Backend Architecture

**Structure**:
```
backend/
├── main.py          # FastAPI app entry point
├── models.py        # SQLModel database models
├── routes/          # API route handlers
├── db.py            # Database connection
└── auth.py          # JWT verification middleware
```

**Conventions**:
- Async handlers preferred
- Dependency injection for database sessions
- Centralized error handling
- Environment variables for all configuration

### VIII. Authentication Flow (Better Auth + JWT)

**Flow**:
1. User logs in on Frontend → Better Auth creates session and issues JWT
2. Frontend stores JWT securely
3. Frontend includes JWT in `Authorization: Bearer <token>` header for API calls
4. Backend extracts and verifies JWT signature using shared secret
5. Backend decodes token to get user_id and validates against URL parameter
6. Backend filters all data by authenticated user

**Shared Secret**:
- Both services use `BETTER_AUTH_SECRET` environment variable
- Never commit secrets to repository
- Use `.env` files for local development

### IX. Security Requirements (NON-NEGOTIABLE)

- No secrets/tokens hardcoded in code
- All secrets via environment variables
- HTTPS required in production
- Input validation on all endpoints
- SQL injection prevention via SQLModel ORM
- XSS prevention in frontend
- CORS configured appropriately
- JWT expiration enforced (recommended: 7 days)

### X. Testing Standards

**Backend**:
- Unit tests for business logic
- Integration tests for API endpoints
- Test user isolation (user A cannot access user B's tasks)
- Test authentication (401 for missing/invalid tokens)

**Frontend**:
- Component tests for UI elements
- Integration tests for API client
- E2E tests for critical flows (login, CRUD operations)

### XI. Code Quality

- Type hints required (Python) / TypeScript strict mode (Frontend)
- Linting enforced (Ruff for Python, ESLint for TypeScript)
- No unused imports or variables
- Meaningful variable and function names
- Comments only where logic is non-obvious
- Maximum function length: 50 lines
- Single responsibility principle

### XII. Environment Configuration

**Required Environment Variables**:
```
# Backend
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=<shared-secret>

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<shared-secret>
```

**Files**:
- `.env.example` committed with placeholder values
- `.env` in `.gitignore` - never committed
- README documents all required variables

## Development Workflow

### Spec-Kit Plus Integration

1. **Specify**: Capture requirements in `specs/<feature>/spec.md`
2. **Plan**: Generate architecture in `specs/<feature>/plan.md`
3. **Tasks**: Break into testable tasks in `specs/<feature>/tasks.md`
4. **Implement**: Execute via Claude Code with task references

### Git Workflow

- Feature branches from `main`
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- PR required for merge to main
- All tests must pass before merge

### Commands

```bash
# Frontend
cd frontend && npm run dev

# Backend
cd backend && uvicorn main:app --reload --port 8000

# Both (Docker)
docker-compose up
```

## Deliverables Checklist

### Repository Structure
- [ ] `/frontend` - Next.js 16+ app with App Router
- [ ] `/backend` - Python FastAPI server
- [ ] `/specs` - Specification files
- [ ] `CLAUDE.md` - Claude Code instructions
- [ ] `README.md` - Setup instructions
- [ ] `.env.example` - Environment template
- [ ] `docker-compose.yml` - Local development

### Features (Basic Level)
- [ ] Add Task - Create new todo items with title and description
- [ ] Delete Task - Remove tasks from the list
- [ ] Update Task - Modify existing task details
- [ ] View Task List - Display all tasks with status indicators
- [ ] Mark as Complete - Toggle task completion status

### Authentication
- [ ] User signup with Better Auth
- [ ] User signin with Better Auth
- [ ] JWT token issuance
- [ ] JWT verification in FastAPI
- [ ] User data isolation

## Governance

- This constitution supersedes all other practices for Phase II
- Amendments require:
  1. Documentation of change rationale
  2. Impact analysis
  3. Migration plan if needed
- All code must verify compliance with these principles
- Constitution > Specify > Plan > Tasks hierarchy applies

## Acceptance Criteria

Phase II is complete when:
1. All 5 Basic Level features implemented as web application
2. RESTful API endpoints created and documented
3. Responsive frontend interface built
4. Data persisted in Neon Serverless PostgreSQL
5. User authentication via Better Auth with JWT
6. Multi-user isolation verified
7. All tests passing
8. Deployed to Vercel (frontend) with working backend

---

**Version**: 1.0.0 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-01-16

