# Task Manager Frontend

A Next.js 16 frontend application for managing personal todo tasks with JWT authentication.

## Features

- **Authentication**: Email/password login and signup using Better Auth
- **Task Management**: Complete CRUD operations for tasks
- **Filters**: View all, pending, or completed tasks
- **Optimistic Updates**: Instant UI feedback for toggle completion
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **User Isolation**: Users can only see their own tasks
- **Accessible**: WCAG 2.1 AA compliant components

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Authentication**: Better Auth with JWT
- **HTTP Client**: Axios
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React
- **Date Formatting**: date-fns

## Prerequisites

- Node.js 20+
- Backend API running at http://localhost:8000
- PostgreSQL database (Neon)

## Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=your-postgresql-connection-string
```

## Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The application will be available at http://localhost:3000

## Project Structure

```
frontend/
├── app/                          # Next.js App Router pages
│   ├── page.tsx                  # Login page
│   ├── signup/                   # Sign up page
│   ├── dashboard/                # Protected dashboard routes
│   │   ├── layout.tsx            # Dashboard layout with nav
│   │   └── tasks/                # Task management pages
│   │       ├── page.tsx          # Task list
│   │       ├── new/              # Create task
│   │       └── [id]/             # Task detail & edit
│   └── api/auth/[...all]/        # Better Auth API routes
├── components/                   # React components
│   ├── ui/                       # Reusable UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── textarea.tsx
│   │   ├── dialog.tsx
│   │   └── spinner.tsx
│   └── tasks/                    # Task-specific components
│       ├── TaskList.tsx          # Task list with filters
│       ├── TaskCard.tsx          # Individual task item
│       └── TaskForm.tsx          # Create/edit form
├── lib/                          # Library code
│   ├── auth.ts                   # Auth client
│   ├── auth-server.ts            # Auth server config
│   ├── types/                    # TypeScript types
│   │   └── task.ts
│   └── api/                      # API client
│       ├── client.ts             # Axios instance
│       └── tasks.ts              # Task API functions
└── .env.local                    # Environment variables
```

## API Integration

All API requests are made through the API client in `lib/api/tasks.ts`:

- **getTasks(userId, params?)** - List all tasks with optional status filter
- **getTask(userId, taskId)** - Get single task by ID
- **createTask(userId, data)** - Create new task
- **updateTask(userId, taskId, data)** - Update existing task
- **deleteTask(userId, taskId)** - Delete task
- **toggleTaskComplete(userId, taskId)** - Toggle completion status

All requests automatically include the JWT token in the Authorization header.

## Authentication Flow

1. User signs up at `/signup` or logs in at `/`
2. Better Auth creates a session and stores token in cookies
3. Protected routes check session and redirect if not authenticated
4. API requests include token from session cookie
5. Backend validates token and returns user-specific data

## Key Features Implementation

### Optimistic Updates
Task completion toggle updates UI immediately and rolls back on error.

### Status Filters
Filter tasks by "all", "pending", or "completed" status with real-time counts.

### Form Validation
Client-side validation for title (1-200 chars) and description (max 1000 chars).

### Error Handling
User-friendly error messages for all API errors with proper HTTP status handling.

### Loading States
Spinners and loading text during data fetching and mutations.

### Empty States
Helpful messages and CTAs when no tasks exist.

## Spec Compliance

This frontend implements all requirements from `specs/task-crud/spec.md`:

- ✅ All 6 user stories (US-001 to US-006)
- ✅ Complete CRUD operations
- ✅ Status filtering
- ✅ User isolation
- ✅ Mobile responsive
- ✅ Accessible components
- ✅ Optimistic updates
- ✅ Error handling
- ✅ Loading states

## Development

### Type Safety
All API responses and component props are fully typed with TypeScript.

### Code Quality
- ESLint for linting
- TypeScript strict mode
- Component-level error boundaries
- Proper ARIA labels for accessibility

### Testing
Run type checking:
```bash
npx tsc --noEmit
```

## Troubleshooting

**Session not persisting**: Ensure BETTER_AUTH_SECRET matches backend configuration.

**API errors**: Verify backend is running at NEXT_PUBLIC_API_URL and CORS is configured.

**Build errors**: Clear .next directory and node_modules, then reinstall dependencies.

**Auth errors**: Check DATABASE_URL is correct and database tables are migrated.

## License

Private - Phase II Hackathon Project
