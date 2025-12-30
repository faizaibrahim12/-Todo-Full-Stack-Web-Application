# Implementation Plan: Frontend Todo App

**Branch**: `001-frontend-todo` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-frontend-todo/spec.md`

## Summary

Full-stack multi-user todo application with Next.js 16+ frontend and FastAPI backend. Users can register, login, and manage personal tasks with complete CRUD operations. Authentication uses Better Auth with JWT tokens shared between frontend and backend. Data persists in Neon PostgreSQL via SQLModel ORM.

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.11+ (Backend)
**Primary Dependencies**: Next.js 16+, Tailwind CSS, Better Auth (Frontend); FastAPI, SQLModel, python-jose (Backend)
**Storage**: Neon PostgreSQL (Serverless)
**Testing**: Jest + React Testing Library (Frontend), pytest (Backend)
**Target Platform**: Web (Desktop + Mobile responsive)
**Project Type**: Web application (monorepo with frontend + backend)
**Performance Goals**: <2s page load, <500ms API response
**Constraints**: Must work on mobile (320px+), JWT token auth, user data isolation
**Scale/Scope**: Multi-user, ~100 concurrent users for hackathon demo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Test-First | PASS | Unit tests for components, API integration tests |
| Simplicity | PASS | Minimal viable feature set, no over-engineering |
| Security | PASS | JWT auth, password hashing, user isolation |
| Observability | PASS | Error handling, API logging |

## Project Structure

### Documentation (this feature)

```text
specs/001-frontend-todo/
├── spec.md              # Feature specification
├── plan.md              # This file (architecture plan)
├── research.md          # Phase 0 research findings
├── data-model.md        # Database schema design
├── quickstart.md        # Setup and run guide
├── contracts/           # API contracts
│   └── openapi.yaml     # OpenAPI 3.1 specification
├── checklists/          # Quality checklists
│   └── requirements.md  # Spec quality validation
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment configuration
├── database.py                # Database connection setup
├── models/
│   ├── __init__.py
│   ├── user.py                # User SQLModel
│   └── task.py                # Task SQLModel
├── schemas/
│   ├── __init__.py
│   ├── user.py                # User Pydantic schemas
│   └── task.py                # Task Pydantic schemas
├── routes/
│   ├── __init__.py
│   ├── auth.py                # Auth endpoints (signup, login, logout)
│   └── tasks.py               # Task CRUD endpoints
├── middleware/
│   ├── __init__.py
│   └── auth.py                # JWT verification middleware
├── utils/
│   ├── __init__.py
│   ├── auth.py                # JWT and password utilities
│   └── exceptions.py          # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_auth.py           # Auth endpoint tests
│   └── test_tasks.py          # Task endpoint tests
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables

frontend/
├── app/
│   ├── layout.tsx             # Root layout with providers
│   ├── page.tsx               # Home page (redirect logic)
│   ├── globals.css            # Global styles + Tailwind
│   ├── login/
│   │   └── page.tsx           # Login page
│   ├── signup/
│   │   └── page.tsx           # Signup page
│   └── dashboard/
│       └── page.tsx           # Task dashboard (protected)
├── components/
│   ├── ui/
│   │   ├── Button.tsx         # Reusable button
│   │   ├── Input.tsx          # Form input
│   │   └── Card.tsx           # Card container
│   ├── auth/
│   │   ├── LoginForm.tsx      # Login form component
│   │   └── SignupForm.tsx     # Signup form component
│   └── tasks/
│       ├── TaskList.tsx       # Task list container
│       ├── TaskItem.tsx       # Individual task row
│       ├── AddTaskForm.tsx    # New task input
│       └── EmptyState.tsx     # No tasks message
├── lib/
│   ├── api.ts                 # API client with auth
│   ├── auth.ts                # Auth context and hooks
│   └── types.ts               # TypeScript interfaces
├── hooks/
│   ├── useAuth.ts             # Auth state hook
│   └── useTasks.ts            # Tasks data hook
├── middleware.ts              # Next.js route protection
├── next.config.js             # Next.js configuration
├── tailwind.config.js         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
├── package.json               # Node dependencies
└── .env.local                 # Environment variables
```

**Structure Decision**: Web application monorepo with separate frontend and backend directories. This provides clear separation of concerns, independent deployment options, and matches the hackathon requirements.

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                               │
├─────────────────────────────────────────────────────────────────────┤
│  Next.js Frontend (localhost:3000)                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │
│  │ Login Page  │  │ Signup Page │  │    Task Dashboard           │  │
│  │             │  │             │  │  ┌─────────────────────┐    │  │
│  │ [Email    ] │  │ [Email    ] │  │  │ + Add Task         │    │  │
│  │ [Password ] │  │ [Password ] │  │  ├─────────────────────┤    │  │
│  │ [Login Btn] │  │ [Signup   ] │  │  │ ☐ Task 1    [🗑️]   │    │  │
│  └─────────────┘  └─────────────┘  │  │ ☑ Task 2    [🗑️]   │    │  │
│                                     │  │ ☐ Task 3    [🗑️]   │    │  │
│                                     │  └─────────────────────┘    │  │
│                                     └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP + JWT Bearer Token
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FastAPI Backend (localhost:8000)                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    JWT Auth Middleware                        │   │
│  │  • Verify token signature (BETTER_AUTH_SECRET)                │   │
│  │  • Extract user_id from claims                                │   │
│  │  • Validate user_id matches path parameter                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│         ┌────────────────────┼────────────────────┐                 │
│         ▼                    ▼                    ▼                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐       │
│  │ Auth Routes │     │ Task Routes │     │ Health Check    │       │
│  │ /api/auth/* │     │ /api/users/ │     │ /health         │       │
│  │             │     │ {id}/tasks  │     │                 │       │
│  └─────────────┘     └─────────────┘     └─────────────────┘       │
│         │                    │                                       │
│         └────────────────────┼───────────────────────────────────   │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      SQLModel ORM                             │   │
│  │  • User model (id, email, password_hash, timestamps)          │   │
│  │  • Task model (id, title, completed, user_id, timestamps)     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ PostgreSQL Protocol (SSL)
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Neon PostgreSQL (Serverless)                                        │
│  ┌─────────────────────┐     ┌─────────────────────────────────┐    │
│  │      users          │     │           tasks                  │    │
│  │ ─────────────────── │     │ ─────────────────────────────── │    │
│  │ id (PK)             │◄────│ user_id (FK)                    │    │
│  │ email (UNIQUE)      │     │ id (PK)                         │    │
│  │ password_hash       │     │ title                           │    │
│  │ created_at          │     │ completed                       │    │
│  │ updated_at          │     │ created_at, updated_at          │    │
│  └─────────────────────┘     └─────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ Database │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ 1. Enter creds │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ 2. POST /auth/login             │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │ 3. Query user  │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ 4. User data   │
     │                │                │<───────────────│
     │                │                │                │
     │                │                │ 5. Verify password
     │                │                │    Generate JWT│
     │                │                │                │
     │                │ 6. { user, token }              │
     │                │<───────────────│                │
     │                │                │                │
     │                │ 7. Store token │                │
     │                │    (localStorage/cookie)        │
     │                │                │                │
     │ 8. Redirect to │                │                │
     │    dashboard   │                │                │
     │<───────────────│                │                │
     │                │                │                │
```

