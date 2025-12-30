# Data Model: Frontend Todo App

**Feature**: 001-frontend-todo
**Date**: 2025-12-27
**Database**: Neon PostgreSQL (Serverless)
**ORM**: SQLModel

## Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│       users         │       │       tasks         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK, UUID)       │──┐    │ id (PK, UUID)       │
│ email (UNIQUE)      │  │    │ title (VARCHAR 500) │
│ password_hash       │  │    │ completed (BOOLEAN) │
│ created_at          │  └───<│ user_id (FK, UUID)  │
│ updated_at          │       │ created_at          │
└─────────────────────┘       │ updated_at          │
                              └─────────────────────┘
```

## Entities

### User

Represents a registered user who owns tasks.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, indexed | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| created_at | TIMESTAMP | NOT NULL, default NOW() | Account creation time |
| updated_at | TIMESTAMP | NOT NULL, auto-update | Last modification time |

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email must be unique (case-insensitive)
- Password minimum 8 characters before hashing

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task

Represents a to-do item owned by a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| title | VARCHAR(500) | NOT NULL | Task description |
| completed | BOOLEAN | NOT NULL, default FALSE | Completion status |
| user_id | UUID | FK → users.id, indexed, NOT NULL | Owner reference |
| created_at | TIMESTAMP | NOT NULL, default NOW() | Task creation time |
| updated_at | TIMESTAMP | NOT NULL, auto-update | Last modification time |

**Validation Rules**:
- Title required, 1-500 characters
- Title cannot be empty or whitespace only
- user_id must reference existing user

**SQLModel Definition**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=500)
    completed: bool = Field(default=False)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Tasks | One-to-Many | A user owns zero or more tasks |
| Task → User | Many-to-One | Each task belongs to exactly one user |

**Cascade Behavior**:
- DELETE user → DELETE all user's tasks (CASCADE)
- UPDATE user.id → UPDATE tasks.user_id (CASCADE)

## Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| users | users_email_idx | email | Fast email lookup during login |
| tasks | tasks_user_id_idx | user_id | Fast task retrieval by user |

## State Transitions

### Task Status

```
[Created] ──── completed=false ───→ [Pending]
                                        │
                                        ↓ toggle
                                   [Completed]
                                        │
                                        ↓ toggle
                                    [Pending]
```

## Data Transfer Objects (DTOs)

### Request DTOs

```python
# User Registration
class UserCreate(SQLModel):
    email: str
    password: str  # Plain text, will be hashed

# User Login
class UserLogin(SQLModel):
    email: str
    password: str

# Task Creation
class TaskCreate(SQLModel):
    title: str

# Task Update
class TaskUpdate(SQLModel):
    title: str | None = None
    completed: bool | None = None
```

### Response DTOs

```python
# User Response (no password)
class UserResponse(SQLModel):
    id: UUID
    email: str
    created_at: datetime

# Task Response
class TaskResponse(SQLModel):
    id: UUID
    title: str
    completed: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

# Auth Response
class AuthResponse(SQLModel):
    user: UserResponse
    token: str

# Task List Response
class TaskListResponse(SQLModel):
    tasks: list[TaskResponse]
    count: int
```

## Migration Strategy

### Initial Migration

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX users_email_idx ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX tasks_user_id_idx ON tasks(user_id);
```

## Query Patterns

### Common Queries

```sql
-- Get user by email (login)
SELECT * FROM users WHERE email = $1;

-- Get all tasks for user
SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC;

-- Create task
INSERT INTO tasks (title, user_id) VALUES ($1, $2) RETURNING *;

-- Update task
UPDATE tasks SET title = $1, completed = $2, updated_at = NOW()
WHERE id = $3 AND user_id = $4 RETURNING *;

-- Delete task
DELETE FROM tasks WHERE id = $1 AND user_id = $2;

-- Toggle task completion
UPDATE tasks SET completed = NOT completed, updated_at = NOW()
WHERE id = $1 AND user_id = $2 RETURNING *;
```
