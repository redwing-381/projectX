"""Mobile notification agent for classifying app notifications."""

import json
import logging
from dataclasses import dataclass
from typing import Optional, List

from openai import OpenAI

from src.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class MobileNotification:
    """Notification from mobile app."""
    id: str
    app: str
    sender: str
    text: str
    timestamp: int


@dataclass
class Classification:
    """Classification result."""
    urgency: str  # "URGENT" or "NOT_URGENT"
    reason: str
    sms_message: Optional[str] = None


CLASSIFICATION_PROMPT = """You are a message urgency classifier for mobile app notifications.

Analyze this {app_name} message and determine if it requires immediate attention.

URGENT indicators:
- Time-sensitive requests (now, ASAP, urgent, emergency)
- Important people (family, boss, close friends)
- Health or safety concerns
- Financial matters requiring action
- Work/school deadlines
- Direct questions requiring immediate response

NOT_URGENT indicators:
- Group chat casual conversation
- Memes, jokes, forwards
- Marketing/promotional messages
- General updates that can wait
- Automated notifications
- Social media activity updates

Message:
From: {sender}
Content: {text}

Respond with ONLY a JSON object in this exact format:
{{"urgency": "URGENT" or "NOT_URGENT", "reason": "one line explanation"}}
"""


class MobileNotificationAgent:
    """Agent for classifying mobile app notifications.
    
    Classification pipeline:
    1. Check VIP senders (instant URGENT)
    2. Check urgent keywords (instant URGENT)
    3. Use LLM for contextual classification
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize the agent with LLM configuration."""
        settings = get_settings()
        self.client = OpenAI(
            api_key=api_key or settings.llm_api_key,
            base_url=base_url or settings.llm_base_url,
        )
        self.model = model or settings.llm_model

    def classify(
        self,
        notification: MobileNotification,
        vip_senders: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
    ) -> Classification:
        """Classify notification urgency.
        
        Args:
            notification: The mobile notification to classify.
            vip_senders: List of VIP sender names/identifiers.
            keywords: List of urgent keywords.
        
        Returns:
            Classification with urgency and reason.
        """
        vip_senders = vip_senders or []
        keywords = keywords or []
        
        # Step 1: Check VIP senders (fast path)
        sender_lower = notification.sender.lower()
        for vip in vip_senders:
            if vip.lower() in sender_lower:
                logger.info(f"VIP sender match: {vip}")
                return Classification(
                    urgency="URGENT",
                    reason=f"VIP sender: {vip}",
                    sms_message=self.format_sms(notification),
                )
        
        # Step 2: Check keywords (fast path)
        text_lower = notification.text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                logger.info(f"Keyword match: {keyword}")
                return Classification(
                    urgency="URGENT",
                    reason=f"Contains urgent keyword: {keyword}",
                    sms_message=self.format_sms(notification),
                )
        
        # Step 3: Use LLM for classification
        try:
            return self._classify_with_llm(notification)
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return self._fallback_classify(notification)

    def _classify_with_llm(self, notification: MobileNotification) -> Classification:
        """Classify using LLM."""
        prompt = CLASSIFICATION_PROMPT.format(
            app_name=notification.app,
            sender=notification.sender,
            text=notification.text,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a message urgency classifier. Respond only with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=100,
        )

        result_text = response.choices[0].message.content.strip()
        logger.debug(f"LLM response: {result_text}")

        # Parse JSON response
        result = json.loads(result_text)
        urgency = result.get("urgency", "NOT_URGENT")
        reason = result.get("reason", "No reason provided")

        # Ensure valid urgency value
        if urgency not in ("URGENT", "NOT_URGENT"):
            urgency = "NOT_URGENT"

        sms_message = self.format_sms(notification) if urgency == "URGENT" else None

        return Classification(
            urgency=urgency,
            reason=reason,
            sms_message=sms_message,
        )

    def _fallback_classify(self, notification: MobileNotification) -> Classification:
        """Fallback classification when LLM fails."""
        text_lower = notification.text.lower()
        
        # Simple keyword-based fallback
        urgent_words = ["urgent", "emergency", "asap", "help", "important", "now", "immediately", "call me"]
        
        for word in urgent_words:
            if word in text_lower:
                return Classification(
                    urgency="URGENT",
                    reason=f"Contains urgent word: {word} (fallback)",
                    sms_message=self.format_sms(notification),
                )
        
        return Classification(
            urgency="NOT_URGENT",
            reason="No urgent indicators found (fallback)",
            sms_message=None,
        )

    def format_sms(self, notification: MobileNotification) -> str:
        """Format notification as SMS with app prefix.
        
        Format: "{APP}: {sender} - {text[:100]}"
        Max length: 160 characters
        """
        app_prefix = notification.app.upper()
        sender = notification.sender
        text = notification.text
        
        # Build SMS with truncation
        prefix = f"{app_prefix}: {sender} - "
        max_text_len = 160 - len(prefix)
        
        if max_text_len <= 0:
            # Prefix too long, truncate sender
            prefix = f"{app_prefix}: "
            max_text_len = 160 - len(prefix) - 3
            text = text[:max_text_len] + "..."
        elif len(text) > max_text_len:
            text = text[:max_text_len - 3] + "..."
        
        sms = f"{prefix}{text}"
        
        # Final safety check
        if len(sms) > 160:
            sms = sms[:157] + "..."
        
        return sms
