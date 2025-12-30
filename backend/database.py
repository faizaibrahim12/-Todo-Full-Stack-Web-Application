"""
Database connection and session management.
"""
from sqlmodel import create_engine, Session, SQLModel
from config import get_settings

settings = get_settings()

# Create engine - supports both SQLite and PostgreSQL
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        echo=True,  # Log SQL queries in development
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        settings.database_url,
        echo=True,  # Log SQL queries in development
        connect_args={"sslmode": "require"}  # Required for Neon
    )


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency for getting database sessions.
    Use with FastAPI Depends().
    """
    with Session(engine) as session:
        yield session
