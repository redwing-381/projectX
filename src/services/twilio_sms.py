"""Twilio SMS service for sending alerts."""

import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from src.models.schemas import Email

logger = logging.getLogger(__name__)

# Maximum SMS length for single message
MAX_SMS_LENGTH = 160


class TwilioService:
    """Service for sending SMS alerts via Twilio."""

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
    ):
        """Initialize Twilio client.

        Args:
            account_sid: Twilio account SID.
            auth_token: Twilio auth token.
            from_number: Twilio phone number to send from.
        """
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def format_alert(self, email: Email) -> str:
        """Format email into SMS message (max 160 chars).

        Args:
            email: Email to format.

        Returns:
            Formatted SMS message.
        """
        # Extract sender name (before email address if present)
        sender = email.sender
        if "<" in sender:
            sender = sender.split("<")[0].strip()
        if len(sender) > 30:
            sender = sender[:27] + "..."

        # Truncate subject if needed
        subject = email.subject
        prefix = f"📧 URGENT from {sender}: "
        max_subject_len = MAX_SMS_LENGTH - len(prefix)

        if len(subject) > max_subject_len:
            subject = subject[: max_subject_len - 3] + "..."

        message = f"{prefix}{subject}"

        # Final safety check
        if len(message) > MAX_SMS_LENGTH:
            message = message[: MAX_SMS_LENGTH - 3] + "..."

        return message

    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS message.

        Args:
            to_number: Recipient phone number.
            message: Message to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        try:
            # Ensure message is within limit
            if len(message) > MAX_SMS_LENGTH:
                message = message[: MAX_SMS_LENGTH - 3] + "..."
                logger.warning("Message truncated to fit SMS limit")

            result = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number,
            )

            logger.info(f"SMS sent successfully. SID: {result.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

    def send_alert(self, email: Email, to_number: str) -> bool:
        """Format and send email alert as SMS.

        Args:
            email: Email to alert about.
            to_number: Recipient phone number.

        Returns:
            True if sent successfully, False otherwise.
        """
        message = self.format_alert(email)
        logger.info(f"Sending alert: {message}")
        return self.send_sms(to_number, message)
