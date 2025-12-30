# Tasks: Frontend Todo App

**Input**: Design documents from `/specs/001-frontend-todo/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Organization**: Tasks organized by: Backend first → Frontend → Integration, following user story priorities.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Exact file paths included in all descriptions

## Path Conventions

- **Backend**: `backend/` (FastAPI + SQLModel)
- **Frontend**: `frontend/` (Next.js App Router)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize monorepo structure and install dependencies
**Complexity**: Low | **Estimated Tasks**: 6

- [x] T001 Create monorepo directory structure with `backend/` and `frontend/` folders
- [x] T002 [P] Initialize backend Python project with `backend/requirements.txt` containing FastAPI, SQLModel, python-jose, passlib, python-dotenv, uvicorn, psycopg2-binary
- [x] T003 [P] Initialize frontend Next.js project in `frontend/` with TypeScript and Tailwind CSS using `npx create-next-app@latest`
- [x] T004 [P] Create `backend/.env.example` with DATABASE_URL and BETTER_AUTH_SECRET placeholders
- [x] T005 [P] Create `frontend/.env.example` with NEXT_PUBLIC_API_URL and BETTER_AUTH_SECRET placeholders
- [x] T006 Create root `.gitignore` with Python venv, node_modules, .env files, __pycache__

**Checkpoint**: Project structure ready, dependencies installable

---

## Phase 2: Foundational (Backend Core Infrastructure)

**Purpose**: Database connection, models, and auth middleware - BLOCKS all user stories
**Complexity**: Medium | **Estimated Tasks**: 12

### Database & Configuration

- [x] T007 Create `backend/config.py` with Settings class loading DATABASE_URL and BETTER_AUTH_SECRET from environment
- [x] T008 Create `backend/database.py` with SQLModel engine setup and get_session dependency for Neon PostgreSQL

### Core Models (Used by ALL stories)

- [x] T009 [P] Create `backend/models/__init__.py` exporting all models
- [x] T010 [P] Create `backend/models/user.py` with User SQLModel (id UUID, email, password_hash, created_at, updated_at)
- [x] T011 [P] Create `backend/models/task.py` with Task SQLModel (id UUID, title, completed, user_id FK, created_at, updated_at)

### Schemas (Request/Response DTOs)

- [x] T012 [P] Create `backend/schemas/__init__.py` exporting all schemas
- [x] T013 [P] Create `backend/schemas/user.py` with UserCreate, UserLogin, UserResponse, AuthResponse
- [x] T014 [P] Create `backend/schemas/task.py` with TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

### Auth Utilities & Middleware

- [x] T015 Create `backend/utils/__init__.py` exporting utilities
- [x] T016 Create `backend/utils/auth.py` with password hashing (bcrypt) and JWT token creation/verification functions
- [x] T017 Create `backend/utils/exceptions.py` with custom HTTPException classes (AuthenticationError, AuthorizationError, NotFoundError)
- [x] T018 Create `backend/middleware/auth.py` with JWT verification dependency that extracts user_id from token and validates against path parameter

**Checkpoint**: Backend foundation ready - can now implement auth and task endpoints

---

## Phase 3: User Story 1 & 2 - Registration & Login (Priority: P1)

**Goal**: Users can create accounts and login to access the application
**Complexity**: Medium | **Estimated Tasks**: 8

**Independent Test**: Navigate to signup, create account, verify redirect to dashboard with JWT token stored

### Backend Auth Routes

- [x] T019 Create `backend/routes/__init__.py` with router exports
- [x] T020 Create `backend/routes/auth.py` with POST /api/auth/signup endpoint (validate email/password, hash password, create user, return JWT)
- [x] T021 [US1][US2] Add POST /api/auth/login endpoint to `backend/routes/auth.py` (verify credentials, return JWT)
- [x] T022 [US1][US2] Add POST /api/auth/logout endpoint to `backend/routes/auth.py` (client-side token removal, return success)

### Backend App Entry Point

- [x] T023 Create `backend/main.py` with FastAPI app, CORS middleware (allow localhost:3000), include auth router, health check endpoint, database table creation on startup

### Backend Verification

- [ ] T024 Manually test auth endpoints using curl or API client: signup creates user, login returns token, invalid credentials return 401

**Checkpoint**: Backend auth fully functional - can register and login via API

---

## Phase 4: User Stories 3 & 4 - Create & View Tasks (Priority: P1)

**Goal**: Authenticated users can create tasks and view their task list
**Complexity**: Medium | **Estimated Tasks**: 6

**Independent Test**: Login, create a task, verify it appears in task list, refresh page to confirm persistence

### Backend Task Routes

- [x] T025 [US3][US4] Create `backend/routes/tasks.py` with GET /api/users/{user_id}/tasks endpoint (verify JWT user matches path, return user's tasks)
- [x] T026 [US3] Add POST /api/users/{user_id}/tasks endpoint to `backend/routes/tasks.py` (create task with user_id from JWT)
- [x] T027 Include tasks router in `backend/main.py`

### Backend Verification

- [ ] T028 Manually test task endpoints: create task with valid JWT, list tasks returns only user's tasks, unauthorized access returns 403

**Checkpoint**: Backend CRUD foundation complete - can create and list tasks via API

---

## Phase 5: User Stories 5 & 6 - Update & Delete Tasks (Priority: P2)

**Goal**: Users can toggle task completion status and delete tasks
**Complexity**: Low | **Estimated Tasks**: 3

**Independent Test**: Create task, toggle status, verify change persists; delete task, verify removal

### Backend Update/Delete Routes

- [x] T029 [US5] Add PATCH /api/users/{user_id}/tasks/{task_id} endpoint to `backend/routes/tasks.py` (update title and/or completed status)
- [x] T030 [US6] Add DELETE /api/users/{user_id}/tasks/{task_id} endpoint to `backend/routes/tasks.py` (verify ownership, delete task)

### Backend Verification

- [ ] T031 Manually test update/delete: toggle completed status, update title, delete task, verify all persist correctly

**Checkpoint**: Backend fully complete - all API endpoints functional

---

## Phase 6: Frontend Foundation

**Purpose**: Setup Next.js with auth context, API client, and shared components
**Complexity**: Medium | **Estimated Tasks**: 12

### TypeScript Types & API Client

- [x] T032 Create `frontend/lib/types.ts` with User, Task, AuthResponse, TaskListResponse, ErrorResponse interfaces
- [x] T033 Create `frontend/lib/api.ts` with API client class: base fetch wrapper, auth header injection, error handling, methods for all endpoints

### Auth Context & Hooks

- [x] T034 Create `frontend/lib/auth.ts` with AuthContext, AuthProvider, token storage (localStorage), login/logout/signup functions
- [x] T035 Create `frontend/hooks/useAuth.ts` with useAuth hook returning user, isAuthenticated, isLoading, login, logout, signup
- [x] T036 Create `frontend/middleware.ts` with Next.js middleware for protected route redirection (redirect /dashboard to /login if no token)

### Shared UI Components

- [x] T037 [P] Create `frontend/components/ui/Button.tsx` with primary/secondary/danger variants, loading state, Tailwind styling
- [x] T038 [P] Create `frontend/components/ui/Input.tsx` with label, error message, Tailwind styling
- [x] T039 [P] Create `frontend/components/ui/Card.tsx` with container styling for forms and content sections

### App Layout

- [x] T040 Update `frontend/app/layout.tsx` with AuthProvider wrapper, global styles import, metadata
- [x] T041 Update `frontend/app/globals.css` with Tailwind directives and any custom utility classes
- [x] T042 Update `frontend/app/page.tsx` with redirect logic (to /dashboard if authenticated, /login if not)
- [x] T043 Configure `frontend/tailwind.config.js` with content paths and any custom theme extensions

**Checkpoint**: Frontend foundation ready - auth context and API client functional

---

## Phase 7: Frontend Auth Pages (US1 & US2)

**Goal**: Complete signup and login user flows
**Complexity**: Medium | **Estimated Tasks**: 6

**Independent Test**: Visit /signup, create account, verify redirect to dashboard; visit /login, authenticate, verify redirect

### Auth Components

- [x] T044 [P] [US1] Create `frontend/components/auth/SignupForm.tsx` with email/password inputs, validation, submit handler, error display
- [x] T045 [P] [US2] Create `frontend/components/auth/LoginForm.tsx` with email/password inputs, submit handler, error display, link to signup

### Auth Pages

- [x] T046 [US1] Create `frontend/app/signup/page.tsx` with SignupForm, redirect on success, link to login
- [x] T047 [US2] Create `frontend/app/login/page.tsx` with LoginForm, redirect on success, link to signup

### Frontend Auth Verification

- [x] T048 Test signup flow end-to-end: form validation, API call, token storage, redirect
- [x] T049 Test login flow end-to-end: form validation, API call, token storage, redirect

**Checkpoint**: Authentication flows complete - users can register and login

---

## Phase 8: Frontend Task Dashboard (US3, US4, US5, US6)

**Goal**: Complete task management UI with create, view, update, delete
**Complexity**: Medium | **Estimated Tasks**: 10

**Independent Test**: Login, see task list (or empty state), add task, toggle completion, delete task

### Task Hooks

- [x] T050 Create `frontend/hooks/useTasks.ts` with useTasks hook: fetch tasks, create task, update task, delete task, loading/error states

### Task Components

- [x] T051 [P] [US4] Create `frontend/components/tasks/EmptyState.tsx` with encouraging message to create first task
- [x] T052 [P] [US3] Create `frontend/components/tasks/AddTaskForm.tsx` with title input, submit button, validation
- [x] T053 [US4][US5][US6] Create `frontend/components/tasks/TaskItem.tsx` with checkbox toggle, title display, delete button, optimistic updates
- [x] T054 [US4] Create `frontend/components/tasks/TaskList.tsx` with task mapping, empty state handling, loading skeleton

### Dashboard Page

- [x] T055 [US3][US4][US5][US6] Create `frontend/app/dashboard/page.tsx` with protected route, task list, add task form, logout button

### Frontend Task Verification

- [x] T056 [US3] Test create task: enter title, submit, verify appears in list
- [x] T057 [US4] Test view tasks: verify all user tasks display with correct status
- [x] T058 [US5] Test toggle status: click checkbox, verify visual update and persistence
- [x] T059 [US6] Test delete task: click delete, verify removal from list

**Checkpoint**: Task management complete - full CRUD working in UI

---

## Phase 9: User Story 7 - Logout (Priority: P3)

**Goal**: Users can securely end their session
**Complexity**: Low | **Estimated Tasks**: 2

**Independent Test**: While logged in, click logout, verify redirect to login, verify cannot access dashboard

### Logout Implementation

- [x] T060 [US7] Add logout button to `frontend/app/dashboard/page.tsx` header with click handler calling auth context logout
- [x] T061 [US7] Test logout flow: click logout, verify token cleared, redirect to login, cannot access /dashboard

**Checkpoint**: Authentication cycle complete - register, login, use app, logout

---

## Phase 10: Polish & Error Handling

**Purpose**: Production-ready refinements and edge cases
**Complexity**: Low | **Estimated Tasks**: 8

### Error Handling & UX

- [x] T062 [P] Add loading spinners to `frontend/components/auth/LoginForm.tsx` and `frontend/components/auth/SignupForm.tsx` during API calls
- [x] T063 [P] Add error toast/alert component to `frontend/components/ui/Toast.tsx` for API error display
- [x] T064 Implement JWT expiry handling in `frontend/lib/api.ts`: detect 401, clear token, redirect to login
- [x] T065 Add API error transformation in `frontend/lib/api.ts` to show user-friendly messages

### Responsive Design

- [x] T066 [P] Ensure all pages are responsive (320px-1920px) - verify `frontend/app/dashboard/page.tsx`, login, signup
- [x] T067 [P] Add mobile-friendly navigation/header to dashboard

### Final Verification

- [x] T068 Full end-to-end test: signup → create tasks → toggle → delete → logout → login → verify tasks persist
- [ ] T069 Cross-browser testing: Chrome, Firefox, Safari (if available)

**Checkpoint**: Application production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────────────────────┐
     │                                                                    │
     ▼                                                                    │
Phase 2 (Foundational) ──────────────────────────────────────────────────┤
     │                                                                    │
     ├──────────────────┬──────────────────┐                             │
     ▼                  ▼                  ▼                             │
Phase 3 (Auth)    Phase 4 (Tasks)    Phase 5 (Update/Delete)            │
     │                  │                  │                             │
     └──────────────────┴──────────────────┘                             │
                        │                                                 │
                        ▼                                                 │
                  Phase 6 (Frontend Foundation)                          │
                        │                                                 │
                        ▼                                                 │
                  Phase 7 (Frontend Auth)                                │
                        │                                                 │
                        ▼                                                 │
                  Phase 8 (Frontend Dashboard)                           │
                        │                                                 │
                        ▼                                                 │
                  Phase 9 (Logout)                                       │
                        │                                                 │
                        ▼                                                 │
                  Phase 10 (Polish) ◄────────────────────────────────────┘
```

