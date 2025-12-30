# Quickstart Guide: Frontend Todo App

**Feature**: 001-frontend-todo
**Date**: 2025-12-27

## Prerequisites

- Node.js 18+ (for Next.js)
- Python 3.11+ (for FastAPI)
- Neon PostgreSQL account (free tier available)
- Git

## Environment Setup

### 1. Clone and Navigate

```bash
cd Hackathon-Phase2
```

### 2. Create Environment Files

**Backend (`backend/.env`)**:
```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-32-character-or-longer-secret-key-here
```

**Frontend (`frontend/.env.local`)**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-32-character-or-longer-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

> **Important**: `BETTER_AUTH_SECRET` must be identical in both files!

### 3. Generate a Secret

```bash
# Using OpenSSL
openssl rand -base64 32

# Or using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn sqlmodel psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-dotenv
```

### 3. Initialize Database

The database tables will be created automatically on first run via SQLModel.

### 4. Start Backend Server

```bash
uvicorn main:app --reload --port 8000
```

Server runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

App runs at: http://localhost:3000

## Verify Setup

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. Test Authentication Flow

```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 3. Open Frontend

Navigate to http://localhost:3000 in your browser.

## Project Structure

```
Hackathon-Phase2/
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── models.py            # SQLModel definitions
│   ├── auth.py              # JWT auth utilities
│   ├── routes/
│   │   ├── auth.py          # Auth endpoints
│   │   └── tasks.py         # Task CRUD endpoints
│   └── .env                 # Backend environment
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home/redirect
│   │   ├── login/
│   │   │   └── page.tsx     # Login page
│   │   ├── signup/
│   │   │   └── page.tsx     # Signup page
│   │   └── dashboard/
│   │       └── page.tsx     # Task dashboard
│   ├── components/
│   │   ├── TaskList.tsx     # Task list component
│   │   ├── TaskItem.tsx     # Individual task
│   │   └── AddTask.tsx      # New task form
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   └── auth.ts          # Auth utilities
│   └── .env.local           # Frontend environment
│
├── specs/
│   └── 001-frontend-todo/   # This feature's specs
│
└── .env.example             # Template for env vars
```

## Common Issues

### CORS Errors

Ensure backend has CORS middleware configured:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### JWT Verification Fails

- Verify `BETTER_AUTH_SECRET` is identical in both .env files
- Check token hasn't expired (default: 7 days)
- Ensure Authorization header format: `Bearer <token>`

### Database Connection Fails

- Verify DATABASE_URL format includes `?sslmode=require` for Neon
- Check Neon dashboard for connection limits
- Ensure IP is allowed in Neon project settings

### Port Already in Use

```bash
# Find and kill process on port 8000 (backend)
lsof -i :8000
kill -9 <PID>

# Find and kill process on port 3000 (frontend)
lsof -i :3000
kill -9 <PID>
```

## Development Workflow

1. **Start backend first** (database must be available)
2. **Start frontend** (connects to backend API)
3. **Make changes** - both servers hot-reload
4. **Test in browser** at http://localhost:3000

## Next Steps

After setup, proceed to implementation:
1. Run `/sp.tasks` to generate implementation tasks
2. Follow task order for proper dependency handling
3. Test each feature as you build
