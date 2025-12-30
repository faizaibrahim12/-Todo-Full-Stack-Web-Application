# Quick Start Guide

Get the Todo App running in 5 minutes!

## Prerequisites

- Node.js 18+
- Python 3.11+
- Neon PostgreSQL database (free at https://neon.tech)

## Step 1: Generate Secret Key

```bash
openssl rand -base64 32
```

Copy this secret - you'll use it in both backend and frontend!

## Step 2: Configure Backend

Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
BETTER_AUTH_SECRET=<your-secret-from-step-1>
```

## Step 3: Start Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend running at http://localhost:8000

## Step 4: Configure Frontend

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<same-secret-from-step-1>
BETTER_AUTH_URL=http://localhost:3000
```

## Step 5: Start Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend running at http://localhost:3000

## Step 6: Use the App!

1. Open http://localhost:3000
2. Click "Sign up" to create an account
3. Enter email and password (8+ characters)
4. Start adding tasks!

## Verify It's Working

✅ Backend health check: http://localhost:8000/health
✅ API docs: http://localhost:8000/docs
✅ Frontend: http://localhost:3000

## Troubleshooting

**"Connection refused"**
- Make sure backend is running first
- Check NEXT_PUBLIC_API_URL points to http://localhost:8000

**"Authentication failed"**
- Verify BETTER_AUTH_SECRET is identical in both .env files
- Make sure it's at least 32 characters

**"Database error"**
- Check your Neon connection string includes `?sslmode=require`
- Verify database is active in Neon dashboard

## Next Steps

- Add some tasks and test the features
- Try logging out and back in
- Check that your tasks persist
- Open in mobile view to test responsive design

For detailed documentation, see [README.md](./README.md)
