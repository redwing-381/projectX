"""Web dashboard routes."""

import logging
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.db.database import get_db, engine
from src.db import crud
from src.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


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


# =============================================================================
# Dashboard
# =============================================================================

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard home page."""
    settings = get_settings()
    
    # Get stats from database if available
    stats = {"emails_checked": 0, "alerts_sent": 0}
    recent_alerts = []
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                stats = crud.get_today_stats(db)
                recent_alerts = crud.get_recent_alerts(db, limit=5)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not fetch stats: {e}")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": stats,
        "recent_alerts": recent_alerts,
    })


# =============================================================================
# Alert History
# =============================================================================

@router.get("/history", response_class=HTMLResponse)
async def history(
    request: Request,
    page: int = Query(1, ge=1),
    urgency: Optional[str] = None,
    search: Optional[str] = None,
):
    """Alert history page with pagination and filters."""
    alerts = []
    total = 0
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                skip = (page - 1) * 20
                alerts = crud.get_alerts(db, skip=skip, limit=20, urgency=urgency, search=search)
                total = crud.get_alerts_count(db, urgency=urgency, search=search)
            finally:
                db.close()
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



# =============================================================================
# VIP Senders
# =============================================================================

@router.get("/vip-senders", response_class=HTMLResponse)
async def vip_senders_page(request: Request):
    """VIP senders management page."""
    senders = []
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                senders = crud.get_vip_senders(db)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not fetch VIP senders: {e}")
    
    return templates.TemplateResponse("vip_senders.html", {
        "request": request,
        "active_page": "vip",
        "senders": senders,
    })


@router.post("/vip-senders/add")
async def add_vip_sender(email: str = Form(...)):
    """Add a new VIP sender."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.add_vip_sender(db, email)
            except IntegrityError:
                db.rollback()
                logger.info(f"VIP sender already exists: {email}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Could not add VIP sender: {e}")
    
    return RedirectResponse("/vip-senders", status_code=303)


@router.post("/vip-senders/delete/{id}")
async def delete_vip_sender(id: int):
    """Delete a VIP sender."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.remove_vip_sender(db, id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Could not delete VIP sender: {e}")
    
    return RedirectResponse("/vip-senders", status_code=303)


# =============================================================================
# Keywords
# =============================================================================

@router.get("/keywords", response_class=HTMLResponse)
async def keywords_page(request: Request):
    """Keyword rules management page."""
    keywords = []
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                keywords = crud.get_keywords(db)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not fetch keywords: {e}")
    
    return templates.TemplateResponse("keywords.html", {
        "request": request,
        "active_page": "keywords",
        "keywords": keywords,
    })


@router.post("/keywords/add")
async def add_keyword(keyword: str = Form(...)):
    """Add a new keyword rule."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.add_keyword(db, keyword)
            except IntegrityError:
                db.rollback()
                logger.info(f"Keyword already exists: {keyword}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Could not add keyword: {e}")
    
    return RedirectResponse("/keywords", status_code=303)


@router.post("/keywords/delete/{id}")
async def delete_keyword(id: int):
    """Delete a keyword rule."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.remove_keyword(db, id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Could not delete keyword: {e}")
    
    return RedirectResponse("/keywords", status_code=303)


# =============================================================================
# Settings
# =============================================================================

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    settings = get_settings()
    
    # Mask phone number
    phone = settings.alert_phone_number
    phone_masked = f"***-***-{phone[-4:]}" if phone and len(phone) >= 4 else "Not configured"
    
    # Get counts
    vip_count = 0
    keyword_count = 0
    db_connected = is_db_connected()
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                vip_count = len(crud.get_vip_senders(db))
                keyword_count = len(crud.get_keywords(db))
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not fetch counts: {e}")
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "active_page": "settings",
        "phone_masked": phone_masked,
        "monitoring_active": not settings.monitoring_paused,
        "db_connected": db_connected,
        "vip_count": vip_count,
        "keyword_count": keyword_count,
    })


@router.post("/settings/toggle-monitoring")
async def toggle_monitoring():
    """Toggle monitoring status."""
    # This would need to update a setting - for now just redirect
    # In production, you'd update a database setting or environment variable
    return RedirectResponse("/settings", status_code=303)
