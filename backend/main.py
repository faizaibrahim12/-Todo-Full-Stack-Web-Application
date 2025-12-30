"""
FastAPI application entry point for Todo App.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_db_and_tables
from routes import auth_router, tasks_router, chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup and shutdown.
    Creates database tables on startup.
    """
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed


# Initialize FastAPI app
app = FastAPI(
    title="Todo App API",
    description="Multi-user todo application with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Todo App API is running"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Todo App API",
        "docs": "/docs",
        "health": "/health",
    }
