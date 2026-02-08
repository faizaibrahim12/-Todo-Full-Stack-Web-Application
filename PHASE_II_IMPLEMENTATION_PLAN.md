# Phase II: Full-Stack Todo Web Application - Implementation Plan

**Created**: 2025-01-07
**Status**: Ready for Execution
**Estimated Effort**: 20-26 hours (full-stack implementation)
**Recommended Duration**: 2-3 days with 6-8 hours/day focus

---

## Executive Summary

Phase II transforms the Phase I console app (in-memory, CLI-based) into a production-ready web application:

- **Frontend**: Next.js 14 + React + TypeScript + TailwindCSS + Better Auth
- **Backend**: FastAPI + SQLModel + JWT authentication + Bcrypt hashing
- **Database**: PostgreSQL 13+ with Alembic migrations
- **Deployment**: Docker-ready architecture

**Key deliverables**: Multi-user authentication, persistent task storage, responsive web UI, RESTful API with 8 endpoints.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [API Specification](#api-specification)
5. [Implementation Phases](#implementation-phases)
6. [Task Execution Order](#task-execution-order)
7. [Backend Implementation Details](#backend-implementation-details)
8. [Frontend Implementation Details](#frontend-implementation-details)
9. [Authentication Integration Flow](#authentication-integration-flow)
10. [Database Migration Strategy](#database-migration-strategy)
11. [Success Criteria & Validation](#success-criteria--validation)

---

## Architecture Overview

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────┐
│         FRONTEND (Next.js 14)                   │
│  React Components + TypeScript + TailwindCSS    │
│  Better Auth + React Query + Zod                │
└────────────┬────────────────────────────────────┘
             │ HTTPS/REST JSON (Port 3000)
             ▼
┌─────────────────────────────────────────────────┐
│         BACKEND (FastAPI)                       │
│  Python 3.10+ + SQLModel + python-jose          │
│  JWT Middleware + CORS + Rate Limiting          │
└────────────┬────────────────────────────────────┘
             │ psycopg2 Driver (Port 5432)
             ▼
┌─────────────────────────────────────────────────┐
│         DATABASE (PostgreSQL 13+)               │
│  users table + tasks table + Alembic versions   │
└─────────────────────────────────────────────────┘
```

### Data Flow Examples

**Registration Flow:**
```
User fills form → Next.js form validation → POST /api/auth/register
→ FastAPI validates email/password → Bcrypt hash password
→ SQLModel creates user → PostgreSQL persists
→ JWT token issued → httpOnly cookie set → Redirect to dashboard
```

**Create Task Flow:**
```
User clicks "Add Task" → Modal form (client-side validation) → POST /api/tasks
→ JWT middleware verifies token → User context extracted
→ FastAPI validates schema → Task service checks ownership
→ SQLModel inserts task with user_id → PostgreSQL persists
→ React Query refetches list → UI updates optimistically
```

**Filtering Flow:**
```
User selects "Pending" filter → URL params updated (status=pending)
→ React Query requests GET /api/tasks?status=pending
→ FastAPI filters: WHERE user_id = :user_id AND completed = FALSE
→ Results returned as JSON array → React renders filtered list
```

---

## Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Frontend Framework** | Next.js | 14+ | App Router, SSR, built-in routing, TypeScript |
| **UI Library** | React | 18+ | Component model, hooks, ecosystem |
| **Language (Frontend)** | TypeScript | Latest | Type safety, better DX |
| **Styling** | TailwindCSS | 3+ | Utility-first, dark mode built-in, responsive |
| **State Management** | React Query | 5+ | Server state caching, sync across tabs |
| **Auth Client** | Better Auth | 0.5+ | Self-hosted, JWT support, type-safe |
| **Form Validation** | Zod | 3.22+ | TypeScript-first, runtime validation |
| **Backend Framework** | FastAPI | 0.104+ | Modern, async, auto OpenAPI docs, validation |
| **Language (Backend)** | Python | 3.10+ | Simplicity, rich ecosystem |
| **ORM** | SQLModel | 0.0.14+ | SQLAlchemy + Pydantic (type hints everywhere) |
| **Database** | PostgreSQL | 13+ | Reliable, multi-user, production-ready |
| **Auth Hashing** | passlib + bcrypt | Latest | Industry standard, cost factor 12 |
| **Token Management** | python-jose | 3.3+ | JWT creation/verification, flexible |
| **Migrations** | Alembic | 1.12+ | SQLAlchemy standard, version control |

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Constraints**:
- Email must be unique (prevents duplicate accounts)
- No plaintext passwords stored (always hashed with bcrypt)
- Timestamps track account lifecycle

### Tasks Table

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    due_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

**Constraints**:
- Foreign key to users (user ownership enforced)
- Cascading delete (delete user = delete their tasks)
- Default completed=FALSE (new tasks pending by default)
- Indexes on common queries (user_id, completed, created_at)

### Data Isolation

**Critical Security Property**: All queries MUST filter by `user_id`:
```python
# ❌ WRONG - returns all tasks
tasks = session.query(Task).filter(Task.completed == False).all()

# ✅ CORRECT - returns only current user's tasks
tasks = session.query(Task).filter(
    Task.user_id == current_user.id,
    Task.completed == False
).all()
```

---

## API Specification

### Authentication Endpoints

#### 1. POST `/api/auth/register`

**Purpose**: Create new user account

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2025-01-07T10:00:00Z"
}
```

**Response (400 Bad Request)**:
```json
{
  "error": "email_already_exists",
  "detail": "Email already registered"
}
```

**Security**:
- Password hashed with bcrypt (cost factor 12)
- Email validated (format check)
- Rate limited: 5 requests/minute per IP
- Password length 8-128 characters

#### 2. POST `/api/auth/login`

**Purpose**: Authenticate and receive JWT token

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Headers**:
```
Set-Cookie: access_token=eyJhbGc...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**Response (401 Unauthorized)**:
```json
{
  "error": "invalid_credentials",
  "detail": "Email or password incorrect"
}
```

**Security**:
- Returns generic error (prevent user enumeration)
- Token in httpOnly cookie (prevents XSS)
- Token expires in 7 days
- Secure flag set in production (HTTPS only)

#### 3. POST `/api/auth/logout`

**Purpose**: Invalidate user's token

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Response (200 OK)**:
```json
{
  "message": "Logged out successfully"
}
```

**Headers**:
```
Set-Cookie: access_token=; Max-Age=0; HttpOnly; Secure; SameSite=Strict
```

#### 4. GET `/api/auth/me`

**Purpose**: Get current authenticated user

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2025-01-07T10:00:00Z"
}
```

**Response (401 Unauthorized)**:
```json
{
  "error": "invalid_token",
  "detail": "Token expired or invalid"
}
```

---

### Task API Endpoints

**All task endpoints require**: `Authorization: Bearer <token>` header

#### 5. GET `/api/tasks`

**Purpose**: List user's tasks with filtering and sorting

**Query Parameters**:
- `status` (optional): `all` | `pending` | `completed` (default: `all`)
- `sort` (optional): `created` | `title` (default: `created`)
- `order` (optional): `asc` | `desc` (default: `desc`)

**Request**:
```
GET /api/tasks?status=pending&sort=created&order=desc
Authorization: Bearer eyJhbGc...
```

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Implement authentication",
      "description": "Add JWT support to backend",
      "completed": false,
      "due_date": "2025-01-15",
      "created_at": "2025-01-07T10:00:00Z",
      "updated_at": "2025-01-07T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Status Codes**:
- 200: Success
- 401: Invalid/expired token
- 500: Server error

#### 6. POST `/api/tasks`

**Purpose**: Create new task

**Request**:
```json
{
  "title": "Review pull request",
  "description": "Check authentication implementation",
  "due_date": "2025-01-15"
}
```

**Response (201 Created)**:
```json
{
  "id": 2,
  "user_id": 1,
  "title": "Review pull request",
  "description": "Check authentication implementation",
  "completed": false,
  "due_date": "2025-01-15",
  "created_at": "2025-01-07T10:05:00Z",
  "updated_at": "2025-01-07T10:05:00Z"
}
```

**Validation**:
- title: Required, 1-255 characters
- description: Optional, 0-5000 characters
- due_date: Optional, ISO 8601 format (YYYY-MM-DD)

#### 7. PATCH `/api/tasks/{id}`

**Purpose**: Update task details

**Request**:
```json
{
  "title": "Review pull requests",
  "description": "Check auth and API endpoints",
  "due_date": "2025-01-20",
  "completed": false
}
```

**Response (200 OK)**: Updated task object

**Status Codes**:
- 200: Updated
- 404: Task not found (or not owned by user)
- 400: Invalid data

#### 8. PATCH `/api/tasks/{id}/toggle`

**Purpose**: Toggle task completion status (convenience endpoint)

**Request**:
```
PATCH /api/tasks/1/toggle
Authorization: Bearer eyJhbGc...
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "completed": true,
  "updated_at": "2025-01-07T10:10:00Z"
}
```

#### 9. DELETE `/api/tasks/{id}`

**Purpose**: Delete task

**Request**:
```
DELETE /api/tasks/1
Authorization: Bearer eyJhbGc...
```

**Response (204 No Content)**: Empty response

**Status Codes**:
- 204: Deleted
- 404: Task not found
- 401: Unauthorized

---

### Error Response Format

All errors follow consistent format:

```json
{
  "error": "error_code",
  "detail": "Human-readable message"
}
```

**Common Status Codes**:
- 400: Bad Request (validation error)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (user doesn't own resource)
- 404: Not Found
- 429: Too Many Requests (rate limited)
- 500: Internal Server Error

---

## Implementation Phases

### Phase P1: Foundation & Setup (2-3 hours)

**Goal**: Backend infrastructure ready, database connected

**Tasks**:
- [T001] Initialize backend project structure
- [T002] Configure database connection & settings
- [T003] Create SQLModel entities (User, Task)
- [T004] Initialize Alembic migrations
- [T005] Create initial migration

**Deliverable**:
- Backend project runs on `localhost:5000`
- PostgreSQL connected and migrations applied
- Swagger docs available at `/docs`

**Can Parallelize**: T002, T003, T004 (different files, no dependencies)

---

### Phase P2: Authentication (4-5 hours)

**Goal**: Users can register, login, receive JWT tokens

**Tasks**:
- [T006] Create JWT utilities (token creation/verification)
- [T007] Implement password hashing (bcrypt)
- [T008] Create auth service (registration, login logic)
- [T009] Create auth routes (POST /register, /login, /logout, GET /me)
- [T010] Add auth middleware and CORS

**Deliverable**:
- User can register with email/password
- User can login and receive JWT token
- Protected endpoints reject requests without token
- CORS allows requests from frontend origin

**Test with curl**:
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

**Can Parallelize**: T006, T007 (security utilities), T008 (service layer), T009 (routes)

---

### Phase P3: Task API (3-4 hours)

**Goal**: Complete REST API for task management

**Tasks**:
- [T011] Create task schemas (Pydantic models for request/response)
- [T012] Create task service (business logic: CRUD, filtering, sorting)
- [T013] Create task routes (all 5 task endpoints)

**Deliverable**:
- GET /api/tasks returns user's tasks (filtered by user_id)
- POST /api/tasks creates new task
- PATCH /api/tasks/{id} updates task
- PATCH /api/tasks/{id}/toggle toggles completion
- DELETE /api/tasks/{id} deletes task
- All enforce user ownership (404 if not owned)
- Filtering by status works (all/pending/completed)
- Sorting works (created_at, title)

**Test with curl**:
```bash
TOKEN="<token_from_login>"

# Create task
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","description":"Study async framework"}'

# List tasks
curl -X GET "http://localhost:5000/api/tasks?status=pending" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Phase P4: Frontend Setup (2-3 hours)

**Goal**: Next.js project initialized with routing and auth integration

**Tasks**:
- [T014] Initialize Next.js 14 project with TypeScript
- [T015] Set up TailwindCSS and dark mode
- [T016] Configure Better Auth
- [T017] Create API client (fetch wrapper with auth)

**Deliverable**:
- Next.js runs on `localhost:3000`
- All pages render without errors
- API client can authenticate and get token
- Better Auth session management working
- TypeScript type checking passes

**Project Structure**:
```
frontend/
├── app/
│   ├── layout.tsx (root layout)
│   ├── page.tsx (home/redirect)
│   ├── auth/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── dashboard/
│       └── page.tsx (task list)
├── components/
│   ├── AuthForm.tsx
│   ├── TaskList.tsx
│   └── ... (other components)
├── lib/
│   ├── api-client.ts
│   ├── auth-client.ts
│   └── types.ts
└── package.json
```

**Can Parallelize**: T014, T015, T016, T017 (different concerns)

---

### Phase P5: Frontend UI (5-6 hours)

**Goal**: Fully functional web interface with all features

**Tasks**:
- [T018] Create auth components (login/register forms)
- [T019] Create task components (task list, task item, task form)
- [T020] Create filter and sort controls
- [T021] Implement dark mode toggle
- [T022] Add notifications (toast system)

**Deliverable**:
- Login page works (email/password validation)
- Register page works (form validation, errors)
- Dashboard displays user's tasks
- Can create, edit, delete tasks
- Can toggle task completion
- Can filter (all/pending/completed)
- Can sort (by date or title)
- Dark mode persists in localStorage
- Success/error notifications appear
- Responsive on mobile/tablet/desktop

**Component Hierarchy**:
```
App
├── AuthLayout (login/register pages)
│   └── AuthForm (reusable login/register form)
└── DashboardLayout (authenticated pages)
    ├── TaskList (main task display)
    │   ├── TaskFilters (status + sort controls)
    │   └── TaskItem (individual task)
    ├── TaskForm (create/edit modal)
    ├── ThemeToggle (light/dark mode)
    └── ToastContainer (notifications)
```

**Can Parallelize**: T018, T019, T020 (UI components), T021 (theme), T022 (notifications)

---

### Phase P6: Integration & Polish (4-5 hours)

**Goal**: Production-ready, tested, error-handled, fully integrated

**Tasks**:
- [T023] Implement React Query mutations (CREATE, UPDATE, DELETE)
- [T024] Add comprehensive error handling
- [T025] Add validation at form level (Zod)
- [T026] Implement loading states and optimistic updates
- [T027] Add rate limiting awareness
- [T028] E2E testing (happy path)
- [T029] Performance optimization
- [T030] Documentation and deployment prep

**Deliverable**:
- All mutations update cache correctly
- Error messages clear and actionable
- Form validation catches errors before submission
- Loading states prevent double submissions
- Optimistic updates improve perceived performance
- Rate limit 429 responses handled gracefully
- E2E flow works: register → login → create task → complete → logout
- Page load times < 1 second
- API documentation complete
- Deployment checklist ready

---

## Task Execution Order

### Critical Path (Minimal Dependencies)

**Can execute sequentially**:

```
T001 (backend init)
  ↓
T002, T003, T004 (run in parallel)
  ↓
T005 (migration created, ready to apply)
  ↓
T006, T007, T008 (security utils + service)
  ↓
T009, T010 (routes + middleware)
  ↓
T011, T012, T013 (task API)
  ↓
[BACKEND READY - can test with curl]
  ↓
T014, T015, T016, T017 (frontend init - can start in parallel with T006+)
  ↓
T018, T019, T020, T021, T022 (UI components - can parallelize)
  ↓
T023, T024, T025, T026, T027 (integration)
  ↓
T028, T029, T030 (testing + deployment)
```

### Recommended Parallelization (2-Developer Team)

**Developer 1 (Backend)**:
- T001 → T002, T003, T004 (parallel) → T005
- T006, T007, T008 (parallel) → T009, T010
- T011, T012, T013 (parallel)

**Developer 2 (Frontend)** - can start after T005 (database ready):
- T014 → T015, T016, T017 (parallel)
- T018, T019, T020 (parallel) → T021 → T022
- Wait for backend T013, then start T023

**Integration** (both together):
- T023 → T024 → T025 → T026 → T027
- T028 (test full flow)
- T029, T030 (final touches)

### Single Developer Route (Sequential)

**Recommended order** (build top-to-bottom):
1. T001-T005 (backend foundation)
2. T006-T010 (auth backend)
3. T011-T013 (task API)
4. **PAUSE** - test backend with curl
5. T014-T017 (frontend foundation)
6. T018-T022 (frontend UI)
7. T023-T027 (integration)
8. T028-T030 (testing + polish)

**Estimated timeline**:
- Backend: 10-12 hours (P1-P3)
- Frontend: 8-10 hours (P4-P6)
- Total: 20-26 hours

---

## Backend Implementation Details

### Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Pydantic Settings
│   ├── database.py                # SQLAlchemy engine & session
│   ├── exceptions.py              # Custom exception classes
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py              # User SQLModel
│   │   ├── schemas.py             # Pydantic request/response
│   │   ├── service.py             # Business logic
│   │   ├── routes.py              # FastAPI routes
│   │   └── jwt.py                 # Token utilities
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── models.py              # Task SQLModel
│   │   ├── schemas.py             # Validation schemas
│   │   ├── service.py             # CRUD & filtering
│   │   └── routes.py              # API endpoints
│   └── middleware/
│       ├── __init__.py
│       └── auth.py                # JWT verification middleware
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       └── ... (future migrations)
├── pyproject.toml
├── .env.example
└── README.md
```

### Key Modules

#### src/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
```

#### src/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    with SessionLocal() as session:
        yield session
```

#### src/auth/models.py
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### src/auth/jwt.py
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .models import User

def create_access_token(user: User) -> str:
    """Generate JWT token for user"""
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise InvalidTokenException()
```

#### src/auth/service.py
```python
from passlib.context import CryptContext
from sqlmodel import Session, select
from .models import User
from .jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def register(self, session: Session, email: str, password: str) -> User:
        # Check if user exists
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            raise EmailAlreadyExistsException()

        # Hash password
        hashed_pwd = pwd_context.hash(password)

        # Create user
        user = User(email=email, hashed_password=hashed_pwd)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def login(self, session: Session, email: str, password: str) -> dict:
        # Find user
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise InvalidCredentialsException()

        # Verify password
        if not pwd_context.verify(password, user.hashed_password):
            raise InvalidCredentialsException()

        # Generate token
        token = create_access_token(user)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 604800  # 7 days
        }
```

#### src/auth/routes.py
```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from .service import AuthService
from .models import User
from ..database import get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()

@router.post("/register")
async def register(
    email: str,
    password: str,
    session: Session = Depends(get_session)
):
    user = auth_service.register(session, email, password)
    return {"id": user.id, "email": user.email}

@router.post("/login")
async def login(
    email: str,
    password: str,
    session: Session = Depends(get_session)
):
    return auth_service.login(session, email, password)
```

### Key Principles

1. **Separation of Concerns**:
   - Models (SQLModel) - data structure
   - Schemas (Pydantic) - validation + serialization
   - Service layer - business logic
   - Routes - HTTP handlers

2. **User Ownership Enforcement**:
   ```python
   # ✅ Always filter by current_user.id
   tasks = session.exec(
       select(Task).where(
           (Task.user_id == current_user.id) &
           (Task.completed == False)
       )
   ).all()
   ```

3. **Error Handling**:
   ```python
   from fastapi import HTTPException

   class InvalidTokenException(HTTPException):
       def __init__(self):
           super().__init__(
               status_code=401,
               detail={"error": "invalid_token", "detail": "Token expired or invalid"}
           )
   ```

4. **Middleware Pattern**:
   ```python
   # Extract user from token in middleware, pass to endpoints
   @app.middleware("http")
   async def auth_middleware(request, call_next):
       token = request.cookies.get("access_token")
       if not token:
           return JSONResponse({"error": "unauthorized"}, status_code=401)
       # ... verify token, add to request.state.user
   ```

---

## Frontend Implementation Details

### Project Structure

```
frontend/
├── app/
│   ├── layout.tsx                 # Root layout (providers)
│   ├── page.tsx                   # Home (redirect to dashboard)
│   ├── auth/
│   │   ├── login/
│   │   │   └── page.tsx           # Login page
│   │   ├── register/
│   │   │   └── page.tsx           # Register page
│   │   └── layout.tsx             # Auth layout (no sidebar)
│   ├── dashboard/
│   │   ├── page.tsx               # Task list
│   │   ├── settings/
│   │   │   └── page.tsx           # Settings (future)
│   │   └── layout.tsx             # Dashboard layout (with sidebar)
│   └── api/
│       └── auth/
│           └── [...auth]/ route.ts # Better Auth handler
├── components/
│   ├── auth/
│   │   ├── AuthForm.tsx           # Login/Register form
│   │   └── ProtectedRoute.tsx     # Auth guard
│   ├── dashboard/
│   │   ├── TaskList.tsx           # Task list container
│   │   ├── TaskItem.tsx           # Single task row
│   │   ├── TaskForm.tsx           # Create/Edit modal
│   │   └── TaskFilters.tsx        # Status/Sort controls
│   ├── common/
│   │   ├── ThemeToggle.tsx        # Dark mode switcher
│   │   ├── ToastContainer.tsx     # Notifications
│   │   └── Loading.tsx            # Spinner/skeleton
│   └── Providers.tsx              # QueryClientProvider
├── lib/
│   ├── api-client.ts              # Fetch wrapper with auth
│   ├── auth-client.ts             # Better Auth client
│   ├── hooks.ts                   # useAuth, useTask, useTasks
│   ├── types.ts                   # TypeScript interfaces
│   ├── theme-context.tsx          # Dark mode logic
│   ├── toast-context.tsx          # Notification system
│   └── utils.ts                   # Helper functions
├── middleware.ts                  # Next.js auth middleware
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── .env.local.example
```

### Key Files

#### lib/api-client.ts
```typescript
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000") {
    this.baseUrl = baseUrl;
  }

  async request<T>(
    method: string,
    path: string,
    body?: unknown,
    token?: string
  ): Promise<T> {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      credentials: "include", // Send cookies
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.error);
    }

    return response.json();
  }

  // Auth endpoints
  async register(email: string, password: string) {
    return this.request("/api/auth/register", { email, password });
  }

  async login(email: string, password: string) {
    return this.request("/api/auth/login", { email, password });
  }

  // Task endpoints
  async getTasks(token: string, status = "all", sort = "created") {
    return this.request(
      `/api/tasks?status=${status}&sort=${sort}`,
      undefined,
      token
    );
  }

  async createTask(token: string, task: CreateTaskInput) {
    return this.request("/api/tasks", task, token);
  }

  async updateTask(token: string, id: number, updates: UpdateTaskInput) {
    return this.request(`/api/tasks/${id}`, updates, token);
  }

  async toggleTask(token: string, id: number) {
    return this.request(`/api/tasks/${id}/toggle`, undefined, token);
  }

  async deleteTask(token: string, id: number) {
    return this.request(`/api/tasks/${id}`, undefined, token);
  }
}

export const apiClient = new ApiClient();
```

#### lib/hooks.ts
```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./api-client";
import { useAuthClient } from "./auth-client";

export function useTasks(status = "all") {
  const { session } = useAuthClient();

  return useQuery({
    queryKey: ["tasks", status],
    queryFn: () => apiClient.getTasks(session?.user?.accessToken, status),
    enabled: !!session,
  });
}

export function useCreateTask() {
  const { session } = useAuthClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input) => apiClient.createTask(session?.user?.accessToken, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

export function useUpdateTask() {
  const { session } = useAuthClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }) =>
      apiClient.updateTask(session?.user?.accessToken, id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

export function useToggleTask() {
  const { session } = useAuthClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id) => apiClient.toggleTask(session?.user?.accessToken, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

export function useDeleteTask() {
  const { session } = useAuthClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id) => apiClient.deleteTask(session?.user?.accessToken, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}
```

#### components/dashboard/TaskList.tsx
```typescript
"use client";

import { useState } from "react";
import { useTasks } from "@/lib/hooks";
import TaskItem from "./TaskItem";
import TaskForm from "./TaskForm";
import TaskFilters from "./TaskFilters";
import { Loading, Empty } from "@/components/common";

export default function TaskList() {
  const [status, setStatus] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const { data, isLoading, error } = useTasks(status);

  if (isLoading) return <Loading />;
  if (error) return <div className="error">{error.message}</div>;
  if (!data?.tasks?.length) return <Empty />;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <TaskFilters status={status} onStatusChange={setStatus} />
        <button
          onClick={() => setShowForm(true)}
          className="btn btn-primary"
        >
          + Add Task
        </button>
      </div>

      {showForm && (
        <TaskForm onClose={() => setShowForm(false)} />
      )}

      <div className="space-y-2">
        {data.tasks.map((task) => (
          <TaskItem key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}
```

#### components/dashboard/TaskItem.tsx
```typescript
"use client";

import { useToggleTask, useDeleteTask, useUpdateTask } from "@/lib/hooks";
import { useState } from "react";

export default function TaskItem({ task }) {
  const [editing, setEditing] = useState(false);
  const toggle = useToggleTask();
  const delete_ = useDeleteTask();
  const update = useUpdateTask();

  return (
    <div className="task-item">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => toggle.mutate(task.id)}
        className="mr-3"
      />
      <div className="flex-1">
        <h3 className={task.completed ? "line-through text-gray-500" : ""}>
          {task.title}
        </h3>
        <p className="text-sm text-gray-600">{task.description}</p>
      </div>
      <button onClick={() => setEditing(true)}>Edit</button>
      <button onClick={() => delete_.mutate(task.id)}>Delete</button>
    </div>
  );
}
```

### Key Patterns

1. **Authentication Flow**:
   ```typescript
   // Login redirects to dashboard, which checks session
   // Dashboard only renders if session exists
   if (!session) {
     redirect("/auth/login");
   }
   ```

2. **React Query Mutations**:
   ```typescript
   // Mutation optimistically updates cache
   const { mutate } = useMutation({
     mutationFn: (data) => apiClient.create(data),
     onSuccess: (response) => {
       queryClient.setQueryData(["items"], (old) => [...old, response]);
     },
   });
   ```

3. **Form Validation with Zod**:
   ```typescript
   import { z } from "zod";

   const taskSchema = z.object({
     title: z.string().min(1).max(255),
     description: z.string().max(5000).optional(),
     dueDate: z.string().date().optional(),
   });

   // Validate before submit
   const result = taskSchema.safeParse(formData);
   if (!result.success) {
     setErrors(result.error.flatten().fieldErrors);
   }
   ```

4. **Dark Mode with Context**:
   ```typescript
   export function ThemeProvider({ children }) {
     const [isDark, setIsDark] = useState(false);

     return (
       <ThemeContext.Provider value={{ isDark, setIsDark }}>
         <div className={isDark ? "dark" : ""}>
           {children}
         </div>
       </ThemeContext.Provider>
     );
   }
   ```

---

## Authentication Integration Flow

### Complete User Journey

#### 1. Registration

```
User visits http://localhost:3000
  ↓
Redirects to /auth/login (not authenticated)
  ↓
User clicks "Register" link → /auth/register
  ↓
Fills form: email, password, confirm password
  ↓
Frontend validates with Zod:
  - Email format: valid email
  - Password length: 8-128 chars
  - Passwords match
  ↓
Frontend submits POST /api/auth/register
  {
    "email": "user@example.com",
    "password": "SecurePass123"
  }
  ↓
Backend validates:
  - Email format
  - Email not already registered
  - Password strength
  ↓
Backend hashes password with bcrypt (cost factor 12)
  ↓
Backend creates user in PostgreSQL
  ↓
Backend generates JWT token (7 day expiry)
  ↓
Backend sets httpOnly cookie: access_token=<JWT>
  ↓
Frontend receives 201 response
  ↓
Better Auth session updated with user data
  ↓
Redirect to /dashboard
  ↓
Dashboard renders with user's tasks (empty for new user)
```

#### 2. Login

```
User visits /auth/login
  ↓
Fills form: email, password
  ↓
Frontend validates with Zod
  ↓
Frontend submits POST /api/auth/login
  ↓
Backend finds user by email
  ↓
Backend verifies password with bcrypt.verify()
  ↓
If invalid: returns 401 with generic error
  ("Email or password incorrect" - prevent user enumeration)
  ↓
If valid: generates JWT token
  ↓
Backend sets httpOnly cookie: access_token=<JWT>
  ↓
Frontend receives token in response + cookie
  ↓
Better Auth stores token in session
  ↓
Redirect to /dashboard
```

#### 3. Protected Route Access

```
User accesses /dashboard
  ↓
Next.js middleware checks for token in cookies
  ↓
If no token → redirect to /auth/login
  ↓
If token exists → verify expiration + signature
  ↓
If invalid/expired → redirect to /auth/login
  ↓
If valid → allow access, store user context
  ↓
Dashboard component fetches tasks via React Query
  ↓
API call includes header: Authorization: Bearer <token>
  ↓
FastAPI middleware:
  - Extracts token from header
  - Verifies JWT signature and expiration
  - Decodes user_id from payload
  - Adds current_user to request.state
  ↓
Route handler accesses current_user
  ↓
Service layer filters queries: WHERE user_id = current_user.id
  ↓
Response includes only user's own data
```

#### 4. Logout

```
User clicks logout button
  ↓
Frontend calls POST /api/auth/logout
  ↓
Backend clears httpOnly cookie
  Set-Cookie: access_token=; Max-Age=0; HttpOnly
  ↓
Frontend clears Better Auth session
  ↓
Next.js middleware detects no token
  ↓
Redirect to /auth/login
```

### Token Flow Diagram

```
┌────────────────────────────────────────┐
│       User Submits Credentials         │
│   (email, password via HTTPS/POST)     │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│   Backend Validates & Hashes           │
│   (bcrypt verify, lookup user)         │
└────────────┬───────────────────────────┘
             │
             ├─→ Invalid: 401 error
             │   (generic error message)
             │
             └─→ Valid: Continue
                    │
                    ▼
         ┌──────────────────────┐
         │ Generate JWT Token   │
         │ ┌──────────────────┐ │
         │ │ Header: HS256    │ │
         │ │ Payload:         │ │
         │ │  - user_id       │ │
         │ │  - email         │ │
         │ │  - exp (7 days)  │ │
         │ │ Signature: HMAC  │ │
         │ └──────────────────┘ │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Set HttpOnly Cookie  │
         │                      │
         │ Set-Cookie:          │
         │ access_token=<JWT>   │
         │ HttpOnly             │
         │ Secure (prod only)   │
         │ SameSite=Strict      │
         │ Max-Age=604800       │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Return to Client     │
         │                      │
         │ {                    │
         │   "access_token"     │
         │   "token_type"       │
         │   "expires_in"       │
         │ }                    │
         └──────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Store in Session      │
        │ (Better Auth)         │
        │                       │
        │ Subsequent requests:  │
        │ Authorization:        │
        │ Bearer <token>        │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Verify Token on       │
        │ Protected Routes      │
        │                       │
        │ ✓ Signature valid?    │
        │ ✓ Not expired?        │
        │ ✓ User exists?        │
        │                       │
        │ ✓ All pass → Access   │
        │ ✗ Any fail → 401      │
        └───────────────────────┘
```

---

## Database Migration Strategy

### Migration Workflow

#### Step 1: Initial Setup (T004-T005)

```bash
# Initialize Alembic in backend/
cd backend
alembic init alembic

# This creates:
# - alembic/ directory
# - alembic/env.py (migration environment)
# - alembic/script.py.mako (migration template)
# - alembic/versions/ (empty directory for migrations)
```

#### Step 2: Create Initial Migration (T005)

```bash
# Auto-generate migration from SQLModel definitions
alembic revision --autogenerate -m "Initial schema: users and tasks tables"

# This creates: alembic/versions/001_initial_schema.py
# Contains:
# - CreateTable('users') with columns
# - CreateTable('tasks') with columns
# - CreateIndex on email, user_id, completed, created_at
```

#### Step 3: Apply Migrations (During T002)

```bash
# Upgrade database to latest migration
alembic upgrade head

# This:
# 1. Reads all migration files in versions/
# 2. Checks alembic_version table for current version
# 3. Runs new migrations in order
# 4. Updates alembic_version table
```

### Migration File Structure

**alembic/versions/001_initial_schema.py**:
```python
"""Initial schema: users and tasks tables

Revision ID: 001
Revises:
Create Date: 2025-01-07 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])

def downgrade() -> None:
    op.drop_table('tasks')
    op.drop_table('users')
```

### Verification Steps

**After running migrations**, verify:

```sql
-- Check users table exists
\dt users

-- Check tasks table exists
\dt tasks

-- Check indexes
\di

-- Expected output:
-- idx_users_email (on users.email)
-- idx_tasks_user_id (on tasks.user_id)
-- idx_tasks_completed (on tasks.completed)
-- idx_tasks_created_at (on tasks.created_at)
```

### Adding Future Migrations

When adding new features (e.g., task tags in Phase III):

```bash
# Add column to Task model in src/tasks/models.py
# tags: str | None = Field(default=None)

# Auto-generate migration
alembic revision --autogenerate -m "Add tags column to tasks table"

# This creates: alembic/versions/002_add_tags.py

# Apply migration
alembic upgrade head
```

---

## Success Criteria & Validation

### Backend Success Criteria

#### ✅ Server Running
```bash
cd backend
pip install -e .
fastapi run src/main.py
# Expected: "Uvicorn running on http://127.0.0.1:8000"
```

#### ✅ Database Connected
```python
from src.database import engine
from src.auth.models import User
engine.echo = True  # Log SQL queries
users = session.query(User).all()
# Expected: No connection errors, tables exist
```

#### ✅ API Documentation
```
Visit: http://localhost:8000/docs
Expected: Swagger UI with all endpoints listed
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- GET /api/tasks
- POST /api/tasks
- PATCH /api/tasks/{id}
- PATCH /api/tasks/{id}/toggle
- DELETE /api/tasks/{id}
```

#### ✅ Authentication Endpoints Work
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
# Expected: 201 Created with user ID

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
# Expected: 200 OK with access_token and expires_in

# Get Current User
TOKEN="<token_from_login>"
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK with user data
```

#### ✅ Task CRUD Works
```bash
TOKEN="<token_from_login>"

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task"}'
# Expected: 201 Created with task ID

# List tasks
curl -X GET "http://localhost:8000/api/tasks?status=all" \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK with array of tasks

# Update task
curl -X PATCH http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated title"}'
# Expected: 200 OK with updated task

# Toggle completion
curl -X PATCH http://localhost:8000/api/tasks/1/toggle \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK with updated task (completed=true)

# Delete task
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
# Expected: 204 No Content
```

#### ✅ User Ownership Enforced
```bash
# Create second account
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user2@example.com","password":"Test123!"}'

TOKEN2="<token_from_user2_login>"

# Try to access user1's task with user2's token
curl -X GET http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN2"
# Expected: 404 Not Found (or empty list if GET /tasks)
```

#### ✅ Rate Limiting Works
```bash
# Send 10 login requests rapid-fire
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
done
# Expected: 429 Too Many Requests on 6th+ request
```

### Frontend Success Criteria

#### ✅ Next.js Running
```bash
cd frontend
npm install
npm run dev
# Expected: "> Ready in 1.2s"
# Visit: http://localhost:3000
```

#### ✅ Auth Pages Load
```
http://localhost:3000/auth/login
Expected: Login form with email/password fields, "Register" link

http://localhost:3000/auth/register
Expected: Register form with email, password, confirm password
```

#### ✅ Complete Registration Flow
```
1. Visit /auth/register
2. Enter email: newuser@example.com
3. Enter password: SecurePass123
4. Confirm password: SecurePass123
5. Click "Sign up"
6. Expected: Redirect to /dashboard
7. Expected: "Welcome, newuser@example.com" message
8. Expected: Empty task list (new user)
```

#### ✅ Complete Login Flow
```
1. Visit /auth/login
2. Enter email: newuser@example.com
3. Enter password: SecurePass123
4. Click "Log in"
5. Expected: Redirect to /dashboard
6. Expected: Task list loads
```

#### ✅ Task CRUD in UI
```
Dashboard page:
1. Click "+ Add Task"
2. Modal appears with form
3. Enter title: "Buy groceries"
4. Enter description: "Milk, eggs, bread"
5. Click "Create"
6. Expected: Task appears in list, modal closes
7. Expected: Toast notification "Task created"

Edit task:
1. Click "Edit" button on task
2. Modal opens with form pre-filled
3. Change title: "Buy groceries & cook"
4. Click "Save"
5. Expected: Task updated in list

Toggle completion:
1. Click checkbox on task
2. Expected: Task marked as completed (strikethrough)
3. Click checkbox again
4. Expected: Task marked as pending (no strikethrough)

Delete task:
1. Click "Delete" button
2. Confirmation dialog appears
3. Click "Confirm"
4. Expected: Task removed from list
5. Expected: Toast notification "Task deleted"
```

#### ✅ Filtering Works
```
Task list with multiple tasks:
1. Click "Pending" filter
2. Expected: Only incomplete tasks shown
3. Click "Completed" filter
4. Expected: Only completed tasks shown
5. Click "All" filter
6. Expected: All tasks shown
```

#### ✅ Sorting Works
```
1. Click "Sort by Title" option
2. Expected: Tasks sorted alphabetically
3. Click "Sort by Date" option
4. Expected: Tasks sorted by created_at (newest first)
```

#### ✅ Dark Mode Works
```
1. Click theme toggle button (sun/moon icon)
2. Expected: Page colors invert (dark background, light text)
3. Refresh page (F5)
4. Expected: Dark mode persists (saved in localStorage)
5. Toggle back to light mode
6. Expected: Light colors restored
7. Refresh page
8. Expected: Light mode persists
```

#### ✅ Error Handling
```
Invalid login:
1. Click "Log in"
2. Enter wrong password
3. Expected: Error message "Email or password incorrect"
4. Expected: Form still visible (not cleared)

Required fields:
1. Try to create task without title
2. Expected: Form validation error "Title required"
3. Expected: Submit button disabled

Network error:
1. Stop backend server
2. Try to load dashboard
3. Expected: Error message "Failed to load tasks"
4. Expected: Retry button appears
```

#### ✅ Responsive Design
```
Mobile (iPhone SE, 375px width):
1. Open http://localhost:3000/dashboard
2. Expected: Layout stacks vertically
3. Expected: Touch targets are 44px+ height
4. Expected: Text readable without zooming

Tablet (iPad, 768px width):
1. Expected: Two-column layout or side-by-side
2. Expected: Task form spans full width

Desktop (1920px width):
1. Expected: Optimal layout with proper spacing
2. Expected: No horizontal scroll
```

### Integration Success Criteria

#### ✅ Frontend ↔ Backend Communication
```
1. Start both servers:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
2. Complete registration flow (frontend to backend)
3. Verify task appears in database:
   SELECT * FROM tasks WHERE user_id = 1;
4. Expected: Task persists across frontend page refreshes
```

#### ✅ JWT Authentication Enforced
```
1. Get valid token from login
2. Use token in task requests
3. Expected: Tasks returned
4. Modify token (change one character)
5. Try to access /api/tasks
6. Expected: 401 Unauthorized
```

#### ✅ User Data Isolation
```
1. Login as user1, create 3 tasks
2. Login as user2 (different account), create 2 tasks
3. Verify user1 sees 3 tasks, user2 sees 2 tasks
4. User1 cannot see user2's tasks
5. User2 cannot modify user1's tasks
```

#### ✅ Performance Acceptable
```
1. Open DevTools Network tab
2. Load dashboard page
3. Check load times:
   - Initial page load: < 1 second
   - API requests: < 500ms
   - Task list render: < 100ms
4. Check for console errors (should be none)
```

#### ✅ Notifications Show Correctly
```
Create task:
1. Create task via UI
2. Expected: Green success toast "Task created successfully"
3. Toast disappears after 3 seconds

Delete task:
1. Delete task via UI
2. Expected: Success toast, then task removed

Error:
1. Stop backend, try to create task
2. Expected: Red error toast with message
3. Expected: Task not added to list
```

---

## Deployment Readiness Checklist

### Backend (FastAPI)

- [ ] All environment variables documented in `.env.example`
- [ ] Database migrations tested and working
- [ ] CORS configured for production frontend URL
- [ ] JWT_SECRET set to strong random value (> 32 chars)
- [ ] Password hashing cost factor set to 12
- [ ] Error responses don't leak sensitive info
- [ ] Rate limiting active on auth endpoints
- [ ] Swagger docs available at /docs
- [ ] HTTPS enforced in production (secure=True)
- [ ] Database connection pooling configured
- [ ] Tests pass (if added)

### Frontend (Next.js)

- [ ] NEXT_PUBLIC_API_URL set to backend URL
- [ ] Build succeeds: `npm run build`
- [ ] Type checking passes: `tsc --noEmit`
- [ ] No console warnings or errors
- [ ] Dark mode persists correctly
- [ ] All routes require authentication (except /auth/*)
- [ ] Environment variables documented in `.env.local.example`
- [ ] Mobile responsive on iOS Safari, Android Chrome
- [ ] Performance metrics acceptable (Lighthouse 80+)

### Database (PostgreSQL)

- [ ] Backup strategy in place
- [ ] Indexes created for common queries
- [ ] Foreign key constraints enforced
- [ ] Connection pooling configured
- [ ] Automated backups scheduled
- [ ] Disaster recovery plan documented

### Testing

- [ ] Happy path flow tested (register → login → CRUD → logout)
- [ ] Error cases tested (wrong password, invalid input)
- [ ] Concurrent user requests tested
- [ ] Database migrations tested forwards and backwards

---

## Quick Reference: Common Commands

### Backend Commands

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# Run development server
fastapi run src/main.py  # or: uvicorn src.main:app --reload

# Database
alembic revision --autogenerate -m "description"
alembic upgrade head  # Apply migrations
alembic downgrade -1  # Rollback one migration

# API Docs
# Open: http://localhost:8000/docs
```

### Frontend Commands

```bash
# Setup
cd frontend
npm install

# Development
npm run dev  # Start dev server

# Building & Deployment
npm run build
npm start  # Run production build

# Quality checks
tsc --noEmit  # Type checking
npm run format  # Format code (if configured)
```

### Database Commands (psql)

```bash
# Connect to database
psql -U postgres -d todo_db

# List tables
\dt

# List indexes
\di

# Check migrations
SELECT * FROM alembic_version;

# Count tasks
SELECT COUNT(*) FROM tasks;

# View user tasks
SELECT * FROM tasks WHERE user_id = 1;
```

---

## Success Metrics

**After completing all 30 tasks, you should be able to**:

✅ Register a new user account via web form
✅ Login with email and password
✅ Create, edit, delete, and complete tasks
✅ Filter tasks by status (pending/completed/all)
✅ Sort tasks by date or title
✅ Toggle dark/light mode
✅ Logout securely
✅ Data persists across sessions
✅ Cannot access other users' tasks
✅ Receive clear error messages for validation failures

**System should be**:

✅ Production-ready with HTTPS/hashing/validation
✅ Responsive on mobile/tablet/desktop
✅ Fast (page loads < 1s)
✅ Secure (JWT, user isolation, CORS)
✅ Maintainable (modular architecture, clear separation of concerns)

---

## Document Index

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **This file** | Complete implementation plan & architecture | 30 min |
| `PHASE_II_SUMMARY.md` | Executive summary & tech stack decisions | 10 min |
| `PHASE_II_README.md` | Getting started guide & project overview | 15 min |
| `specs/phase-ii-web-app/spec.md` | Feature specification & user stories | 30 min |
| `specs/phase-ii-web-app/plan.md` | Detailed architecture & data models | 20 min |
| `specs/phase-ii-web-app/tasks.md` | 30 granular implementation tasks | 30 min |

---

## Next Steps

1. **Review this plan** - Understand architecture and dependencies
2. **Set up environment** - Python 3.10+, Node.js 18+, PostgreSQL
3. **Start with T001** - Backend project initialization
4. **Follow task sequence** - Use task execution order as guide
5. **Test after each phase** - Validate with curl/UI
6. **Track progress** - Mark tasks as completed
7. **Deploy when ready** - Follow deployment checklist

---

**Status**: ✅ **READY FOR EXECUTION**

**Estimated Timeline**: 20-26 hours (20-30% buffer for debugging)
**Recommended Pace**: 6-8 hours/day for 3 days
**Team Size**: 1 (sequential) or 2 (backend + frontend in parallel)

---

**Created**: 2025-01-07
**Based on**: Phase I Console App
**Next Phase**: Phase III (user profiles, task sharing, mobile app)
