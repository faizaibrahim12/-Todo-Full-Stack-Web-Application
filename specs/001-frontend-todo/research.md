# Research: Frontend Todo App

**Feature**: 001-frontend-todo
**Date**: 2025-12-27
**Purpose**: Resolve technical unknowns and establish best practices for implementation

## Research Areas

### 1. Monorepo Structure

**Decision**: Two-directory monorepo with `/frontend` (Next.js) and `/backend` (FastAPI)

**Rationale**:
- Clear separation of concerns between frontend and backend
- Independent deployment capabilities
- Shared environment variables at root level
- Simple structure for hackathon scope

**Alternatives Considered**:
- Turborepo/Nx monorepo: Overkill for two projects, adds complexity
- Single fullstack framework (Next.js API routes): Doesn't match FastAPI requirement
- Separate repositories: Harder to maintain shared configuration

### 2. Authentication Flow with Better Auth + JWT

**Decision**: Better Auth handles auth on frontend, JWT tokens passed to FastAPI backend

**Authentication Flow**:
```
1. User submits credentials → Frontend (Better Auth)
2. Better Auth validates → Creates session + JWT token
3. JWT stored in httpOnly cookie or localStorage
4. Frontend includes JWT in Authorization header for API calls
5. Backend verifies JWT using shared BETTER_AUTH_SECRET
6. Backend extracts user_id from JWT claims
```

**Rationale**:
- Better Auth provides ready-made signup/login components
- JWT enables stateless backend authentication
- Shared secret ensures both systems can verify tokens
- httpOnly cookies preferred for XSS protection

**Alternatives Considered**:
- Session-based auth: Requires session storage on backend, more complex
- OAuth providers only: Doesn't meet email/password requirement
- Custom auth implementation: Reinventing the wheel, security risks

### 3. Database Schema with SQLModel

**Decision**: Two tables - `users` and `tasks` with foreign key relationship

**Schema Design**:
```
users:
  - id: UUID (primary key)
  - email: String (unique, indexed)
  - password_hash: String
  - created_at: DateTime
  - updated_at: DateTime

tasks:
  - id: UUID (primary key)
  - title: String (max 500 chars)
  - completed: Boolean (default: false)
  - user_id: UUID (foreign key → users.id, indexed)
  - created_at: DateTime
  - updated_at: DateTime
```

**Rationale**:
- SQLModel combines SQLAlchemy + Pydantic for type safety
- UUID primary keys for security (non-sequential)
- Foreign key ensures referential integrity
- Index on user_id for efficient task queries

**Alternatives Considered**:
- NoSQL (MongoDB): Overkill, PostgreSQL sufficient
- Integer IDs: Sequential IDs can leak information
- Soft deletes: Out of scope for MVP

### 4. API Endpoint Design

**Decision**: RESTful API with user_id in path, JWT verification middleware

**Endpoint Structure**:
```
POST   /api/auth/signup          # Create account
POST   /api/auth/login           # Authenticate
POST   /api/auth/logout          # End session

GET    /api/users/{user_id}/tasks           # List user's tasks
POST   /api/users/{user_id}/tasks           # Create task
PATCH  /api/users/{user_id}/tasks/{task_id} # Update task
DELETE /api/users/{user_id}/tasks/{task_id} # Delete task
```

**Rationale**:
- User ID in path makes resource ownership explicit
- JWT middleware validates token before route handlers
- Middleware extracts user_id and compares with path parameter
- Standard REST verbs for CRUD operations

**Alternatives Considered**:
- GraphQL: Overkill for simple CRUD
- User ID only from token (not in path): Less explicit, harder to debug
- Nested routes (/users/{id}/tasks): Same as chosen, slightly different structure

### 5. Frontend-Backend Communication

**Decision**: Fetch API with Authorization Bearer header, centralized API client

**Implementation**:
```typescript
// lib/api.ts
const api = {
  async request(endpoint: string, options: RequestInit = {}) {
    const token = getAuthToken(); // From Better Auth
    return fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });
  }
};
```

**Rationale**:
- Native Fetch API, no extra dependencies
- Centralized client for consistent auth header injection
- Easy to add error handling and retry logic
- TypeScript types for request/response

**Alternatives Considered**:
- Axios: Extra dependency, Fetch is sufficient
- React Query/SWR: Good for caching, but adds complexity
- tRPC: Requires backend changes, overkill for REST API

### 6. Phase 1 Task Logic Reuse

**Decision**: Extract core task logic from Phase 1, adapt for multi-user context

**Reusable Components**:
- Task data structure (title, completed status)
- CRUD operation patterns
- Validation logic (title required, max length)

**Adaptations Required**:
- Add user_id to all task operations
- Filter queries by user_id
- Add authentication checks

**Rationale**:
- Proven logic from Phase 1
- Reduces implementation time
- Consistent behavior across phases

### 7. Environment Variables

**Decision**: Root-level `.env` files with framework-specific prefixes

**Variables**:
```
# Root .env (shared reference)
BETTER_AUTH_SECRET=<32+ char secret>
DATABASE_URL=postgresql://...@neon.tech/...

# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<same as root>

# Backend .env
DATABASE_URL=postgresql://...@neon.tech/...
BETTER_AUTH_SECRET=<same as root>
```

**Rationale**:
- BETTER_AUTH_SECRET must be identical for JWT verification
- DATABASE_URL only needed by backend
- NEXT_PUBLIC_ prefix exposes to browser (for API URL only)
- Separate .env files per project for deployment flexibility

**Alternatives Considered**:
- Single shared .env: Works locally but complicates deployment
- Hardcoded values: Security risk, not portable

## Technical Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend Framework | Next.js | 16+ |
| Frontend Language | TypeScript | 5.x |
| Frontend Styling | Tailwind CSS | 3.x |
| Frontend Auth | Better Auth | Latest |
| Backend Framework | FastAPI | 0.100+ |
| Backend ORM | SQLModel | 0.0.14+ |
| Database | Neon PostgreSQL | Serverless |
| Token Format | JWT | RS256/HS256 |

## Resolved Unknowns

| Unknown | Resolution |
|---------|------------|
| Auth flow | Better Auth (frontend) → JWT → FastAPI verification |
| Token storage | httpOnly cookie (preferred) or localStorage |
| User isolation | user_id in JWT claims, verified against path param |
| API structure | RESTful with /api/users/{user_id}/tasks pattern |
| Schema design | users + tasks tables with FK relationship |
| Env vars | Shared BETTER_AUTH_SECRET, separate DATABASE_URL |
