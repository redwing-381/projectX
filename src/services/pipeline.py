"""Pipeline orchestrator for email-to-SMS flow."""

import logging
from typing import Union, Optional

from src.models.schemas import (
    Email,
    Urgency,
    AlertResult,
    PipelineResult,
)
from src.services.gmail import GmailService
from src.services.twilio_sms import TwilioService
from src.agents.classifier import ClassifierAgent
from src.agents.crew import EmailProcessingCrew
from src.db import crud

logger = logging.getLogger(__name__)

# Type alias for classifier (supports both old and new)
ClassifierType = Union[ClassifierAgent, EmailProcessingCrew]


def is_already_processed(email_id: str) -> bool:
    """Check if email has already been processed.
    
    Args:
        email_id: Email ID to check
        
    Returns:
        True if already processed, False otherwise
    """
    try:
        from src.db.database import get_db_session, engine
        
        # Check if database is available
        if engine is None:
            logger.warning("Database not available for duplicate check")
            return False
        
        with get_db_session() as db:
            existing = crud.get_alert_by_email_id(db, email_id)
            if existing:
                logger.debug(f"Email {email_id} already processed (found in DB)")
                return True
            return False
    except Exception as e:
        logger.warning(f"Duplicate check failed (treating as new): {e}")
        return False


# In-memory cache for recently processed emails (backup for DB failures)
_processed_cache: set = set()
_cache_max_size = 1000


def mark_as_processed(email_id: str) -> None:
    """Mark email as processed in memory cache."""
    global _processed_cache
    _processed_cache.add(email_id)
    # Trim cache if too large
    if len(_processed_cache) > _cache_max_size:
        # Remove oldest entries (convert to list, slice, convert back)
        _processed_cache = set(list(_processed_cache)[-500:])


def is_in_cache(email_id: str) -> bool:
    """Check if email is in the in-memory processed cache."""
    return email_id in _processed_cache


def save_alert_to_db(email: Email, classification, sms_sent: bool, demo_mode: bool = False) -> None:
    """Save alert result to database.
    
    Args:
        email: Email that was processed
        classification: Classification result
        sms_sent: Whether SMS was sent
        demo_mode: If True, skip database save (demo isolation)
    """
    # Always mark in cache (even in demo mode for safety)
    mark_as_processed(email.id)
    
    # Skip DB save in demo mode
    if demo_mode:
        logger.debug(f"Demo mode: skipping DB save for {email.id}")
        return
        
    try:
        from src.db.database import get_db_session, engine
        
        if engine is None:
            logger.warning(f"Database not available, email {email.id} only cached in memory")
            return
        
        with get_db_session() as db:
            # Check if already exists
            existing = crud.get_alert_by_email_id(db, email.id)
            if existing:
                logger.debug(f"Alert already exists for email {email.id}")
                return
            
            # Handle both enum and string urgency values
            urgency_value = classification.urgency
            if hasattr(urgency_value, 'value'):
                urgency_value = urgency_value.value
            
            crud.create_alert(
                db=db,
                email_id=email.id,
                sender=email.sender,
                subject=email.subject,
                snippet=email.snippet,
                urgency=urgency_value,
                reason=classification.reason,
                sms_sent=sms_sent,
            )
            logger.debug(f"Saved alert to database: {email.id}")
    except Exception as e:
        logger.warning(f"Could not save to database: {e}")


