"""Settings routes."""

import logging

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.deps import get_db_optional, is_db_connected
from src.db import crud
from src.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session | None = Depends(get_db_optional)):
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
    device_count = 0
    devices = []
    last_sync = None
    mobile_notification_count = 0
    api_key_configured = bool(settings.api_key)
    mobile_enabled_count = 0
    mobile_monitoring_enabled = False
    
    if db is not None:
        try:
            vip_count = len(crud.get_vip_senders(db))
            keyword_count = len(crud.get_keywords(db))
            monitoring_enabled = crud.get_monitoring_enabled(db)
            check_interval = crud.get_check_interval(db)
            device_count = crud.get_device_count(db)
            devices = crud.get_all_devices(db)
            last_sync = crud.get_last_sync_time(db)
            mobile_notification_count = crud.get_total_mobile_notifications(db)
            
            # Calculate mobile monitoring status
            mobile_enabled_count = sum(1 for d in devices if getattr(d, 'monitoring_enabled', True))
            mobile_monitoring_enabled = device_count > 0 and mobile_enabled_count == device_count
        except Exception as e:
            logger.warning(f"Could not fetch counts: {e}")
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "active_page": "settings",
        "phone_masked": phone_masked,
        "monitoring_enabled": monitoring_enabled,
        "check_interval": check_interval,
        "db_connected": db_connected,
        "vip_count": vip_count,
        "keyword_count": keyword_count,
        "device_count": device_count,
        "devices": devices,
        "last_sync": last_sync,
        "mobile_notification_count": mobile_notification_count,
        "api_key_configured": api_key_configured,
        "mobile_enabled_count": mobile_enabled_count,
        "mobile_monitoring_enabled": mobile_monitoring_enabled,
    })


@router.post("/settings/toggle-scheduled-monitoring")
async def toggle_scheduled_monitoring(db: Session | None = Depends(get_db_optional)):
    """Toggle scheduled monitoring on/off."""
    if db is not None:
        try:
            current = crud.get_monitoring_enabled(db)
            crud.set_monitoring_enabled(db, not current)
            logger.info(f"Scheduled monitoring {'disabled' if current else 'enabled'}")
        except Exception as e:
            logger.error(f"Could not toggle monitoring: {e}")
    
    return RedirectResponse("/settings", status_code=303)


@router.post("/settings/set-interval")
async def set_check_interval(
    interval: int = Form(...),
    db: Session | None = Depends(get_db_optional),
):
    """Set the email check interval."""
    if db is not None:
        try:
            crud.set_check_interval(db, interval)
            logger.info(f"Check interval set to {interval} minutes")
        except Exception as e:
            logger.error(f"Could not set interval: {e}")
    
    return RedirectResponse("/settings", status_code=303)


@router.post("/settings/toggle-monitoring")
async def toggle_monitoring(db: Session | None = Depends(get_db_optional)):
    """Toggle monitoring status (legacy endpoint)."""
    return await toggle_scheduled_monitoring(db)


@router.post("/settings/start-all-monitoring")
async def start_all_monitoring(db: Session | None = Depends(get_db_optional)):
    """Start monitoring on all platforms (email + mobile)."""
    if db is not None:
        try:
            # Start email monitoring
            crud.set_monitoring_enabled(db, True)
            
            # Start mobile monitoring
            crud.set_all_devices_monitoring(db, True)
            crud.queue_mobile_command(db, "start_monitoring", None)
            
            logger.info("All monitoring started (email + mobile)")
        except Exception as e:
            logger.error(f"Could not start all monitoring: {e}")
    
    return RedirectResponse("/settings", status_code=303)


@router.post("/settings/stop-all-monitoring")
async def stop_all_monitoring(db: Session | None = Depends(get_db_optional)):
    """Stop monitoring on all platforms (email + mobile)."""
    if db is not None:
        try:
            # Stop email monitoring
            crud.set_monitoring_enabled(db, False)
            
            # Stop mobile monitoring
            crud.set_all_devices_monitoring(db, False)
            crud.queue_mobile_command(db, "stop_monitoring", None)
            
            logger.info("All monitoring stopped (email + mobile)")
        except Exception as e:
            logger.error(f"Could not stop all monitoring: {e}")
    
    return RedirectResponse("/settings", status_code=303)


@router.post("/settings/toggle-mobile-monitoring")
async def toggle_mobile_monitoring(db: Session | None = Depends(get_db_optional)):
    """Toggle mobile monitoring on/off for all devices."""
    if db is not None:
        try:
            devices = crud.get_all_devices(db)
            # Check if any device has monitoring enabled
            any_enabled = any(getattr(d, 'monitoring_enabled', True) for d in devices)
            
            # Toggle: if any enabled, disable all; otherwise enable all
            new_state = not any_enabled
            crud.set_all_devices_monitoring(db, new_state)
            
            # Queue command for mobile apps
            command = "start_monitoring" if new_state else "stop_monitoring"
            crud.queue_mobile_command(db, command, None)
            
            logger.info(f"Mobile monitoring {'enabled' if new_state else 'disabled'} for all devices")
        except Exception as e:
            logger.error(f"Could not toggle mobile monitoring: {e}")
    
    return RedirectResponse("/settings", status_code=303)
