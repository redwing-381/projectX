"""Dashboard routes."""

import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.deps import get_db_optional
from src.db import crud

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session | None = Depends(get_db_optional)):
    """Dashboard home page."""
    stats = {"emails_checked": 0, "alerts_sent": 0}
    recent_alerts = []
    device_count = 0
    last_sync = None
    source_counts = {}
    
    if db is not None:
        try:
            stats = crud.get_today_stats(db)
            recent_alerts = crud.get_recent_alerts(db, limit=5)
            device_count = crud.get_device_count(db)
            last_sync = crud.get_last_sync_time(db)
            source_counts = crud.get_notification_counts_by_source(db)
        except Exception as e:
            logger.warning(f"Could not fetch stats: {e}")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": stats,
        "recent_alerts": recent_alerts,
        "device_count": device_count,
        "last_sync": last_sync,
        "source_counts": source_counts,
        "check_result": None,
    })


@router.post("/web/check", response_class=HTMLResponse)
async def web_check_emails(request: Request, db: Session | None = Depends(get_db_optional)):
    """Check emails and return to dashboard with results."""
    check_result = None
    check_data = None
    
    # Run the check directly using the pipeline (no HTTP call needed)
    try:
        from src.main import pipeline
        
        if pipeline is None:
            check_result = {"success": False, "message": "❌ Pipeline not initialized"}
        else:
            result = await pipeline.run()
            check_data = {
                "emails_checked": result.emails_checked,
                "alerts_sent": result.alerts_sent,
            }
            check_result = {
                "success": True,
                "message": f"✅ Checked {result.emails_checked} emails, sent {result.alerts_sent} alerts"
            }
    except Exception as e:
        logger.error(f"Check emails error: {e}")
        check_result = {"success": False, "message": f"❌ Error: {str(e)}"}
    
    # Get stats from database
    stats = {"emails_checked": 0, "alerts_sent": 0}
    recent_alerts = []
    device_count = 0
    last_sync = None
    source_counts = {}
    
    if db is not None:
        try:
            stats = crud.get_today_stats(db)
            recent_alerts = crud.get_recent_alerts(db, limit=5)
            device_count = crud.get_device_count(db)
            last_sync = crud.get_last_sync_time(db)
            source_counts = crud.get_notification_counts_by_source(db)
        except Exception as e:
            logger.warning(f"Could not fetch stats: {e}")
    
    # If no DB stats but we have check data, use that
    if stats["emails_checked"] == 0 and check_data:
        stats["emails_checked"] = check_data.get('emails_checked', 0)
        stats["alerts_sent"] = check_data.get('alerts_sent', 0)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": stats,
        "recent_alerts": recent_alerts,
        "device_count": device_count,
        "last_sync": last_sync,
        "source_counts": source_counts,
        "check_result": check_result,
    })
