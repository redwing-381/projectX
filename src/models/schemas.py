"""Pydantic models for ProjectX."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Urgency(str, Enum):
    """Email urgency classification."""

    URGENT = "URGENT"
    NOT_URGENT = "NOT_URGENT"


class Email(BaseModel):
    """Extracted email data."""

    id: str = Field(..., description="Gmail message ID")
    sender: str = Field(..., description="Sender email address or name")
    subject: str = Field(..., description="Email subject line")
    snippet: str = Field(..., description="Email body snippet/preview")


class TelegramMessage(BaseModel):
    """Telegram message data."""

    id: str = Field(..., description="Telegram message ID")
    sender: str = Field(..., description="Sender name")
    sender_username: Optional[str] = Field(None, description="Sender @username if available")
    text: str = Field(..., description="Message text content")
    timestamp: datetime = Field(..., description="When message was sent")
    is_forwarded: bool = Field(False, description="Whether this was forwarded")
    original_sender: Optional[str] = Field(None, description="Original sender if forwarded")
    chat_id: str = Field(..., description="Chat ID for replies")


class Classification(BaseModel):
    """AI classification result."""

    urgency: str = Field(..., description="Urgency level: URGENT or NOT_URGENT")
    reason: str = Field(..., min_length=1, description="One-line reason for classification")
    sms_message: Optional[str] = Field(None, description="SMS message if urgent")


class AlertResult(BaseModel):
    """Result of processing a single email."""

    email_id: str
    sender: str
    subject: str
    urgency: Urgency
    reason: str
    sms_sent: bool = False


class PipelineResult(BaseModel):
    """Result of running the full pipeline."""

    emails_checked: int = 0
    alerts_sent: int = 0
    results: list[AlertResult] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    app_name: str = "ProjectX"


class CheckResponse(BaseModel):
    """Response from /check endpoint."""

    success: bool
    message: str
    data: PipelineResult | None = None


# =============================================================================
# Mobile App API Models
# =============================================================================

class NotificationPayload(BaseModel):
    """Individual notification from mobile app."""

    id: str = Field(..., description="Unique notification ID")
    app: str = Field(..., description="Source app name (e.g., WhatsApp)")
    sender: str = Field(..., description="Sender name or identifier")
    text: str = Field(..., description="Notification text content")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")


class NotificationBatchRequest(BaseModel):
    """Batch of notifications from mobile app."""

    device_id: str = Field(..., description="Unique device identifier")
    notifications: list[NotificationPayload] = Field(
        default_factory=list, description="List of notifications to process"
    )


class NotificationBatchResponse(BaseModel):
    """Response after processing notifications."""

    success: bool = Field(..., description="Whether processing succeeded")
    processed: int = Field(0, description="Number of notifications processed")
    urgent_count: int = Field(0, description="Number of urgent notifications")
    message: str = Field("", description="Status message")
