"""Mobile app API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.api.deps import get_db, verify_api_key
from src.db import crud
from src.config import get_settings
from src.models.schemas import (
    NotificationPayload,
    NotificationBatchRequest,
    NotificationBatchResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class CommandResponse(BaseModel):
    """Response for command polling."""
    commands: list
    monitoring_enabled: bool


class CommandAckRequest(BaseModel):
    """Request to acknowledge command execution."""
    command_id: int


@router.post("/api/notifications", response_model=NotificationBatchResponse)
async def receive_notifications(
    request: NotificationBatchRequest,
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Receive notifications from Android app, classify urgency, send SMS for urgent ones.
    
    This endpoint:
    1. Receives a batch of notifications from the Android app
    2. Registers/updates the device
    3. Checks if monitoring is enabled for this device
    4. Classifies each notification for urgency using the MobileNotificationAgent
    5. Sends SMS alerts for urgent notifications
    6. Saves all notifications to the database
    """
    from src.agents.mobile_notification_agent import MobileNotificationAgent, MobileNotification
    from src.main import pipeline
    
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    processed = 0
    urgent_count = 0
    
    # Register/update device and get VIP senders and keywords
    try:
        device = crud.get_or_create_device(db, request.device_id)
        
        # Check if monitoring is enabled for this device
        if hasattr(device, 'monitoring_enabled') and not device.monitoring_enabled:
            logger.info(f"Monitoring disabled for device {request.device_id}, skipping processing")
            return NotificationBatchResponse(
                success=True,
                processed=0,
                urgent_count=0,
                message="Monitoring disabled for this device",
            )
        
        vip_list = crud.get_vip_senders(db)
        vip_senders = [v.email_or_domain for v in vip_list]
        kw_list = crud.get_keywords(db)
        keywords = [k.keyword for k in kw_list]
    except Exception as e:
        logger.warning(f"Could not fetch VIP/keywords: {e}")
        vip_senders = []
        keywords = []
    
    # Initialize agent
    agent = MobileNotificationAgent()
    
    for notif in request.notifications:
        try:
            # Create notification object
            mobile_notif = MobileNotification(
                id=notif.id,
                app=notif.app,
                sender=notif.sender,
                text=notif.text,
                timestamp=notif.timestamp,
            )
            
            # Classify
            classification = agent.classify(mobile_notif, vip_senders, keywords)
            
            # Generate unique email_id for database
            email_id = f"mobile:{notif.id}"
            
            # Determine source format (android:appname)
            app_lower = notif.app.lower().replace(" ", "")
            source = f"android:{app_lower}"
            
            # Save to database (check for duplicate)
            try:
                existing = crud.get_alert_by_email_id(db, email_id)
                if not existing:
                    crud.create_alert(
                        db=db,
                        email_id=email_id,
                        sender=notif.sender,
                        subject=f"{notif.app} notification",
                        snippet=notif.text[:500] if notif.text else "",
                        urgency=classification.urgency,
                        reason=classification.reason,
                        sms_sent=False,
                        source=source,
                    )
            except Exception as db_error:
                logger.warning(f"Failed to save notification: {db_error}")
            
            # Send SMS if urgent
            if classification.urgency == "URGENT":
                urgent_count += 1
                sms_text = classification.sms_message or f"{notif.app}: {notif.sender} - {notif.text[:100]}"
                
                try:
                    settings = get_settings()
                    sent = pipeline.twilio.send_sms(
                        to_number=settings.alert_phone_number,
                        message=sms_text,
                    )
                    if sent:
                        logger.info(f"SMS sent for urgent {notif.app} notification from {notif.sender}")
                        # Update database record
                        try:
                            alert = crud.get_alert_by_email_id(db, email_id)
                            if alert:
                                alert.sms_sent = True
                                db.commit()
                        except Exception:
                            pass
                except Exception as sms_error:
                    logger.error(f"Failed to send SMS: {sms_error}")
            
            processed += 1
            
        except Exception as e:
            logger.error(f"Error processing notification {notif.id}: {e}")
    
    # Update device sync stats
    if processed > 0:
        try:
            crud.update_device_sync(db, request.device_id, processed)
        except Exception as e:
            logger.warning(f"Could not update device sync: {e}")
    
    message = f"Processed {processed} notifications"
    if urgent_count > 0:
        message += f", {urgent_count} urgent (SMS sent)"
    
    logger.info(f"Mobile batch: {message} from device {request.device_id}")
    
    return NotificationBatchResponse(
        success=True,
        processed=processed,
        urgent_count=urgent_count,
        message=message,
    )


