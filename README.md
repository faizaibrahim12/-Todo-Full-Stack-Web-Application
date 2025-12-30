# Todo App - Full Stack Application

A modern, full-stack todo application with user authentication, built with Next.js 15+ and FastAPI.

## Features

- User registration and authentication with JWT tokens
- Personal task management (Create, Read, Update, Delete)
- Task completion tracking
- Responsive design for mobile and desktop
- Secure API with user data isolation
- Real-time updates with optimistic UI

## Tech Stack

### Frontend
- **Framework**: Next.js 15+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Auth**: Custom JWT implementation with localStorage
- **State Management**: React Context API + Custom Hooks

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL (Serverless)
- **Auth**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib

## Project Structure

```
Hackathon-Phase2/
├── backend/               # FastAPI backend
│   ├── main.py           # Application entry point
│   ├── config.py         # Environment configuration
│   ├── database.py       # Database connection
│   ├── models/           # SQLModel definitions
│   ├── schemas/          # Pydantic schemas
│   ├── routes/           # API endpoints
│   ├── middleware/       # JWT auth middleware
│   ├── utils/            # Helper functions
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # Next.js frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   ├── hooks/            # Custom React hooks
│   └── package.json      # Node dependencies
│
└── specs/                # Design documentation
    └── 001-frontend-todo/
        ├── spec.md       # Feature specification
        ├── plan.md       # Architecture plan
        ├── tasks.md      # Implementation tasks
        └── contracts/    # API contracts
```

## Prerequisites

- **Node.js** 18+ (for Next.js frontend)
- **Python** 3.11+ (for FastAPI backend)
- **Neon PostgreSQL** account (free tier available at https://neon.tech)
- **Git** (for version control)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Hackathon-Phase2
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install fastapi uvicorn sqlmodel psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-dotenv
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create `backend/.env` file:

```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-32-character-or-longer-secret-key-here
```

**Important**: Generate a secure secret key:

```bash
# Using OpenSSL
openssl rand -base64 32

# Or using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Start Backend Server

```bash
uvicorn main:app --reload --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Frontend Setup

#### Navigate to Frontend Directory

```bash
cd ../frontend  # From backend directory
# Or
cd frontend     # From project root
```

#### Install Dependencies

```bash
npm install
```

#### Configure Environment Variables

Create `frontend/.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-32-character-or-longer-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**Important**: Use the SAME secret key as the backend!

#### Start Development Server

```bash
npm run dev
```

The frontend will be available at: http://localhost:3000

## Running Both Services

### Option 1: Two Terminal Windows

**Terminal 1 (Backend)**:
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

### Option 2: Using npm concurrently (Recommended)

From the project root, you can set up a script to run both:

```json
// package.json (create in root)
{
  "scripts": {
    "dev:backend": "cd backend && uvicorn main:app --reload --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\""
  },
  "devDependencies": {
    "concurrently": "^8.0.0"
  }
}
```

Then run:
```bash
npm install
npm run dev
```

## Using the Application

### 1. Create an Account

1. Navigate to http://localhost:3000
2. You'll be redirected to the login page
3. Click "Sign up" link
4. Enter email and password (minimum 8 characters)
5. Click "Sign Up" button
6. You'll be automatically logged in and redirected to the dashboard

### 2. Manage Tasks

- **Add Task**: Type in the input field at the top and click "Add Task"
- **Complete Task**: Click the checkbox next to a task
- **Delete Task**: Click the trash icon on the right side of a task
- **View Tasks**: All your tasks are displayed in the main area

### 3. Logout

- Click the "Log Out" button in the top right corner
- You'll be redirected to the login page
- Your tasks will persist and be available when you log back in

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - End session

### Tasks (Protected - Requires JWT)

- `GET /api/users/{user_id}/tasks` - List user's tasks
- `POST /api/users/{user_id}/tasks` - Create new task
- `PATCH /api/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/users/{user_id}/tasks/{task_id}` - Delete task

## Testing

### Manual Testing Flow

1. **Signup Flow**:
   - Create account with valid email/password
   - Verify automatic login and redirect to dashboard

2. **Task Management**:
   - Create a task
   - Toggle task completion
   - Delete a task
   - Verify all operations persist

3. **Logout and Login**:
   - Logout from dashboard
   - Login with same credentials
   - Verify tasks are still present

4. **Error Handling**:
   - Try signup with invalid email
   - Try login with wrong password
   - Verify error messages display correctly

### API Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login (save the token from response)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Get tasks (replace TOKEN and USER_ID)
curl http://localhost:8000/api/users/{USER_ID}/tasks \
  -H "Authorization: Bearer {TOKEN}"
```

## Troubleshooting

### CORS Errors

Ensure backend has CORS middleware configured for http://localhost:3000

### JWT Verification Fails

- Verify `BETTER_AUTH_SECRET` is identical in both `.env` files
- Check token hasn't expired
- Ensure Authorization header format is `Bearer <token>`

### Database Connection Fails

- Verify DATABASE_URL includes `?sslmode=require` for Neon
- Check Neon dashboard for connection limits
- Ensure IP is allowed in Neon project settings

### Port Already in Use

```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Module Not Found Errors

**Backend**:
```bash
pip install -r backend/requirements.txt
```

**Frontend**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Development Tips

1. **Hot Reload**: Both servers support hot reload - changes are reflected automatically
2. **API Documentation**: Visit http://localhost:8000/docs for interactive API docs
3. **Browser DevTools**: Use React DevTools and Network tab for debugging
4. **Database**: View data directly in Neon dashboard

## Production Deployment

### Backend (FastAPI)

Deploy to:
- **Railway**: Connect GitHub repo, set environment variables
- **Render**: Deploy as web service
- **Vercel**: Use Python runtime

### Frontend (Next.js)

Deploy to:
- **Vercel**: `vercel deploy` (recommended)
- **Netlify**: Connect GitHub repo
- **Railway**: Deploy as web service

### Environment Variables for Production

Update URLs in production:
- `NEXT_PUBLIC_API_URL`: Your production backend URL
- `BETTER_AUTH_URL`: Your production frontend URL
- `DATABASE_URL`: Your production database URL

## Security Considerations

- JWT tokens stored in localStorage (consider httpOnly cookies for production)
- All passwords hashed with bcrypt
- User data isolation enforced at database level
- Input validation on both frontend and backend
- CORS restricted to frontend origin

## License

MIT

## Support

For issues or questions, please open an issue in the GitHub repository.
#   - T o d o - F u l l - S t a c k - W e b - A p p l i c a t i o n  
 