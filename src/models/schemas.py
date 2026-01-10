"""Pydantic models for ProjectX."""

from enum import Enum
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


class Classification(BaseModel):
    """AI classification result."""

    urgency: Urgency = Field(..., description="Urgency level")
    reason: str = Field(..., min_length=1, description="One-line reason for classification")


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
