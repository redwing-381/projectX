"""Alert history routes."""

import logging
from typing import Optional
from io import StringIO
import csv

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, StreamingResponse
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
    format: Optional[str] = None,
    db: Session | None = Depends(get_db_optional),
):
    """Alert history page with pagination and filters."""
    # Handle CSV export
    if format == "csv":
        return await export_history_csv(db)
    
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


async def export_history_csv(db: Session | None):
    """Export all history as CSV file."""
    output = StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        "ID", "Date", "Source", "Sender", "Subject", 
        "Urgency", "Reason", "SMS Sent"
    ])
    
    if db is not None:
        try:
            # Get all alerts (no pagination for export)
            alerts = crud.get_alerts(db, skip=0, limit=10000)
            
            for alert in alerts:
                writer.writerow([
                    alert.email_id,
                    alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    alert.source or "email",
                    alert.sender,
                    alert.subject,
                    alert.urgency,
                    alert.reason,
                    "Yes" if alert.sms_sent else "No",
                ])
        except Exception as e:
            logger.error(f"CSV export error: {e}")
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=projectx_history.csv"}
    )
