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


# =============================================================================
# Android App Notifications API
# =============================================================================

from pydantic import BaseModel
from typing import List


class NotificationPayload(BaseModel):
    """Individual notification from Android app."""
    id: str
    app: str
    sender: str
    text: str
    timestamp: int


class NotificationBatchRequest(BaseModel):
    """Batch of notifications from Android app."""
    device_id: str
    notifications: List[NotificationPayload]


class NotificationBatchResponse(BaseModel):
    """Response after processing notifications."""
    success: bool
    processed: int
    urgent_count: int
    message: str = ""


@router.post("/api/notifications", response_model=NotificationBatchResponse)
async def receive_notifications(
    request: NotificationBatchRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """Receive notifications from Android app, classify urgency, send SMS for urgent ones.
    
    This endpoint:
    1. Receives a batch of notifications from the Android app
    2. Classifies each notification for urgency using the AI classifier
    3. Sends SMS alerts for urgent notifications
    4. Saves all notifications to the database
    """
    from src.main import pipeline
    from src.models.schemas import TelegramMessage, UrgencyLevel
    from fastapi import HTTPException
    
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    processed = 0
    urgent_count = 0
    
    for notif in request.notifications:
        try:
            # Create a message object for classification
            # Reuse TelegramMessage schema since it has similar structure
            message = TelegramMessage(
                sender=notif.sender,
                text=notif.text,
                timestamp=notif.timestamp,
            )
            
            # Classify using the crew/classifier
            try:
                from src.agents.telegram_crew import TelegramProcessingCrew
                crew = TelegramProcessingCrew(verbose=False)
                classification = crew.process_message(message)
            except Exception as crew_error:
                logger.warning(f"Crew classification failed: {crew_error}, using fallback")
                # Fallback: simple keyword-based classification
                urgent_keywords = ["urgent", "emergency", "asap", "help", "important", "call me"]
                is_urgent = any(kw in notif.text.lower() for kw in urgent_keywords)
                
                class SimpleClassification:
                    urgency = "URGENT" if is_urgent else "NOT_URGENT"
                    reason = "Keyword match" if is_urgent else "No urgent keywords"
                    sms_message = f"{notif.app}: {notif.sender} - {notif.text[:100]}" if is_urgent else None
                
                classification = SimpleClassification()
            
            # Save to database
            if engine is not None:
                try:
                    from src.db.database import SessionLocal
                    db = SessionLocal()
                    try:
                        crud.create_alert(
                            db=db,
                            sender=notif.sender,
                            subject=f"{notif.app} notification",
                            urgency=classification.urgency,
                            reason=classification.reason,
                            sms_sent=False,
                            source=f"android:{notif.app.lower()}",
                        )
                    finally:
                        db.close()
                except Exception as db_error:
                    logger.warning(f"Failed to save notification: {db_error}")
            
            # Send SMS if urgent
            if classification.urgency == "URGENT":
                urgent_count += 1
                sms_text = getattr(classification, 'sms_message', None) or f"{notif.app}: {notif.sender} - {notif.text[:100]}"
                
                try:
                    settings = get_settings()
                    sent = pipeline.twilio.send_sms(
                        to_number=settings.alert_phone_number,
                        message=sms_text,
                    )
                    if sent:
                        logger.info(f"SMS sent for urgent {notif.app} notification from {notif.sender}")
                        # Update database record
                        if engine is not None:
                            try:
                                from src.db.database import SessionLocal
                                db = SessionLocal()
                                try:
                                    latest = crud.get_recent_alerts(db, limit=1)
                                    if latest:
                                        latest[0].sms_sent = True
                                        db.commit()
                                finally:
                                    db.close()
                            except Exception:
                                pass
                except Exception as sms_error:
                    logger.error(f"Failed to send SMS: {sms_error}")
            
            processed += 1
            
        except Exception as e:
            logger.error(f"Error processing notification {notif.id}: {e}")
    
    message = f"Processed {processed} notifications"
    if urgent_count > 0:
        message += f", {urgent_count} urgent (SMS sent)"
    
    logger.info(f"Android batch: {message} from device {request.device_id}")
    
    return NotificationBatchResponse(
        success=True,
        processed=processed,
        urgent_count=urgent_count,
        message=message,
    )
