"""Quick actions API for one-click operations."""

import logging
import re

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.api.deps import get_db_optional
from src.db import crud

logger = logging.getLogger(__name__)
router = APIRouter()


def extract_email(sender: str) -> str | None:
    """Extract email address from sender string.
    
    "John Doe <john@example.com>" -> "john@example.com"
    "john@example.com" -> "john@example.com"
    """
    # Try to extract from angle brackets first
    match = re.search(r'<([^>]+@[^>]+)>', sender)
    if match:
        return match.group(1).lower()
    
    # Check if it's already a plain email
    if re.match(r'^[^@]+@[^@]+\.[^@]+$', sender.strip()):
        return sender.strip().lower()
    
    return None


@router.post("/api/quick-actions/add-vip")
async def add_sender_to_vip(sender: str, db: Session | None = Depends(get_db_optional)):
    """Add sender to VIP list via AJAX."""
    if db is None:
        return JSONResponse({"success": False, "error": "Database not available"}, status_code=503)
    
    email = extract_email(sender)
    if not email:
        return JSONResponse({"success": False, "error": "Could not extract email from sender"}, status_code=400)
    
    try:
        # Check if already VIP
        is_vip, _ = crud.is_vip_sender(db, email)
        if is_vip:
            return JSONResponse({"success": True, "already_vip": True, "email": email})
        
        # Add to VIP list
        crud.add_vip_sender(db, email)
        logger.info(f"Added {email} to VIP list via quick action")
        
        # Invalidate cache
        from src.config import cache
        cache.invalidate("vip_senders")
        
        return JSONResponse({"success": True, "already_vip": False, "email": email})
    except Exception as e:
        logger.error(f"Error adding VIP sender: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.get("/api/quick-actions/check-vip")
async def check_if_vip(sender: str, db: Session | None = Depends(get_db_optional)):
    """Check if sender is already in VIP list."""
    if db is None:
        return JSONResponse({"is_vip": False, "error": "Database not available"})
    
    email = extract_email(sender)
    if not email:
        return JSONResponse({"is_vip": False, "error": "Could not extract email"})
    
    try:
        is_vip, _ = crud.is_vip_sender(db, email)
        return JSONResponse({"is_vip": is_vip, "email": email})
    except Exception as e:
        logger.error(f"Error checking VIP status: {e}")
        return JSONResponse({"is_vip": False, "error": str(e)})
