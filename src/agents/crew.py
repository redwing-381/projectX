"""CrewAI crew orchestration for email processing."""

import json
import logging
import os
from crewai import Crew, Process, LLM

from src.models.schemas import Email, Classification, Urgency
from src.agents.definitions import (
    create_monitor_agent,
    create_classifier_agent,
    create_alert_agent,
)
from src.agents.tasks import (
    create_monitor_task,
    create_classifier_task,
    create_alert_task,
)

logger = logging.getLogger(__name__)


class EmailProcessingCrew:
    """Crew that processes emails using Monitor, Classifier, and Alert agents."""

    def __init__(
        self,
        api_key: str,
        model: str = "openrouter/openai/gpt-4o-mini",
        verbose: bool = False,
    ):
        """Initialize the crew with LLM configuration.
        
        Args:
            api_key: OpenRouter API key.
            model: Model name in CrewAI format (e.g., openrouter/openai/gpt-4o-mini).
            verbose: Whether to enable verbose logging for agents.
        """
        # Set the API key as environment variable for CrewAI
        os.environ["OPENROUTER_API_KEY"] = api_key
        
        self.llm = LLM(
            model=model,
            api_key=api_key,
        )
        self.verbose = verbose
        
        # Create agents
        self.monitor = create_monitor_agent(self.llm, verbose)
        self.classifier = create_classifier_agent(self.llm, verbose)
        self.alerter = create_alert_agent(self.llm, verbose)
        
        logger.info(f"EmailProcessingCrew initialized with model: {model}")

    def process_email(self, email: Email) -> Classification:
        """Process a single email through the crew.
        
        Args:
            email: The email to process.
        
        Returns:
            Classification with urgency and reason.
        """
        try:
            # Create tasks for this email
            monitor_task = create_monitor_task(self.monitor, email)
            classifier_task = create_classifier_task(self.classifier, email)
            alert_task = create_alert_task(self.alerter, email)
            
            # Create and run the crew
            crew = Crew(
                agents=[self.monitor, self.classifier, self.alerter],
                tasks=[monitor_task, classifier_task, alert_task],
                process=Process.sequential,
                verbose=self.verbose,
            )
            
            result = crew.kickoff()
            logger.debug(f"Crew result: {result}")
            
            return self._parse_result(result, email)
            
        except Exception as e:
            logger.error(f"Crew processing error for email {email.id}: {e}")
            return Classification(
                urgency=Urgency.NOT_URGENT,
                reason=f"Classification failed - {str(e)[:50]}",
            )

    def _parse_result(self, result, email: Email) -> Classification:
        """Parse crew output into Classification.
        
        Args:
            result: The crew execution result.
            email: The original email (for context in error handling).
        
        Returns:
            Classification extracted from the result.
        """
        try:
            # Get the raw output string
            raw_output = str(result.raw) if hasattr(result, 'raw') else str(result)
            logger.debug(f"Raw crew output: {raw_output}")
            
            # Try to find JSON in the output
            # Look for the classifier task output which contains urgency
            json_str = self._extract_json(raw_output)
            
            if json_str:
                data = json.loads(json_str)
                urgency_str = data.get("urgency", "NOT_URGENT")
                reason = data.get("reason", "No reason provided")
                
                urgency = Urgency.URGENT if urgency_str == "URGENT" else Urgency.NOT_URGENT
                return Classification(urgency=urgency, reason=reason)
            
            # Fallback: check if output contains URGENT keyword
            if "URGENT" in raw_output.upper() and "NOT_URGENT" not in raw_output.upper():
                return Classification(
                    urgency=Urgency.URGENT,
                    reason="Classified as urgent based on crew analysis",
                )
            
            return Classification(
                urgency=Urgency.NOT_URGENT,
                reason="Classified as not urgent based on crew analysis",
            )
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from crew output: {e}")
            return Classification(
                urgency=Urgency.NOT_URGENT,
                reason="Could not parse classification result",
            )
        except Exception as e:
            logger.error(f"Error parsing crew result: {e}")
            return Classification(
                urgency=Urgency.NOT_URGENT,
                reason=f"Parse error - {str(e)[:30]}",
            )

    def _extract_json(self, text: str) -> str | None:
        """Extract JSON object from text.
        
        Args:
            text: Text that may contain JSON.
        
        Returns:
            JSON string if found, None otherwise.
        """
        # Look for JSON patterns with urgency field
        import re
        
        # Try to find JSON with urgency field
        patterns = [
            r'\{[^{}]*"urgency"[^{}]*\}',
            r'\{[^{}]*"sms"[^{}]*\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue
        
        return None
