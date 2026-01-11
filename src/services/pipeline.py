"""Pipeline orchestrator for email-to-SMS flow."""

import logging
from typing import Union

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

logger = logging.getLogger(__name__)

# Type alias for classifier (supports both old and new)
ClassifierType = Union[ClassifierAgent, EmailProcessingCrew]


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

    async def run(self, max_emails: int = 10) -> PipelineResult:
        """Execute full pipeline: fetch → classify → alert.

        Args:
            max_emails: Maximum number of emails to process.

        Returns:
            PipelineResult with all processing results.
        """
        result = PipelineResult()

        try:
            # Step 1: Fetch unread emails
            logger.info("Fetching unread emails...")
            emails = await self.gmail.get_unread_emails(max_results=max_emails)
            result.emails_checked = len(emails)

            if not emails:
                logger.info("No unread emails to process")
                return result

            # Step 2: Classify each email and alert if urgent
            for email in emails:
                alert_result = await self._process_email(email)
                result.results.append(alert_result)

                if alert_result.sms_sent:
                    result.alerts_sent += 1

            logger.info(
                f"Pipeline complete: {result.emails_checked} checked, "
                f"{result.alerts_sent} alerts sent"
            )
            return result

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            raise

    async def _process_email(self, email: Email) -> AlertResult:
        """Process a single email through classification and alerting.

        Args:
            email: Email to process.

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
            
        logger.info(
            f"Classification: {classification.urgency.value} - {classification.reason}"
        )

        # Send SMS if urgent
        sms_sent = False
        if classification.urgency == Urgency.URGENT:
            logger.info("Email is URGENT - sending SMS alert")
            sms_sent = self.twilio.send_alert(email, self.alert_phone)

            if sms_sent:
                logger.info("✅ SMS alert sent successfully")
            else:
                logger.warning("⚠️ Failed to send SMS alert")
        else:
            logger.info("Email is not urgent - no alert needed")

        return AlertResult(
            email_id=email.id,
            sender=email.sender,
            subject=email.subject,
            urgency=classification.urgency,
            reason=classification.reason,
            sms_sent=sms_sent,
        )
