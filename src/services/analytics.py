"""Analytics service for dashboard metrics and charts."""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.db.models import AlertHistory


def get_emails_by_day(db: Session, days: int = 7) -> list[dict]:
    """Get email counts grouped by day for line chart.
    
    Returns: [{"date": "2026-01-19", "count": 15}, ...]
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = (
        db.query(
            func.date(AlertHistory.created_at).label("date"),
            func.count(AlertHistory.id).label("count")
        )
        .filter(AlertHistory.created_at >= start_date)
        .group_by(func.date(AlertHistory.created_at))
        .order_by(func.date(AlertHistory.created_at))
        .all()
    )
    
    return [{"date": str(r.date), "count": r.count} for r in results]


def get_urgency_ratio(db: Session) -> dict:
    """Get urgent vs non-urgent counts for pie chart.
    
    Returns: {"urgent": 25, "not_urgent": 175}
    """
    urgent_count = (
        db.query(func.count(AlertHistory.id))
        .filter(AlertHistory.urgency == "URGENT")
        .scalar() or 0
    )
    
    total_count = db.query(func.count(AlertHistory.id)).scalar() or 0
    not_urgent_count = total_count - urgent_count
    
    return {"urgent": urgent_count, "not_urgent": not_urgent_count}


def get_top_senders(db: Session, limit: int = 5) -> list[dict]:
    """Get top senders by email count for bar chart.
    
    Returns: [{"sender": "boss@company.com", "count": 12}, ...]
    """
    results = (
        db.query(
            AlertHistory.sender,
            func.count(AlertHistory.id).label("count")
        )
        .group_by(AlertHistory.sender)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    
    return [{"sender": _extract_email(r.sender), "count": r.count} for r in results]


def get_summary_metrics(db: Session) -> dict:
    """Get key metrics for dashboard cards.
    
    Returns: {"total_emails": 200, "total_alerts": 25, "alert_rate": 12.5}
    """
    total_emails = db.query(func.count(AlertHistory.id)).scalar() or 0
    
    total_alerts = (
        db.query(func.count(AlertHistory.id))
        .filter(AlertHistory.urgency == "URGENT")
        .scalar() or 0
    )
    
    alert_rate = (total_alerts / total_emails * 100) if total_emails > 0 else 0.0
    
    # Get today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_emails = (
        db.query(func.count(AlertHistory.id))
        .filter(AlertHistory.created_at >= today_start)
        .scalar() or 0
    )
    today_alerts = (
        db.query(func.count(AlertHistory.id))
        .filter(AlertHistory.created_at >= today_start)
        .filter(AlertHistory.urgency == "URGENT")
        .scalar() or 0
    )
    
    return {
        "total_emails": total_emails,
        "total_alerts": total_alerts,
        "alert_rate": round(alert_rate, 1),
        "today_emails": today_emails,
        "today_alerts": today_alerts,
    }


def _extract_email(sender: str) -> str:
    """Extract email address from sender string.
    
    "John Doe <john@example.com>" -> "john@example.com"
    "john@example.com" -> "john@example.com"
    """
    if "<" in sender and ">" in sender:
        start = sender.index("<") + 1
        end = sender.index(">")
        return sender[start:end]
    return sender
