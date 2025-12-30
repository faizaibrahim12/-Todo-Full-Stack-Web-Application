# Todo App Backend

FastAPI backend with SQLModel, Neon PostgreSQL, and JWT authentication.

## Setup

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
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT (generate with `openssl rand -base64 32`)

### 4. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

Server runs at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout

### Tasks (Requires JWT)
- `GET /api/users/{user_id}/tasks` - List user's tasks
- `POST /api/users/{user_id}/tasks` - Create task
- `PATCH /api/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/users/{user_id}/tasks/{task_id}` - Delete task

### Health
- `GET /health` - Health check
- `GET /` - API info

## Testing with cURL

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Create Task (use token from login)
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Buy groceries"}'
```

### List Tasks
```bash
curl http://localhost:8000/api/users/{user_id}/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Settings and environment configuration
├── database.py          # Database connection and session management
├── models/              # SQLModel database models
│   ├── user.py          # User model
│   └── task.py          # Task model (with user_id FK)
├── schemas/             # Pydantic request/response schemas
│   ├── user.py          # User DTOs
│   └── task.py          # Task DTOs
├── routes/              # API endpoints
│   ├── auth.py          # Authentication routes
│   └── tasks.py         # Task CRUD routes
├── middleware/          # Request middleware
│   └── auth.py          # JWT verification
└── utils/               # Utility functions
    ├── auth.py          # Password hashing, JWT functions
    └── exceptions.py    # Custom HTTP exceptions
```

## Key Features

- **JWT Authentication**: Secure token-based auth with Better Auth secret
- **User Isolation**: All queries filter by user_id from JWT
- **Password Security**: Bcrypt hashing with passlib
- **CORS**: Configured for localhost:3000 (frontend)
- **Auto DB Creation**: Tables created automatically on startup
- **Validation**: Pydantic schemas validate all inputs
- **Error Handling**: Custom exceptions for auth, authorization, not found

## Database Schema

### users
- id (UUID, PK)
- email (VARCHAR, UNIQUE, INDEXED)
- password_hash (VARCHAR)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### tasks
- id (UUID, PK)
- title (VARCHAR 500)
- completed (BOOLEAN, default FALSE)
- user_id (UUID, FK → users.id, INDEXED)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