@router.get("/api/mobile/commands/{device_id}")
async def get_device_commands(
    device_id: str,
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Poll for pending commands for this device.
    
    Mobile app should call this periodically to check for remote commands.
    Returns list of pending commands and current monitoring status.
    """
    # Get pending commands
    commands = crud.get_pending_commands(db, device_id)
    
    # Get device monitoring status
    device = crud.get_or_create_device(db, device_id)
    monitoring_enabled = getattr(device, 'monitoring_enabled', True)
    
    return {
        "commands": [
            {
                "id": cmd.id,
                "command": cmd.command,
                "payload": cmd.payload,
                "created_at": cmd.created_at.isoformat(),
            }
            for cmd in commands
        ],
        "monitoring_enabled": monitoring_enabled,
    }


@router.post("/api/mobile/commands/{device_id}/ack")
async def acknowledge_command(
    device_id: str,
    request: CommandAckRequest,
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Acknowledge that a command has been executed by the mobile app."""
    success = crud.mark_command_executed(db, request.command_id)
    
    if success:
        logger.info(f"Command {request.command_id} acknowledged by device {device_id}")
        return {"success": True, "message": "Command acknowledged"}
    else:
        return {"success": False, "message": "Command not found"}


@router.post("/api/mobile/control/start")
async def start_mobile_monitoring(
    device_id: Optional[str] = None,
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Start monitoring on mobile device(s).
    
    If device_id is provided, starts monitoring on that device only.
    Otherwise, starts monitoring on all devices.
    """
    if device_id:
        # Single device
        device = crud.set_device_monitoring(db, device_id, True)
        if device:
            crud.queue_mobile_command(db, "start_monitoring", device_id)
            return {"success": True, "message": f"Monitoring started for device {device_id}"}
        return {"success": False, "message": "Device not found"}
    else:
        # All devices
        count = crud.set_all_devices_monitoring(db, True)
        crud.queue_mobile_command(db, "start_monitoring", None)  # Broadcast
        return {"success": True, "message": f"Monitoring started for {count} devices"}


@router.post("/api/mobile/control/stop")
async def stop_mobile_monitoring(
    device_id: Optional[str] = None,
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Stop monitoring on mobile device(s).
    
    If device_id is provided, stops monitoring on that device only.
    Otherwise, stops monitoring on all devices.
    """
    if device_id:
        # Single device
        device = crud.set_device_monitoring(db, device_id, False)
        if device:
            crud.queue_mobile_command(db, "stop_monitoring", device_id)
            return {"success": True, "message": f"Monitoring stopped for device {device_id}"}
        return {"success": False, "message": "Device not found"}
    else:
        # All devices
        count = crud.set_all_devices_monitoring(db, False)
        crud.queue_mobile_command(db, "stop_monitoring", None)  # Broadcast
        return {"success": True, "message": f"Monitoring stopped for {count} devices"}


@router.get("/api/mobile/status")
async def get_mobile_status(
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get status of all mobile devices and their monitoring state."""
    devices = crud.get_all_devices(db)
    
    return {
        "devices": [
            {
                "device_id": d.device_id,
                "device_name": d.device_name,
                "monitoring_enabled": getattr(d, 'monitoring_enabled', True),
                "notification_count": d.notification_count,
                "last_sync_at": d.last_sync_at.isoformat() if d.last_sync_at else None,
            }
            for d in devices
        ],
        "total_devices": len(devices),
        "enabled_count": sum(1 for d in devices if getattr(d, 'monitoring_enabled', True)),
    }
