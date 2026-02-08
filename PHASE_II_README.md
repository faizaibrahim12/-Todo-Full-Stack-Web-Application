# Phase II - Full-Stack Todo Web Application

**Status**: ✅ Specification Complete - Ready for Implementation
**Created**: 2025-01-07
**Lead Document**: This file

---

## Quick Links

| Document | Purpose | Best For |
|----------|---------|----------|
| **[PHASE_II_SUMMARY.md](./PHASE_II_SUMMARY.md)** | Executive summary of entire Phase II | Project overview, tech stack decisions |
| **[IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)** | Visual task dependencies & timeline | Planning your execution, parallelization |
| **[specs/phase-ii-web-app/spec.md](./specs/phase-ii-web-app/spec.md)** | Complete feature specification | Understanding requirements & acceptance criteria |
| **[specs/phase-ii-web-app/plan.md](./specs/phase-ii-web-app/plan.md)** | Architecture & design plan | System design, module breakdown |
| **[specs/phase-ii-web-app/tasks.md](./specs/phase-ii-web-app/tasks.md)** | 30 actionable implementation tasks | Day-to-day development |

---

## Phase II at a Glance

### What is Phase II?

Transformation of the Phase I console app into a production-ready web application:

**Phase I** (Completed):
- CLI REPL interface
- In-memory task storage
- Single-user, local only
- Pure Python (stdlib only)

**Phase II** (New):
- Web interface (Next.js + React)
- Persistent database (PostgreSQL)
- Multi-user with authentication (JWT + bcrypt)
- Professional backend API (FastAPI)
- Responsive UI with dark mode
- Production-ready security

### Architecture Overview

```
┌─────────────────────────────────────┐
│       Frontend (Next.js 14)          │
│  React, TypeScript, TailwindCSS      │
│  Better Auth, React Query, Zod       │
└────────────┬────────────────────────┘
             │ HTTPS/REST JSON
             ▼
┌─────────────────────────────────────┐
│       Backend (FastAPI)              │
│  Python, SQLModel, python-jose       │
│  Middleware: JWT, CORS, Rate Limit   │
└────────────┬────────────────────────┘
             │ psycopg2
             ▼
┌─────────────────────────────────────┐
│    Database (PostgreSQL 13+)         │
│  users table, tasks table            │
│  Migrations: Alembic                 │
└─────────────────────────────────────┘
```

### Key Features

✅ **Authentication**
- Email/password registration
- Secure login with JWT tokens
- HttpOnly cookies (XSS protection)
- Bcrypt password hashing

✅ **Task Management**
- Create, read, update, delete tasks
- Mark tasks complete/incomplete
- Filter by status (pending/completed)
- Sort by created date or title
- Due dates for planning

✅ **User Interface**
- Responsive design (mobile/tablet/desktop)
- Light & dark mode
- Real-time task updates
- Error notifications
- Loading states & optimistic updates

✅ **Data Persistence**
- PostgreSQL database
- Alembic migrations
- User ownership enforcement
- Task data survives sessions

---

## What You'll Learn

Implementing Phase II covers:

### Backend
- FastAPI application structure
- SQLModel ORM (combining SQLAlchemy + Pydantic)
- JWT authentication & token management
- Password hashing with bcrypt
- Database migrations with Alembic
- REST API design patterns
- Middleware & dependency injection

### Frontend
- Next.js 14 App Router
- React hooks & component composition
- Server-side state management with React Query
- Client-side form validation with Zod
- Authentication flow implementation
- Dark mode with localStorage
- Error handling & user notifications

### Full-Stack
- Multi-tier architecture
- CORS & security best practices
- Database design for user isolation
- End-to-end testing
- Deployment readiness

---

## Getting Started

### Step 1: Read the Specifications

Start with **PHASE_II_SUMMARY.md** (10 min read):
- Overview of what you're building
- Technology rationale
- Success criteria

Then dive into spec.md (30 min):
- User stories and acceptance criteria
- Requirements breakdown
- Data models

### Step 2: Review the Architecture

Read **plan.md** (20 min):
- 3-tier architecture
- Module breakdown
- Implementation phases
- Authentication flow

### Step 3: Understand Your Tasks

Check **IMPLEMENTATION_ROADMAP.md** (15 min):
- Dependency graph
- Duration estimates
- Parallelization opportunities
- Choose your execution strategy

### Step 4: Start Implementing

Open **tasks.md** and begin with Task T001:
- Each task has clear steps
- File paths provided
- Expected outcomes documented
- Dependencies mapped

---

## Implementation Phases

### Phase P1: Foundation (2-3 hours)
Backend project structure, database setup, SQLModel entities, migrations

**Outcome**: Database ready, can connect from code

### Phase P2: Authentication (4-5 hours)
JWT utilities, password hashing, registration/login endpoints, auth middleware

**Outcome**: Users can register and login, tokens issued

### Phase P3: Task API (3-4 hours)
Task CRUD endpoints, filtering, sorting, user ownership validation