### Critical Path

1. **T001-T006**: Setup (parallel where marked)
2. **T007-T018**: Backend foundation (blocks everything)
3. **T019-T031**: Backend API complete (enables frontend)
4. **T032-T043**: Frontend foundation
5. **T044-T069**: Frontend features + polish

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002, T003, T004, T005 can all run in parallel
```

**Phase 2 (Foundational)**:
```
T009, T010, T011 (models) can run in parallel
T012, T013, T014 (schemas) can run in parallel
```

**Phase 6 (Frontend Foundation)**:
```
T037, T038, T039 (UI components) can run in parallel
```

**Phase 7 (Frontend Auth)**:
```
T044, T045 (auth components) can run in parallel
```

**Phase 8 (Frontend Dashboard)**:
```
T051, T052 (task components) can run in parallel
```

---

## Task Summary

| Phase | Description | Task Count | Complexity |
|-------|-------------|------------|------------|
| 1 | Setup | 6 | Low |
| 2 | Foundational | 12 | Medium |
| 3 | Auth Backend (US1, US2) | 6 | Medium |
| 4 | Tasks Backend (US3, US4) | 4 | Medium |
| 5 | Update/Delete Backend (US5, US6) | 3 | Low |
| 6 | Frontend Foundation | 12 | Medium |
| 7 | Frontend Auth (US1, US2) | 6 | Medium |
| 8 | Frontend Dashboard (US3-US6) | 10 | Medium |
| 9 | Logout (US7) | 2 | Low |
| 10 | Polish | 8 | Low |
| **Total** | | **69** | |

### Tasks by User Story

| User Story | Backend Tasks | Frontend Tasks | Total |
|------------|---------------|----------------|-------|
| US1 (Registration) | T020, T023 | T044, T046, T048 | 5 |
| US2 (Login) | T021, T022 | T045, T047, T049 | 5 |
| US3 (Create Task) | T026 | T052, T055, T056 | 4 |
| US4 (View Tasks) | T025 | T051, T053, T054, T055, T057 | 6 |
| US5 (Update Task) | T029 | T053, T055, T058 | 4 |
| US6 (Delete Task) | T030 | T053, T055, T059 | 4 |
| US7 (Logout) | T022 | T060, T061 | 3 |

---

## Implementation Strategy

### MVP First (Recommended)

1. Complete Phases 1-4 (Setup + Backend Auth + Backend Tasks)
2. Complete Phase 6-7 (Frontend Foundation + Auth)
3. **STOP**: You now have a working signup/login
4. Complete Phase 8 (Dashboard with tasks)
5. **STOP**: You now have full task CRUD
6. Add Phase 9-10 (Logout + Polish)

### Suggested Execution Order

```bash
# Day 1: Backend Complete
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

# Day 2: Frontend Complete
Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10
```

---

## Notes

- All backend tasks should be tested via API client before moving to frontend
- Frontend tasks assume backend is running at http://localhost:8000
- Use `uvicorn main:app --reload` for backend dev server
- Use `npm run dev` for frontend dev server
- Commit after each phase completion
- Each phase has a checkpoint for validation
