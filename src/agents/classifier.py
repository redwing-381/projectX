"""Email urgency classifier agent using LLM."""

import logging
from typing import Optional, Tuple
from openai import OpenAI

from src.models.schemas import Email, Classification, Urgency
from src.config import cache

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """You are an email urgency classifier. Analyze the email and determine if it requires immediate attention.

Consider these factors for URGENT classification:
- Time-sensitive deadlines (today, tomorrow, ASAP)
- Emergency or crisis situations
- Important people (boss, family, professors)
- Financial matters requiring immediate action
- Health or safety concerns
- Job/interview related urgent matters

Consider these factors for NOT_URGENT:
- Marketing/promotional emails
- Newsletters and subscriptions
- Social media notifications
- General updates that can wait
- Automated system notifications

Email Details:
- From: {sender}
- Subject: {subject}
- Preview: {snippet}

Respond with ONLY a JSON object in this exact format:
{{"urgency": "URGENT" or "NOT_URGENT", "reason": "one line explanation"}}
"""


def get_cached_vip_senders():
    """Get VIP senders with caching (60s TTL)."""
    cached = cache.get("vip_senders")
    if cached is not None:
        return cached
    
    try:
        from src.db.database import get_db_session
        from src.db import crud
        
        with get_db_session() as db:
            vip_senders = crud.get_vip_senders(db)
            result = [v.email_or_domain.lower() for v in vip_senders]
            cache.set("vip_senders", result)
            return result
    except Exception:
        return []


def get_cached_keywords():
    """Get keywords with caching (60s TTL)."""
    cached = cache.get("keywords")
    if cached is not None:
        return cached
    
    try:
        from src.db.database import get_db_session
        from src.db import crud
        
        with get_db_session() as db:
            keywords = crud.get_keywords(db)
            result = [k.keyword.lower() for k in keywords]
            cache.set("keywords", result)
            return result
    except Exception:
        return []


def check_vip_and_keywords(email: Email) -> Tuple[bool, Optional[str]]:
    """Check if email matches VIP sender or contains urgent keyword.
    
    Uses cached VIP senders and keywords for performance.
    
    Returns:
        Tuple of (is_urgent, reason) if matched, (False, None) otherwise.
    """
    email_lower = email.sender.lower()
    
    # Check VIP senders (cached)
    vip_senders = get_cached_vip_senders()
    for vip in vip_senders:
        if vip in email_lower or email_lower.endswith(f"@{vip}") or email_lower.endswith(f".{vip}"):
            return True, f"VIP sender: {vip}"
    
    # Check keywords (cached)
    text_to_check = f"{email.subject} {email.snippet}".lower()
    keywords = get_cached_keywords()
    for keyword in keywords:
        if keyword in text_to_check:
            return True, f"Urgent keyword: {keyword}"
    
    return False, None


class ClassifierAgent:
    """Agent that classifies email urgency using LLM (OpenRouter or OpenAI compatible)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "openai/gpt-4o-mini",
    ):
        """Initialize classifier with LLM API.

        Args:
            api_key: API key (OpenRouter or OpenAI).
            base_url: API base URL (OpenRouter or OpenAI).
            model: Model to use for classification.
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model

    async def classify(self, email: Email) -> Classification:
        """Classify email urgency using LLM.

        Args:
            email: Email to classify.

        Returns:
            Classification with urgency level and reason.
        """
        # First check VIP senders and keywords (instant URGENT)
        is_urgent, rule_reason = check_vip_and_keywords(email)
        if is_urgent:
            logger.info(f"Email marked URGENT by rule: {rule_reason}")
            return Classification(urgency=Urgency.URGENT, reason=rule_reason)
        
        # Fall back to LLM classification
        try:
            prompt = CLASSIFICATION_PROMPT.format(
                sender=email.sender,
                subject=email.subject,
                snippet=email.snippet,
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an email urgency classifier. Respond only with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=100,
            )

            result_text = response.choices[0].message.content.strip()
            logger.debug(f"LLM response: {result_text}")

            # Parse JSON response
            import json

            result = json.loads(result_text)

            urgency = Urgency.URGENT if result["urgency"] == "URGENT" else Urgency.NOT_URGENT
            reason = result.get("reason", "No reason provided")

            return Classification(urgency=urgency, reason=reason)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return Classification(
                urgency=Urgency.NOT_URGENT,
                reason="Classification failed - could not parse response",
            )
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return Classification(
                urgency=Urgency.NOT_URGENT,
                reason=f"Classification failed - {str(e)[:50]}",
            )
