"""FastAPI application for ProjectX."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.models.schemas import HealthResponse, CheckResponse, PipelineResult
from src.services.gmail import GmailService
from src.services.twilio_sms import TwilioService
from src.services.pipeline import Pipeline
from src.agents.classifier import ClassifierAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline: Pipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global pipeline

    settings = get_settings()
    logger.info(f"Starting {settings.app_name}...")

    # Initialize services
    try:
        gmail = GmailService(
            credentials_path=settings.google_credentials_path,
            token_path=settings.google_token_path,
        )

        classifier = ClassifierAgent(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
        )

        twilio = TwilioService(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            from_number=settings.twilio_phone_number,
        )

        pipeline = Pipeline(
            gmail=gmail,
            classifier=classifier,
            twilio=twilio,
            alert_phone=settings.alert_phone_number,
        )

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Continue anyway - health check will work, but /check will fail

    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="ProjectX",
    description="Smart notification bridge - monitors email, detects urgency with AI, sends SMS alerts",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.app_name)


@app.post("/check", response_model=CheckResponse)
async def check_emails() -> CheckResponse:
    """Run the email check pipeline.

    Fetches unread emails, classifies urgency, and sends SMS for urgent ones.
    """
    global pipeline

    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized. Check server logs.",
        )

    try:
        logger.info("Starting email check pipeline...")
        result = await pipeline.run()

        return CheckResponse(
            success=True,
            message=f"Checked {result.emails_checked} emails, sent {result.alerts_sent} alerts",
            data=result,
        )

    except FileNotFoundError as e:
        logger.error(f"Credentials error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}",
        )


@app.post("/test-urgent")
async def test_urgent():
    """Test endpoint to simulate an urgent email classification and SMS.

    This bypasses Gmail and tests the classifier + SMS flow directly.
    """
    global pipeline

    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized. Check server logs.",
        )

    from src.models.schemas import Email

    # Simulate an urgent email
    test_email = Email(
        id="test-urgent-001",
        sender="Boss <boss@company.com>",
        subject="URGENT: Server is down - need immediate help!",
        snippet="Production server crashed. All hands on deck. Call me ASAP.",
    )

    try:
        # Classify the test email
        classification = await pipeline.classifier.classify(test_email)

        result = {
            "email": {
                "sender": test_email.sender,
                "subject": test_email.subject,
                "snippet": test_email.snippet,
            },
            "classification": {
                "urgency": classification.urgency.value,
                "reason": classification.reason,
            },
            "sms_sent": False,
            "sms_error": None,
        }

        # Try to send SMS if classified as urgent
        if classification.urgency.value == "URGENT":
            try:
                sent = pipeline.twilio.send_alert(test_email, pipeline.alert_phone)
                result["sms_sent"] = sent
                if not sent:
                    result["sms_error"] = "SMS send returned False - check Twilio config"
            except Exception as e:
                result["sms_error"] = str(e)

        return {
            "success": True,
            "message": "Test completed",
            "data": result,
        }

    except Exception as e:
        logger.error(f"Test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "app": "ProjectX",
        "description": "Smart notification bridge",
        "endpoints": {
            "health": "GET /health",
            "check": "POST /check",
            "test_urgent": "POST /test-urgent",
        },
    }
