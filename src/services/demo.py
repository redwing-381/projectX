"""Demo mode service for hackathon presentation."""

from datetime import datetime
from typing import Optional
from src.models.schemas import Email, AlertResult, Urgency


# 10 diverse sample emails covering all classification scenarios
SAMPLE_EMAILS = [
    # 1. VIP sender match (boss)
    Email(
        id="demo-001",
        sender="Sarah Chen <boss@company.com>",
        subject="Quick sync needed on Q1 roadmap",
        snippet="Hey, can we hop on a call in 30 mins? Need to discuss the timeline changes for the product launch.",
    ),
    # 2. Keyword match (URGENT in subject)
    Email(
        id="demo-002",
        sender="IT Support <support@company.com>",
        subject="URGENT: Password reset required",
        snippet="Your account password will expire in 24 hours. Please reset it immediately to avoid losing access.",
    ),
    # 3. Time-sensitive deadline (AI classification)
    Email(
        id="demo-003",
        sender="Professor Williams <prof.williams@university.edu>",
        subject="Assignment deadline extended to TODAY 11:59 PM",
        snippet="Due to technical issues, I'm extending the deadline. Please submit by tonight.",
    ),
    # 4. Marketing/promotional (NOT urgent)
    Email(
        id="demo-004",
        sender="Amazon <deals@amazon.com>",
        subject="Flash Sale: Up to 70% off electronics",
        snippet="Don't miss out on our biggest sale of the year! Limited time offer on laptops, phones, and more.",
    ),
    # 5. Newsletter (NOT urgent)
    Email(
        id="demo-005",
        sender="TechCrunch Daily <newsletter@techcrunch.com>",
        subject="Your daily tech digest - Jan 19, 2026",
        snippet="Top stories: AI breakthrough at OpenAI, Tesla's new factory, and more startup funding news.",
    ),
    # 6. Family emergency (AI classification - URGENT)
    Email(
        id="demo-006",
        sender="Mom <mom@gmail.com>",
        subject="Call me when you can - Dad's in hospital",
        snippet="Don't panic, he's stable now. Had a minor fall. Doctor says he'll be fine but call when free.",
    ),
    # 7. Job interview follow-up (AI classification - URGENT)
    Email(
        id="demo-007",
        sender="HR Team <recruiting@techstartup.io>",
        subject="Interview scheduled for tomorrow 10 AM",
        snippet="Congratulations! We'd like to invite you for a final round interview. Please confirm your availability.",
    ),
    # 8. Social media notification (NOT urgent)
    Email(
        id="demo-008",
        sender="LinkedIn <notifications@linkedin.com>",
        subject="You have 5 new connection requests",
        snippet="John Smith and 4 others want to connect with you. See who's in your network.",
    ),
    # 9. Financial alert (AI classification - could be URGENT)
    Email(
        id="demo-009",
        sender="Chase Bank <alerts@chase.com>",
        subject="Unusual activity detected on your account",
        snippet="We noticed a $500 transaction from an unfamiliar location. If this wasn't you, please call us.",
    ),
    # 10. System notification (NOT urgent)
    Email(
        id="demo-010",
        sender="GitHub <noreply@github.com>",
        subject="[projectx] New pull request #42",
        snippet="dependabot opened a pull request: Bump fastapi from 0.109.0 to 0.110.0",
    ),
]


def get_sample_emails() -> list[Email]:
    """Return sample emails for demo mode."""
    return SAMPLE_EMAILS.copy()


def is_demo_mode(session: dict) -> bool:
    """Check if demo mode is active in session."""
    return session.get("demo_mode", False)


def activate_demo(session: dict) -> None:
    """Activate demo mode in session."""
    session["demo_mode"] = True
    session["demo_results"] = []
    session["demo_activated_at"] = datetime.utcnow().isoformat()


def deactivate_demo(session: dict) -> None:
    """Deactivate demo mode and clear session data."""
    session.pop("demo_mode", None)
    session.pop("demo_results", None)
    session.pop("demo_activated_at", None)


def store_demo_results(session: dict, results: list[AlertResult]) -> None:
    """Store classification results in session (not DB).
    
    Keeps only the last 20 results to prevent session bloat.
    """
    # Convert AlertResult objects to dicts for JSON serialization
    result_dicts = []
    for r in results:
        result_dicts.append({
            "email_id": r.email_id,
            "sender": r.sender,
            "subject": r.subject,
            "urgency": r.urgency.value if hasattr(r.urgency, 'value') else r.urgency,
            "reason": r.reason,
            "sms_sent": r.sms_sent,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    existing = session.get("demo_results", [])
    combined = existing + result_dicts
    
    # Keep only last 20 results
    session["demo_results"] = combined[-20:]


def get_demo_results(session: dict) -> list[dict]:
    """Retrieve demo results from session."""
    return session.get("demo_results", [])


def get_demo_stats(session: dict) -> dict:
    """Get demo mode statistics."""
    results = get_demo_results(session)
    urgent_count = sum(1 for r in results if r.get("urgency") == "URGENT")
    
    return {
        "total_checked": len(results),
        "alerts_sent": urgent_count,
        "demo_activated_at": session.get("demo_activated_at"),
    }