class Pipeline:
    """Orchestrates the email check → classify → alert pipeline."""

    def __init__(
        self,
        gmail: GmailService,
        classifier: ClassifierType,
        twilio: TwilioService,
        alert_phone: str,
    ):
        """Initialize pipeline with all services.

        Args:
            gmail: Gmail service for fetching emails.
            classifier: Classifier agent or CrewAI crew for urgency detection.
            twilio: Twilio service for sending SMS.
            alert_phone: Phone number to send alerts to.
        """
        self.gmail = gmail
        self.classifier = classifier
        self.twilio = twilio
        self.alert_phone = alert_phone
        self._use_crew = isinstance(classifier, EmailProcessingCrew)

    def _check_sms_restrictions(self) -> Optional[str]:
        """Check if SMS sending is restricted by quiet hours or rate limits.
        
        Returns:
            Reason string if blocked, None if allowed
        """
        try:
            from src.db.database import get_db_session
            from src.db import crud
            
            with get_db_session() as db:
                # Check quiet hours
                if crud.is_quiet_hours(db):
                    quiet = crud.get_quiet_hours(db)
                    return f"Quiet hours active ({quiet['start']}:00 - {quiet['end']}:00)"
                
                # Check rate limit
                if crud.is_rate_limited(db):
                    limit = crud.get_rate_limit(db)
                    return f"Rate limit reached ({limit['max_per_hour']}/hour)"
                
            return None
        except Exception as e:
            logger.debug(f"Could not check SMS restrictions: {e}")
            return None

    async def run(self, max_emails: int = 10, demo_mode: bool = False) -> PipelineResult:
        """Execute full pipeline: fetch → classify → alert.

        Args:
            max_emails: Maximum number of emails to process.
            demo_mode: If True, use sample emails and skip real SMS/DB.

        Returns:
            PipelineResult with all processing results.
        """
        result = PipelineResult()

        try:
            # Step 1: Fetch emails (sample emails in demo mode)
            if demo_mode:
                from src.services.demo import get_sample_emails
                logger.info("Demo mode: using sample emails")
                emails = get_sample_emails()[:max_emails]
            else:
                logger.info("Fetching unread emails...")
                emails = await self.gmail.get_unread_emails(max_results=max_emails)
            
            result.emails_checked = len(emails)

            if not emails:
                logger.info("No emails to process")
                return result

            # Step 2: Filter out already-processed emails (skip in demo mode)
            if not demo_mode:
                new_emails = []
                for email in emails:
                    # Check both database AND in-memory cache
                    if is_already_processed(email.id) or is_in_cache(email.id):
                        logger.debug(f"Skipping already processed email: {email.id}")
                    else:
                        new_emails.append(email)
                
                skipped = len(emails) - len(new_emails)
                if skipped > 0:
                    logger.info(f"Skipped {skipped} already-processed emails")
                emails = new_emails

            if not emails:
                logger.info("No new emails to process")
                return result

            # Step 3: Classify each email and alert if urgent
            for email in emails:
                alert_result = await self._process_email(email, demo_mode=demo_mode)
                result.results.append(alert_result)

                if alert_result.sms_sent:
                    result.alerts_sent += 1

            logger.info(
                f"Pipeline complete: {result.emails_checked} checked, "
                f"{result.alerts_sent} alerts sent"
                f"{' (demo mode)' if demo_mode else ''}"
            )
            return result

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            raise

    async def _process_email(self, email: Email, demo_mode: bool = False) -> AlertResult:
        """Process a single email through classification and alerting.

        Args:
            email: Email to process.
            demo_mode: If True, simulate SMS instead of sending.

        Returns:
            AlertResult with processing outcome.
        """
        logger.info(f"Processing email from {email.sender}: {email.subject[:50]}...")

        # Classify urgency using either CrewAI or direct classifier
        if self._use_crew:
            logger.debug("Using CrewAI crew for classification")
            classification = self.classifier.process_email(email)
        else:
            logger.debug("Using direct classifier for classification")
            classification = await self.classifier.classify(email)
        
        # Handle both enum and string urgency values
        urgency_value = classification.urgency
        if hasattr(urgency_value, 'value'):
            urgency_value = urgency_value.value
            
        logger.info(
            f"Classification: {urgency_value} - {classification.reason}"
        )

        # Send SMS if urgent (simulate in demo mode)
        sms_sent = False
        sms_blocked_reason = None
        is_urgent = urgency_value == "URGENT" or urgency_value == Urgency.URGENT
        if is_urgent:
            if demo_mode:
                logger.info("Demo mode: simulating SMS alert (not actually sent)")
                sms_sent = True  # Simulate success
            else:
                # Check quiet hours and rate limits
                sms_blocked_reason = self._check_sms_restrictions()
                
                if sms_blocked_reason:
                    logger.info(f"SMS blocked: {sms_blocked_reason}")
                    sms_sent = False
                else:
                    logger.info("Email is URGENT - sending SMS alert")
                    sms_sent = self.twilio.send_alert(email, self.alert_phone)

                    if sms_sent:
                        logger.info("SMS alert sent successfully")
                    else:
                        logger.warning("Failed to send SMS alert")
        else:
            logger.info("Email is not urgent - no alert needed")

        # Save to database (skip in demo mode)
        save_alert_to_db(email, classification, sms_sent, demo_mode=demo_mode)
        
        # Convert urgency to enum for AlertResult
        urgency_enum = Urgency.URGENT if urgency_value == "URGENT" else Urgency.NOT_URGENT

        return AlertResult(
            email_id=email.id,
            sender=email.sender,
            subject=email.subject,
            urgency=urgency_enum,
            reason=classification.reason,
            sms_sent=sms_sent,
        )
