"""Database connection and session management."""

import os
from contextlib import contextmanager

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

# Load .env file before reading DATABASE_URL
from dotenv import load_dotenv
load_dotenv()


def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.environ.get("DATABASE_URL", "")
    
    # Railway uses postgres:// but SQLAlchemy needs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    return url


# Create engine with optimized connection pooling
DATABASE_URL = get_database_url()

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,           # Base pool size
        max_overflow=10,       # Extra connections when needed
        pool_pre_ping=True,    # Verify connections before use
        pool_recycle=300,      # Recycle connections after 5 minutes
        echo=False,            # Disable SQL logging for performance
        connect_args={
            "connect_timeout": 10,  # Connection timeout
            "options": "-c statement_timeout=30000"  # 30s query timeout
        } if "postgresql" in DATABASE_URL else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Set session-level optimizations
    @event.listens_for(engine, "connect")
    def set_pg_options(dbapi_conn, connection_record):
        """Set PostgreSQL session options for performance."""
        try:
            cursor = dbapi_conn.cursor()
            cursor.execute("SET work_mem = '16MB'")  # More memory for sorts
            cursor.close()
        except Exception:
            pass  # Ignore if not PostgreSQL
else:
    engine = None
    SessionLocal = None


def get_db():
    """Dependency for FastAPI routes to get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL environment variable.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database session (for non-FastAPI code)."""
    if SessionLocal is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL environment variable.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    if engine is None:
        return
    
    from src.db.models import Base
    Base.metadata.create_all(bind=engine)
    
    # Run migrations for new columns
    _run_migrations()


def _run_migrations():
    """Run database migrations for new columns."""
    if engine is None:
        return
    
    from sqlalchemy import text
    
    migrations = [
        # Add source column to alert_history if it doesn't exist
        """
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'alert_history' AND column_name = 'source'
            ) THEN 
                ALTER TABLE alert_history ADD COLUMN source VARCHAR(20) DEFAULT 'email';
            END IF;
        END $$;
        """,
    ]
    
    with engine.connect() as conn:
        for migration in migrations:
            try:
                conn.execute(text(migration))
                conn.commit()
            except Exception as e:
                print(f"Migration warning: {e}")
