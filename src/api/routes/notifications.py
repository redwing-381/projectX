"""Notifications page routes."""

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

# App source mapping for display
APP_DISPLAY_NAMES = {
    "android:whatsapp": ("WhatsApp", "#25D366"),
    "android:instagram": ("Instagram", "#E4405F"),
    "android:telegram": ("Telegram", "#0088cc"),
    "android:slack": ("Slack", "#4A154B"),
    "android:discord": ("Discord", "#5865F2"),
    "android:messenger": ("Messenger", "#0084FF"),
    "android:sms": ("SMS", "#6B7280"),
    "email": ("Email", "#EA4335"),
    "telegram": ("Telegram (Legacy)", "#0088cc"),
}


@router.get("/notifications", response_class=HTMLResponse)
async def notifications_page(
    request: Request,
    app: Optional[str] = None,
    page: int = Query(1, ge=1),
    db: Session | None = Depends(get_db_optional),
):
    """Notifications page with app filtering and pagination."""
    notifications = []
    total = 0
    app_counts = {}
    per_page = 20
    
    if db is not None:
        try:
            # Get counts by source
            app_counts = crud.get_notification_counts_by_source(db)
            
            # Get filtered notifications
            skip = (page - 1) * per_page
            
            if app and app != "all":
                # Map app filter to source prefix
                source_prefix = f"android:{app.lower()}" if app != "email" else "email"
                notifications = crud.get_notifications_by_source(db, source_prefix, skip=skip, limit=per_page)
                total = app_counts.get(source_prefix, 0)
            else:
                # Get all notifications
                notifications = crud.get_alerts(db, skip=skip, limit=per_page)
                total = crud.get_alerts_count(db)
        except Exception as e:
            logger.warning(f"Could not fetch notifications: {e}")
    
    # Calculate total pages
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    # Calculate total for "All" tab
    all_count = sum(app_counts.values())
    
    return templates.TemplateResponse("notifications.html", {
        "request": request,
        "active_page": "notifications",
        "notifications": notifications,
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "current_app": app or "all",
        "app_counts": app_counts,
        "all_count": all_count,
        "app_display_names": APP_DISPLAY_NAMES,
    })
