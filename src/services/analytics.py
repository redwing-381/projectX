"""Analytics service for dashboard metrics and charts."""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func, desc, case
from sqlalchemy.orm import Session

from src.db.models import AlertHistory


def get_emails_by_day(db: Session, days: int = 7) -> list[dict]:
    """Get message counts grouped by day for line chart.
    
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
    """Get top senders by message count for bar chart.
    
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


def get_source_breakdown(db: Session) -> dict:
    """Get message counts by source (email, whatsapp, telegram, etc).
    
    Returns: {"email": 50, "whatsapp": 30, "telegram": 10, "other": 5}
    """
    results = (
        db.query(
            AlertHistory.source,
            func.count(AlertHistory.id).label("count")
        )
        .group_by(AlertHistory.source)
        .all()
    )
    
    breakdown = {"email": 0, "whatsapp": 0, "telegram": 0, "other": 0}
    
    for r in results:
        source = r.source or "email"
        if source == "email":
            breakdown["email"] += r.count
        elif "whatsapp" in source.lower():
            breakdown["whatsapp"] += r.count
        elif "telegram" in source.lower():
            breakdown["telegram"] += r.count
        else:
            breakdown["other"] += r.count
    
    return breakdown


def get_summary_metrics(db: Session) -> dict:
    """Get key metrics for dashboard cards.
    
    Returns: {"total_messages": 200, "total_alerts": 25, "alert_rate": 12.5, ...}
    """
    total_messages = db.query(func.count(AlertHistory.id)).scalar() or 0
    
    total_alerts = (
        db.query(func.count(AlertHistory.id))
        .filter(AlertHistory.urgency == "URGENT")
        .scalar() or 0
    )
    
    alert_rate = (total_alerts / total_messages * 100) if total_messages > 0 else 0.0
    
    # Get today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_messages = (
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
    
    # Get source breakdown
    source_breakdown = get_source_breakdown(db)
    
    return {
        "total_emails": source_breakdown["email"],
        "total_messages": total_messages,
        "total_alerts": total_alerts,
        "alert_rate": round(alert_rate, 1),
        "today_emails": today_messages,
        "today_alerts": today_alerts,
        "source_breakdown": source_breakdown,
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