**Outcome**: Full REST API for task management

### Phase P4: Frontend Setup (2-3 hours)
Next.js project, routing structure, Better Auth integration, API client

**Outcome**: Frontend skeleton with auth flow

### Phase P5: Frontend UI (5-6 hours)
Auth forms, task list, CRUD components, filters, dark mode

**Outcome**: Fully functional web interface

### Phase P6: Polish (4-5 hours)
Notifications, error handling, rate limiting, validation, testing

**Outcome**: Production-ready application

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.10+ |
| **Backend Framework** | FastAPI | 0.104+ |
| **Backend ORM** | SQLModel | 0.0.14+ |
| **Database** | PostgreSQL | 13+ |
| **Auth Hashing** | passlib + bcrypt | Latest |
| **Auth Tokens** | python-jose + cryptography | Latest |
| **Frontend Framework** | Next.js | 14+ |
| **Frontend Language** | TypeScript | Latest |
| **UI Library** | React | 18+ |
| **UI Styling** | TailwindCSS | 3+ |
| **Frontend Auth** | Better Auth | 0.5+ |
| **State Management** | React Query | 5+ |
| **Validation** | Zod | 3.22+ |
| **Database Migrations** | Alembic | 1.12+ |

---

## Success Criteria

### Backend ✓
- [ ] FastAPI server runs on localhost:5000
- [ ] PostgreSQL database connected
- [ ] Migrations applied successfully
- [ ] `/api/auth/register` endpoint works
- [ ] `/api/auth/login` endpoint works & returns JWT
- [ ] Task CRUD endpoints work
- [ ] User ownership enforced (can't see other users' tasks)
- [ ] Swagger docs available at `/docs`

### Frontend ✓
- [ ] Next.js server runs on localhost:3000
- [ ] Login page loads at `/auth/login`
- [ ] Register page loads at `/auth/register`
- [ ] Can register new account
- [ ] Can login with credentials
- [ ] Can view task list on dashboard
- [ ] Can create new task
- [ ] Can edit existing task
- [ ] Can delete task
- [ ] Can toggle task completion
- [ ] Can filter by status (all/pending/completed)
- [ ] Can sort by created date or title
- [ ] Can toggle dark mode
- [ ] Responsive on mobile/tablet/desktop

### Integration ✓
- [ ] Frontend ↔ Backend communication works
- [ ] JWT authentication enforced
- [ ] Tasks persist in database
- [ ] User data isolation enforced
- [ ] Error messages clear and actionable
- [ ] Notifications show on success/error
- [ ] Performance acceptable (< 1s page loads)

---

## Development Environment Setup

### Prerequisites
```bash
# Python 3.10+
python --version

# Node.js 18+
node --version
npm --version

# PostgreSQL 13+
psql --version
```

### Quick Start

1. **Clone the repo**
```bash
cd in_memory_console_app
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Database Setup**
```bash
# Create PostgreSQL database
createdb todo_db

# Or use Docker
docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres
```

5. **Run Development Servers**
```bash
# Terminal 1: Backend
cd backend
fastapi run src/main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit: `http://localhost:3000`

---

## Project Structure

```
in_memory_console_app/
├── backend/                          # FastAPI backend
│   ├── src/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings & environment
│   │   ├── database.py              # SQLAlchemy setup
│   │   ├── auth/                    # Authentication module
│   │   │   ├── models.py            # User model
│   │   │   ├── schemas.py           # Request/response schemas
│   │   │   ├── service.py           # Business logic
│   │   │   ├── routes.py            # API endpoints
│   │   │   └── jwt.py               # Token utilities
│   │   ├── tasks/                   # Task management module
│   │   │   ├── models.py            # Task model
│   │   │   ├── schemas.py           # Validation schemas
│   │   │   ├── service.py           # Business logic
│   │   │   └── routes.py            # API endpoints
│   │   ├── middleware/              # Middleware
│   │   │   ├── auth.py              # JWT verification
│   │   │   └── rate_limit.py        # Rate limiting
│   │   └── exceptions.py            # Custom exceptions
│   ├── alembic/                     # Database migrations
│   │   ├── versions/                # Migration files
│   │   ├── env.py                   # Migration environment
│   │   └── script.py.mako
│   ├── tests/                       # Backend tests
│   ├── pyproject.toml               # Dependencies
│   ├── .env.example                 # Environment template
│   └── README.md                    # Backend docs
│
├── frontend/                         # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home page (redirect)
│   │   ├── auth/
│   │   │   ├── login/page.tsx       # Login page
│   │   │   └── register/page.tsx    # Register page
│   │   ├── dashboard/
│   │   │   ├── page.tsx             # Task list
│   │   │   └── settings/page.tsx    # Settings (future)
│   │   └── api/
│   │       └── auth/[auth]/route.ts # Better Auth handler
│   ├── components/
│   │   ├── AuthForm.tsx             # Login/Register form
│   │   ├── TaskForm.tsx             # Create/Edit task
│   │   ├── TaskList.tsx             # Task list display
│   │   ├── TaskItem.tsx             # Single task
│   │   ├── TaskFilters.tsx          # Status/sort controls
│   │   ├── ThemeToggle.tsx          # Light/dark mode
│   │   ├── ToastContainer.tsx       # Notifications
│   │   ├── Providers.tsx            # Provider setup
│   │   └── ... other components
│   ├── lib/
│   │   ├── api-client.ts            # Fetch wrapper
│   │   ├── auth-client.ts           # Better Auth client
│   │   ├── types.ts                 # TypeScript types
│   │   ├── hooks.ts                 # Custom hooks
│   │   ├── theme-context.tsx        # Dark mode logic
│   │   └── toast-context.tsx        # Notifications
│   ├── middleware.ts                # Next.js middleware
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── .env.local.example           # Environment template
│   └── README.md                    # Frontend docs
│
├── specs/
│   ├── todo-console/                # Phase I specs
│   │   ├── spec.md
│   │   ├── plan.md
│   │   └── tasks.md
│   └── phase-ii-web-app/            # Phase II specs
│       ├── spec.md                  # Feature specification
│       ├── plan.md                  # Architecture plan
│       └── tasks.md                 # 30 implementation tasks
│
├── docs/                            # Additional documentation
│   ├── ARCHITECTURE.md              # Design decisions
│   ├── API.md                       # API reference
│   └── DEPLOYMENT.md                # Production setup
│
├── PHASE_II_SUMMARY.md              # Executive summary
├── PHASE_II_README.md               # This file
├── IMPLEMENTATION_ROADMAP.md        # Task timeline & dependencies
├── README.md                        # Project overview
└── CLAUDE.md                        # Development guidelines
```

