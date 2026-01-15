"""Web dashboard routes."""

import logging
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.db.database import get_db, engine
from src.db import crud
from src.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

# Security for API endpoints
security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify API key from Authorization header."""
    settings = get_settings()
    
    if not settings.api_key:
        return True
    
    if not credentials:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if credentials.credentials != settings.api_key:
        from fastapi import HTTPException
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
    
    # Check Telegram status
    telegram_connected = bool(settings.telegram_api_id and settings.telegram_session)
    telegram_user = None
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": stats,
        "recent_alerts": recent_alerts,
        "telegram_connected": telegram_connected,
        "telegram_user": telegram_user,
        "check_result": None,
    })


@router.post("/web/check", response_class=HTMLResponse)
async def web_check_emails(request: Request):
    """Check emails and return to dashboard with results."""
    settings = get_settings()
    check_result = None
    check_data = None
    
    # Run the check
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/check", timeout=60.0)
            if response.status_code == 200:
                data = response.json()
                check_data = data.get('data', {})
                check_result = {
                    "success": True,
                    "message": f"✅ Checked {check_data.get('emails_checked', 0)} emails, sent {check_data.get('alerts_sent', 0)} alerts"
                }
            else:
                check_result = {"success": False, "message": f"❌ Error: {response.text}"}
    except Exception as e:
        check_result = {"success": False, "message": f"❌ Error: {str(e)}"}
    
    # Get stats from database or use check results
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
    
    # If no DB stats but we have check data, use that
    if stats["emails_checked"] == 0 and check_data:
        stats["emails_checked"] = check_data.get('emails_checked', 0)
        stats["alerts_sent"] = check_data.get('alerts_sent', 0)
    
    telegram_connected = bool(settings.telegram_api_id and settings.telegram_session)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": stats,
        "recent_alerts": recent_alerts,
        "telegram_connected": telegram_connected,
        "telegram_user": None,
        "check_result": check_result,
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
    
    # Get counts and monitoring settings
    vip_count = 0
    keyword_count = 0
    monitoring_enabled = False
    check_interval = 5
    db_connected = is_db_connected()
    telegram_connected = bool(settings.telegram_api_id and settings.telegram_session)
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                vip_count = len(crud.get_vip_senders(db))
                keyword_count = len(crud.get_keywords(db))
                monitoring_enabled = crud.get_monitoring_enabled(db)
                check_interval = crud.get_check_interval(db)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not fetch counts: {e}")
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "active_page": "settings",
        "phone_masked": phone_masked,
        "monitoring_enabled": monitoring_enabled,
        "check_interval": check_interval,
        "db_connected": db_connected,
        "telegram_connected": telegram_connected,
        "vip_count": vip_count,
        "keyword_count": keyword_count,
    })


@router.post("/settings/toggle-scheduled-monitoring")
async def toggle_scheduled_monitoring():
    """Toggle scheduled monitoring on/off."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                current = crud.get_monitoring_enabled(db)
                crud.set_monitoring_enabled(db, not current)
                logger.info(f"Scheduled monitoring {'disabled' if current else 'enabled'}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Could not toggle monitoring: {e}")
    
    return RedirectResponse("/settings", status_code=303)


@router.post("/settings/set-interval")
async def set_check_interval(interval: int = Form(...)):
    """Set the email check interval."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.set_check_interval(db, interval)
                logger.info(f"Check interval set to {interval} minutes")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Could not set interval: {e}")
    
    return RedirectResponse("/settings", status_code=303)


@router.post("/settings/toggle-monitoring")
async def toggle_monitoring():
    """Toggle monitoring status (legacy endpoint).
    
    Redirects to the new toggle endpoint.
    """
    return await toggle_scheduled_monitoring()


# =============================================================================
# API Endpoints for CLI (Protected)
# =============================================================================

@router.get("/api/monitoring")
async def get_monitoring_status(authenticated: bool = Depends(verify_api_key)):
    """Get current monitoring status (for CLI)."""
    from src.main import monitoring_running
    
    enabled = False
    interval = 5
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                enabled = crud.get_monitoring_enabled(db)
                interval = crud.get_check_interval(db)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not fetch monitoring status: {e}")
    
    return {
        "enabled": enabled,
        "running": monitoring_running,
        "interval_minutes": interval,
    }


@router.post("/api/monitoring/start")
async def start_monitoring(authenticated: bool = Depends(verify_api_key)):
    """Enable scheduled monitoring (for CLI)."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.set_monitoring_enabled(db, True)
            finally:
                db.close()
            return {"success": True, "message": "Scheduled monitoring enabled"}
        except Exception as e:
            logger.error(f"Could not enable monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Database not connected"}


@router.post("/api/monitoring/stop")
async def stop_monitoring(authenticated: bool = Depends(verify_api_key)):
    """Disable scheduled monitoring (for CLI)."""
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.set_monitoring_enabled(db, False)
            finally:
                db.close()
            return {"success": True, "message": "Scheduled monitoring disabled"}
        except Exception as e:
            logger.error(f"Could not disable monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Database not connected"}


@router.post("/api/monitoring/interval")
async def set_monitoring_interval(minutes: int = Form(...), authenticated: bool = Depends(verify_api_key)):
    """Set monitoring interval (for CLI)."""
    if minutes < 1 or minutes > 1440:
        return {"success": False, "error": "Interval must be between 1 and 1440 minutes"}
    
    if engine is not None:
        try:
            from src.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.set_check_interval(db, minutes)
            finally:
                db.close()
            return {"success": True, "message": f"Interval set to {minutes} minutes"}
        except Exception as e:
            logger.error(f"Could not set interval: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Database not connected"}
