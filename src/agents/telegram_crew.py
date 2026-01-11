"""Telegram message processing crew using CrewAI."""

import json
import logging
from typing import Optional

from crewai import LLM

from src.config import get_settings
from src.models.schemas import TelegramMessage, Classification
from src.agents.definitions import create_telegram_monitor_agent, create_alert_agent
from src.agents.tasks import create_telegram_classifier_task, create_telegram_alert_task

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


class TelegramProcessingCrew:
    """Crew for processing Telegram messages through classification pipeline."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the Telegram processing crew.
        
        Args:
            verbose: Whether to enable verbose logging for agents.
        """
        self.verbose = verbose
        self._llm: Optional[LLM] = None
        
    @property
    def llm(self) -> LLM:
        """Lazy-load the LLM instance."""
        if self._llm is None:
            self._llm = LLM(
                model=settings.llm_model,
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key,
            )
        return self._llm
    
    def process_message(
        self,
        message: TelegramMessage,
        vip_senders: list[str] | None = None,
        keywords: list[str] | None = None,
    ) -> Classification:
        """Process a Telegram message through the classification pipeline.
        
        Args:
            message: The Telegram message to process.
            vip_senders: List of VIP sender usernames/names.
            keywords: List of urgent keywords.
        
        Returns:
            Classification result with urgency and reason.
        """
        vip_senders = vip_senders or []
        keywords = keywords or []
        
        # Check VIP senders first (fast path)
        sender_lower = (message.sender or "").lower()
        username_lower = (message.sender_username or "").lower()
        
        for vip in vip_senders:
            vip_lower = vip.lower()
            if vip_lower in sender_lower or vip_lower == username_lower:
                logger.info(f"VIP sender match: {vip}")
                return Classification(
                    urgency="URGENT",
                    reason=f"VIP sender: {vip}",
                    sms_message=self._format_sms(message),
                )
        
        # Check keywords (fast path)
        text_lower = (message.text or "").lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                logger.info(f"Keyword match: {keyword}")
                return Classification(
                    urgency="URGENT",
                    reason=f"Contains urgent keyword: {keyword}",
                    sms_message=self._format_sms(message),
                )
        
        # Use LLM for classification
        try:
            return self._classify_with_llm(message)
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return self._fallback_classify(message)
    
    def _classify_with_llm(self, message: TelegramMessage) -> Classification:
        """Classify message using CrewAI agents."""
        try:
            # Create agents
            monitor_agent = create_telegram_monitor_agent(self.llm, self.verbose)
            alert_agent = create_alert_agent(self.llm, self.verbose)
            
            # Create and execute classification task
            classifier_task = create_telegram_classifier_task(monitor_agent, message)
            classification_result = classifier_task.execute_sync()
            
            # Parse classification result
            result_text = str(classification_result)
            classification_data = self._parse_json_response(result_text)
            
            urgency = classification_data.get("urgency", "NOT_URGENT")
            reason = classification_data.get("reason", "No reason provided")
            
            # If urgent, format SMS
            sms_message = None
            if urgency == "URGENT":
                alert_task = create_telegram_alert_task(alert_agent, message)
                alert_result = alert_task.execute_sync()
                alert_data = self._parse_json_response(str(alert_result))
                sms_message = alert_data.get("sms")
                
                # Fallback SMS if agent didn't provide one
                if not sms_message:
                    sms_message = self._format_sms(message)
            
            return Classification(
                urgency=urgency,
                reason=reason,
                sms_message=sms_message,
            )
            
        except Exception as e:
            logger.error(f"CrewAI classification error: {e}")
            raise
    
    def _fallback_classify(self, message: TelegramMessage) -> Classification:
        """Fallback classification when LLM fails."""
        text_lower = (message.text or "").lower()
        
        # Simple keyword-based fallback
        urgent_words = ["urgent", "emergency", "asap", "help", "important", "now", "immediately"]
        
        for word in urgent_words:
            if word in text_lower:
                return Classification(
                    urgency="URGENT",
                    reason=f"Contains urgent word: {word} (fallback)",
                    sms_message=self._format_sms(message),
                )
        
        return Classification(
            urgency="NOT_URGENT",
            reason="No urgent indicators found (fallback)",
            sms_message=None,
        )
    
    def _format_sms(self, message: TelegramMessage) -> str:
        """Format a Telegram message as SMS."""
        sender = message.sender or message.sender_username or "Unknown"
        text = message.text or ""
        
        # Truncate to fit SMS limit (160 chars)
        prefix = f"TG: {sender} - "
        max_text_len = 160 - len(prefix)
        
        if len(text) > max_text_len:
            text = text[:max_text_len - 3] + "..."
        
        return f"{prefix}{text}"
    
    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from LLM response."""
        # Try to find JSON in the response
        text = text.strip()
        
        # Look for JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end > start:
            json_str = text[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        return {}
