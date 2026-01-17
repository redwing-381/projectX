"""Architecture page routes."""

import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.deps import get_db_optional, is_db_connected
from src.db import crud

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/architecture", response_class=HTMLResponse)
async def architecture_page(request: Request, db: Session | None = Depends(get_db_optional)):
    """Architecture page with system diagram and status."""
    db_connected = is_db_connected()
    device_count = 0
    last_sync = None
    
    if db is not None:
        try:
            device_count = crud.get_device_count(db)
            last_sync = crud.get_last_sync_time(db)
        except Exception as e:
            logger.warning(f"Could not fetch device info: {e}")
    
    return templates.TemplateResponse("architecture.html", {
        "request": request,
        "active_page": "architecture",
        "db_connected": db_connected,
        "device_count": device_count,
        "last_sync": last_sync,
    })
