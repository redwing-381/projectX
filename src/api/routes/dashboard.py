"""Dashboard routes."""

import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.deps import get_db_optional
from src.db import crud
from src.config import cache

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


def get_dashboard_data(db: Session | None) -> dict:
    """Get all dashboard data with caching."""
    if db is None:
        return {
            "stats": {"emails_checked": 0, "alerts_sent": 0},
            "recent_alerts": [],
            "device_count": 0,
            "last_sync": None,
            "source_counts": {},
        }
    
    # Try cache first
    cached = cache.get("dashboard_data")
    if cached:
        return cached
    
    try:
        data = {
            "stats": crud.get_today_stats(db),
            "recent_alerts": crud.get_recent_alerts(db, limit=5),
            "device_count": crud.get_device_count(db),
            "last_sync": crud.get_last_sync_time(db),
            "source_counts": crud.get_notification_counts_by_source(db),
        }
        cache.set("dashboard_data", data)
        return data
    except Exception as e:
        logger.warning(f"Could not fetch stats: {e}")
        return {
            "stats": {"emails_checked": 0, "alerts_sent": 0},
            "recent_alerts": [],
            "device_count": 0,
            "last_sync": None,
            "source_counts": {},
        }


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session | None = Depends(get_db_optional)):
    """Dashboard home page."""
    data = get_dashboard_data(db)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": data["stats"],
        "recent_alerts": data["recent_alerts"],
        "device_count": data["device_count"],
        "last_sync": data["last_sync"],
        "source_counts": data["source_counts"],
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
            check_result = {"success": False, "message": "Pipeline not initialized"}
        else:
            result = await pipeline.run()
            check_data = {
                "emails_checked": result.emails_checked,
                "alerts_sent": result.alerts_sent,
            }
            check_result = {
                "success": True,
                "message": f"Checked {result.emails_checked} emails, sent {result.alerts_sent} alerts"
            }
            # Invalidate cache after check
            cache.invalidate("dashboard_data")
    except Exception as e:
        logger.error(f"Check emails error: {e}")
        check_result = {"success": False, "message": f"Error: {str(e)}"}
    
    # Get fresh data after check
    data = get_dashboard_data(db)
    
    # If no DB stats but we have check data, use that
    if data["stats"]["emails_checked"] == 0 and check_data:
        data["stats"]["emails_checked"] = check_data.get('emails_checked', 0)
        data["stats"]["alerts_sent"] = check_data.get('alerts_sent', 0)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": data["stats"],
        "recent_alerts": data["recent_alerts"],
        "device_count": data["device_count"],
        "last_sync": data["last_sync"],
        "source_counts": data["source_counts"],
        "check_result": check_result,
    })