### Task CRUD Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ Database │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ 1. Add task    │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ 2. POST /users/{id}/tasks       │
     │                │    + Authorization: Bearer JWT  │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │ 3. Verify JWT  │
     │                │                │    Extract user_id
     │                │                │    Check id match
     │                │                │                │
     │                │                │ 4. INSERT task │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ 5. New task    │
     │                │                │<───────────────│
     │                │                │                │
     │                │ 6. TaskResponse│                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ 7. Update UI   │                │
     │ 8. See new task│    (optimistic)│                │
     │<───────────────│                │                │
     │                │                │                │
```

## Key Decisions

### 1. JWT Token Storage

**Decision**: Store JWT in localStorage with httpOnly cookie fallback consideration

**Rationale**:
- localStorage is simpler for hackathon scope
- Token easily accessible for Authorization header
- httpOnly cookies would be more secure (XSS protection) but add complexity

**Trade-offs**:
- Vulnerable to XSS (mitigated by input sanitization)
- Simpler implementation vs. cookie-based auth

### 2. API Path Structure

**Decision**: `/api/users/{user_id}/tasks` with user_id in path

**Rationale**:
- Explicit resource ownership in URL
- Easy to debug and understand
- Backend validates path user_id matches JWT user_id

### 3. State Management

**Decision**: React Context for auth state, component state for tasks

**Rationale**:
- Auth state needed globally (protected routes)
- Task state localized to dashboard
- No need for Redux/Zustand complexity

### 4. Error Handling Strategy

**Decision**: Centralized API client with error transformation

**Rationale**:
- Consistent error format across app
- User-friendly messages (no technical details)
- Easy to add retry logic later

## Security Considerations

1. **Password Hashing**: bcrypt with salt (handled by Better Auth)
2. **JWT Verification**: Signature check with shared secret
3. **User Isolation**: All queries filter by user_id from JWT
4. **Input Validation**: Frontend + Backend validation
5. **CORS**: Restrict to frontend origin only
6. **SQL Injection**: Prevented by SQLModel parameterized queries

## Complexity Tracking

> No constitution violations requiring justification.

| Decision | Complexity Level | Justification |
|----------|------------------|---------------|
| Monorepo structure | Low | Two directories, clear separation |
| JWT auth | Medium | Standard pattern, well-documented |
| SQLModel ORM | Low | Type-safe, minimal boilerplate |
| Tailwind CSS | Low | Utility-first, no custom CSS needed |

## Dependencies

### Backend (Python)

```
fastapi>=0.100.0
uvicorn>=0.23.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0
pytest>=7.0.0
httpx>=0.24.0
```

### Frontend (Node.js)

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "better-auth": "latest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "@types/react": "^18.2.0",
    "@types/node": "^20.0.0"
  }
}
```

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Follow task order (backend first, then frontend)
3. Test each component as implemented
4. Integration test full auth + task flow

## Related Artifacts

- [Feature Specification](./spec.md)
- [Research Findings](./research.md)
- [Data Model](./data-model.md)
- [API Contract](./contracts/openapi.yaml)
- [Quickstart Guide](./quickstart.md)
