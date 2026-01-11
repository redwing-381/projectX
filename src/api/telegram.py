"""Telegram webhook API routes."""

import logging
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from src.config import get_settings
from src.db.database import get_db
from src.db import crud
from src.services.telegram import TelegramService
from src.services.twilio_sms import TwilioService
from src.agents.telegram_crew import TelegramProcessingCrew

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Get settings
settings = get_settings()

# Initialize services
telegram_service = TelegramService(settings.telegram_bot_token)
telegram_crew = TelegramProcessingCrew(verbose=False)


@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming Telegram webhook updates.
    
    This endpoint receives messages forwarded to the bot and processes
    them through the classification pipeline.
    """
    try:
        update = await request.json()
        logger.info(f"Received Telegram update: {update.get('update_id')}")
        
        # Parse the update into TelegramMessage
        message = telegram_service.parse_update(update)
        
        if not message:
            logger.debug("No message in update, skipping")
            return {"ok": True, "message": "No message to process"}
        
        # Generate unique ID for this message
        message_id = f"tg_{message.id}_{int(datetime.utcnow().timestamp())}"
        
        # Check if already processed
        existing = crud.get_alert_by_email_id(db, message_id)
        if existing:
            logger.info(f"Message {message_id} already processed")
            return {"ok": True, "message": "Already processed"}
        
        # Get VIP senders and keywords from database
        vip_senders = [v.email_or_domain for v in crud.get_vip_senders(db)]
        keywords = [k.keyword for k in crud.get_keywords(db)]
        
        # Process through classification pipeline
        classification = telegram_crew.process_message(
            message=message,
            vip_senders=vip_senders,
            keywords=keywords,
        )
        
        logger.info(f"Classification: {classification.urgency} - {classification.reason}")
        
        # Send SMS if urgent
        sms_sent = False
        if classification.urgency == "URGENT" and classification.sms_message:
            try:
                twilio = TwilioService()
                twilio.send_sms(
                    to=settings.alert_phone_number,
                    message=classification.sms_message,
                )
                sms_sent = True
                logger.info(f"SMS sent for urgent Telegram message")
                
                # Send confirmation back to Telegram
                telegram_service.send_message(
                    chat_id=update.get("message", {}).get("chat", {}).get("id"),
                    text=f"✅ Alert sent! Classified as URGENT: {classification.reason}",
                )
            except Exception as e:
                logger.error(f"Failed to send SMS: {e}")
        
        # Save to alert history
        crud.create_alert(
            db=db,
            email_id=message_id,
            sender=message.sender or message.sender_username or "Unknown",
            subject=f"Telegram: {message.sender_username or 'message'}",
            snippet=message.text[:500] if message.text else "",
            urgency=classification.urgency,
            reason=classification.reason,
            sms_sent=sms_sent,
            source="telegram",
        )
        
        return {
            "ok": True,
            "urgency": classification.urgency,
            "reason": classification.reason,
            "sms_sent": sms_sent,
        }
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        # Return 200 to prevent Telegram from retrying
        return {"ok": False, "error": str(e)}


@router.get("/set-webhook")
async def set_webhook(url: str = None):
    """Set the Telegram webhook URL.
    
    Args:
        url: The webhook URL. If not provided, uses the Railway URL.
    """
    if not url:
        # Use Railway URL if available
        railway_url = settings.railway_public_url
        if railway_url:
            url = f"{railway_url}/telegram/webhook"
        else:
            raise HTTPException(
                status_code=400,
                detail="No URL provided and RAILWAY_PUBLIC_URL not set"
            )
    
    success = telegram_service.set_webhook(url)
    
    if success:
        return {"ok": True, "webhook_url": url}
    else:
        raise HTTPException(status_code=500, detail="Failed to set webhook")


@router.get("/webhook-info")
async def get_webhook_info():
    """Get current webhook information from Telegram."""
    info = telegram_service.get_webhook_info()
    return info or {"error": "Failed to get webhook info"}
