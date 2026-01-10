"""Email urgency classifier agent using LLM."""

import logging
from openai import OpenAI

from src.models.schemas import Email, Classification, Urgency

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
