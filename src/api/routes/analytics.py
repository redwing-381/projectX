"""Analytics routes for charts and metrics."""

import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.deps import get_db_optional
from src.services import analytics

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, db: Session | None = Depends(get_db_optional)):
    """Render analytics dashboard page."""
    if db is None:
        return templates.TemplateResponse("analytics.html", {
            "request": request,
            "active_page": "analytics",
            "has_data": False,
            "metrics": {"total_emails": 0, "total_alerts": 0, "alert_rate": 0, "today_emails": 0, "today_alerts": 0},
            "emails_by_day": [],
            "urgency_ratio": {"urgent": 0, "not_urgent": 0},
            "top_senders": [],
        })
    
    try:
        metrics = analytics.get_summary_metrics(db)
        emails_by_day = analytics.get_emails_by_day(db, days=7)
        urgency_ratio = analytics.get_urgency_ratio(db)
        top_senders = analytics.get_top_senders(db, limit=5)
        has_data = metrics["total_emails"] > 0
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        has_data = False
        metrics = {"total_emails": 0, "total_alerts": 0, "alert_rate": 0, "today_emails": 0, "today_alerts": 0}
        emails_by_day = []
        urgency_ratio = {"urgent": 0, "not_urgent": 0}
        top_senders = []
    
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "active_page": "analytics",
        "has_data": has_data,
        "metrics": metrics,
        "emails_by_day": emails_by_day,
        "urgency_ratio": urgency_ratio,
        "top_senders": top_senders,
    })


@router.get("/api/analytics/data")
async def analytics_data(db: Session | None = Depends(get_db_optional)):
    """Return analytics data as JSON for AJAX updates."""
    if db is None:
        return JSONResponse({
            "metrics": {"total_emails": 0, "total_alerts": 0, "alert_rate": 0},
            "emails_by_day": [],
            "urgency_ratio": {"urgent": 0, "not_urgent": 0},
            "top_senders": [],
        })
    
    try:
        return JSONResponse({
            "metrics": analytics.get_summary_metrics(db),
            "emails_by_day": analytics.get_emails_by_day(db, days=7),
            "urgency_ratio": analytics.get_urgency_ratio(db),
            "top_senders": analytics.get_top_senders(db, limit=5),
        })
    except Exception as e:
        logger.error(f"Analytics API error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