---

## Common Commands

### Backend
```bash
# Install dependencies
cd backend && pip install -e .

# Run development server
fastapi run src/main.py  # or: uvicorn src.main:app --reload

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# View API documentation
# Open: http://localhost:8000/docs

# Run tests (if added)
pytest tests/
```

### Frontend
```bash
# Install dependencies
cd frontend && npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Run type checking
tsc --noEmit

# Format code
npm run format
```

---

## Troubleshooting

### Database Connection Error
**Problem**: `could not connect to server: Connection refused`
**Solution**:
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Use Docker: `docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres`

### CORS Errors in Browser
**Problem**: `Cross-Origin Request Blocked`
**Solution**:
- Check `NEXT_PUBLIC_API_URL` matches backend URL
- Verify `CORSMiddleware` allows frontend origin
- Check credentials are being sent: `credentials: "include"`

### JWT Token Not Persisting
**Problem**: Get logged out after page refresh
**Solution**:
- Check httpOnly cookie is being set in login response
- Verify `secure=False` in development (http), `secure=True` in production (https)
- Check cookie sameSite policy

### Task Not Appearing After Creation
**Problem**: Create task but doesn't show in list
**Solution**:
- Check React Query is invalidating cache after mutation
- Verify task ownership is correct (user_id matches)
- Check API response includes task with correct user_id

### Styling Not Applying
**Problem**: TailwindCSS classes not working in dark mode
**Solution**:
- Verify `darkMode: 'class'` in tailwind.config.js
- Check dark: prefix is being used correctly
- Clear Next.js cache: `rm -rf .next && npm run dev`

---

## Next Steps

1. **Choose your role**:
   - Backend developer? Start with Phase P1 in tasks.md
   - Frontend developer? Start with Phase P4 in tasks.md
   - Full-stack? Start with Phase P1 sequentially

2. **Set up your environment** (see above)

3. **Read the detailed specs** in order: spec.md → plan.md → tasks.md

4. **Track your progress** using IMPLEMENTATION_ROADMAP.md

5. **Implement tasks** one at a time, referencing tasks.md for details

6. **Test after each phase** to catch issues early

7. **Deploy when complete** (deployment guide in docs/)

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **React Query Docs**: https://tanstack.com/query/latest
- **TailwindCSS Docs**: https://tailwindcss.com/docs
- **Better Auth Docs**: https://www.better-auth.com

---

## Questions?

- **"What should I build?"** → See `IMPLEMENTATION_ROADMAP.md`
- **"How should I build it?"** → See `specs/phase-ii-web-app/plan.md`
- **"What are the requirements?"** → See `specs/phase-ii-web-app/spec.md`
- **"What's the detailed task?"** → See `specs/phase-ii-web-app/tasks.md`
- **"What's the technology stack?"** → See `PHASE_II_SUMMARY.md`

---

## Status

✅ **Phase II Specification**: COMPLETE
⏳ **Phase II Implementation**: READY TO START

Total effort: **20-26 hours** (full stack)
Recommended: **2-3 days** with dedicated focus

Start with **Task T001** in `specs/phase-ii-web-app/tasks.md`

---

**Created**: 2025-01-07
**By**: Claude Code (AI-assisted development)
**For**: In-Memory Console App Phase II

