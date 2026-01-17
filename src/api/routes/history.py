"""Alert history routes."""

import logging
from typing import Optional

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.deps import get_db_optional
from src.db import crud

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/history", response_class=HTMLResponse)
async def history(
    request: Request,
    page: int = Query(1, ge=1),
    urgency: Optional[str] = None,
    search: Optional[str] = None,
    db: Session | None = Depends(get_db_optional),
):
    """Alert history page with pagination and filters."""
    alerts = []
    total = 0
    
    if db is not None:
        try:
            skip = (page - 1) * 20
            alerts = crud.get_alerts(db, skip=skip, limit=20, urgency=urgency, search=search)
            total = crud.get_alerts_count(db, urgency=urgency, search=search)
        except Exception as e:
            logger.warning(f"Could not fetch history: {e}")
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "active_page": "history",
        "alerts": alerts,
        "total": total,
        "page": page,
        "urgency": urgency,
        "search": search,
    })
