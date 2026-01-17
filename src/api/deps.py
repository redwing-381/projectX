"""Shared dependencies for API routes."""

from typing import Generator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.db.database import SessionLocal, engine
from src.config import get_settings

# Security scheme for API endpoints
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Database session dependency.
    
    Yields a database session and ensures it's closed after use.
    Use with FastAPI's Depends(): db: Session = Depends(get_db)
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_optional() -> Generator[Session | None, None, None]:
    """Optional database session dependency.
    
    Returns None if database is not available instead of raising an error.
    Useful for pages that can render with partial data.
    """
    if engine is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """Verify API key from Authorization header.
    
    Returns True if:
    - No API_KEY is configured (auth disabled)
    - Valid API key provided
    
    Raises HTTPException if:
    - API_KEY is configured but no credentials provided
    - API_KEY is configured but credentials don't match
    """
    settings = get_settings()
    
    if not settings.api_key:
        return True
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Use 'projectx login' to authenticate.",
        )
    
    if credentials.credentials != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


def is_db_connected() -> bool:
    """Check if database is connected."""
    try:
        if engine is None:
            return False
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
