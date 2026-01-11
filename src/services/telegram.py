"""Telegram bot service for receiving and sending messages."""

import logging
from datetime import datetime
from typing import Optional

import httpx

from src.models.schemas import TelegramMessage

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


class TelegramService:
    """Service for Telegram bot operations."""

    def __init__(self, bot_token: str):
        """Initialize with bot token.

        Args:
            bot_token: Telegram bot token from @BotFather.
        """
        self.bot_token = bot_token
        self.api_base = f"{TELEGRAM_API_BASE}{bot_token}"

    def set_webhook(self, webhook_url: str) -> bool:
        """Register webhook URL with Telegram API (sync version).

        Args:
            webhook_url: Full URL for webhook endpoint.

        Returns:
            True if webhook was set successfully.
        """
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.api_base}/setWebhook",
                    json={"url": webhook_url},
                )
                result = response.json()
                
                if result.get("ok"):
                    logger.info(f"Telegram webhook set to: {webhook_url}")
                    return True
                else:
                    logger.error(f"Failed to set webhook: {result}")
                    return False
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False

    def delete_webhook(self) -> bool:
        """Remove webhook from Telegram API (sync version).

        Returns:
            True if webhook was deleted successfully.
        """
        try:
            with httpx.Client() as client:
                response = client.post(f"{self.api_base}/deleteWebhook")
                result = response.json()
                return result.get("ok", False)
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False

    def parse_update(self, update: dict) -> Optional[TelegramMessage]:
        """Parse Telegram webhook update into TelegramMessage.

        Args:
            update: Raw webhook update from Telegram.

        Returns:
            TelegramMessage if valid text message, None otherwise.
        """
        try:
            message = update.get("message")
            if not message:
                logger.debug("Update has no message field")
                return None

            # Only handle text messages
            text = message.get("text")
            if not text:
                logger.debug("Message has no text (might be media)")
                return None

            # Extract sender info
            from_user = message.get("from", {})
            sender_name = from_user.get("first_name", "Unknown")
            if from_user.get("last_name"):
                sender_name += f" {from_user['last_name']}"
            
            sender_username = from_user.get("username")

            # Check if forwarded
            is_forwarded = False
            original_sender = None
            
            if "forward_from" in message:
                is_forwarded = True
                fwd_user = message["forward_from"]
                original_sender = fwd_user.get("first_name", "Unknown")
                if fwd_user.get("last_name"):
                    original_sender += f" {fwd_user['last_name']}"
                if fwd_user.get("username"):
                    original_sender += f" (@{fwd_user['username']})"
            elif "forward_sender_name" in message:
                is_forwarded = True
                original_sender = message["forward_sender_name"]

            # Parse timestamp
            timestamp = datetime.fromtimestamp(message.get("date", 0))

            return TelegramMessage(
                id=str(message.get("message_id", "")),
                sender=sender_name,
                sender_username=sender_username,
                text=text,
                timestamp=timestamp,
                is_forwarded=is_forwarded,
                original_sender=original_sender,
                chat_id=str(message.get("chat", {}).get("id", "")),
            )

        except Exception as e:
            logger.error(f"Error parsing Telegram update: {e}")
            return None

    def send_message(self, chat_id: str, text: str) -> bool:
        """Send a message to a chat (sync version).

        Args:
            chat_id: Telegram chat ID.
            text: Message text to send.

        Returns:
            True if message was sent successfully.
        """
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.api_base}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                    },
                )
                result = response.json()
                return result.get("ok", False)
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def get_webhook_info(self) -> dict:
        """Get current webhook info (sync version).

        Returns:
            Webhook info from Telegram API.
        """
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.api_base}/getWebhookInfo")
                return response.json()
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            return {}
