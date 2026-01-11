"""CrewAI task definitions for email and Telegram processing."""

from crewai import Task, Agent
from src.models.schemas import Email, TelegramMessage


def create_monitor_task(agent: Agent, email: Email) -> Task:
    """Create monitoring task for an email.
    
    Args:
        agent: The Monitor Agent to assign this task to.
        email: The email to analyze.
    
    Returns:
        Configured monitoring Task.
    """
    return Task(
        description=f"""Analyze this email and provide brief context for urgency classification:

From: {email.sender}
Subject: {email.subject}
Preview: {email.snippet}

Identify key signals:
1. Sender type (person, company, automated system)
2. Subject urgency indicators (deadlines, action words)
3. Any time-sensitive language in the preview

Provide a 1-2 sentence context summary.""",
        expected_output="Brief context summary about the email's urgency signals",
        agent=agent,
    )


def create_classifier_task(agent: Agent, email: Email) -> Task:
    """Create classification task for an email.
    
    Args:
        agent: The Classifier Agent to assign this task to.
        email: The email to classify.
    
    Returns:
        Configured classification Task.
    """
    return Task(
        description=f"""Based on the context provided, classify this email's urgency.

Email Details:
From: {email.sender}
Subject: {email.subject}
Preview: {email.snippet}

URGENT indicators:
- Time-sensitive deadlines (today, tomorrow, ASAP)
- Emergency or crisis situations
- Important people (boss, family, professors)
- Financial matters requiring immediate action
- Health or safety concerns
- Job/interview related urgent matters

NOT_URGENT indicators:
- Marketing/promotional emails
- Newsletters and subscriptions
- Social media notifications
- General updates that can wait
- Automated system notifications

You MUST respond with ONLY valid JSON in this exact format:
{{"urgency": "URGENT", "reason": "brief explanation"}}
or
{{"urgency": "NOT_URGENT", "reason": "brief explanation"}}""",
        expected_output='JSON object with urgency classification: {"urgency": "URGENT" or "NOT_URGENT", "reason": "explanation"}',
        agent=agent,
    )


def create_alert_task(agent: Agent, email: Email) -> Task:
    """Create alert formatting task for an email.
    
    Args:
        agent: The Alert Agent to assign this task to.
        email: The email to format as SMS.
    
    Returns:
        Configured alert formatting Task.
    """
    return Task(
        description=f"""Based on the classification, format an SMS alert if the email is URGENT.

Email Details:
From: {email.sender}
Subject: {email.subject}

Rules:
1. If NOT_URGENT: respond with {{"sms": null}}
2. If URGENT: create an SMS message that:
   - Is UNDER 160 characters total
   - Includes sender name (shortened if needed)
   - Includes subject (truncated if needed)
   - Is clear and actionable

Example format: "URGENT: [Sender] - [Subject truncated...]"

You MUST respond with ONLY valid JSON:
{{"sms": "your message here"}} or {{"sms": null}}""",
        expected_output='JSON object with SMS message: {"sms": "message"} or {"sms": null}',
        agent=agent,
    )



def create_telegram_classifier_task(agent: Agent, message: TelegramMessage) -> Task:
    """Create classification task for a Telegram message.
    
    Args:
        agent: The Telegram Monitor Agent to assign this task to.
        message: The Telegram message to classify.
    
    Returns:
        Configured classification Task.
    """
    forwarded_info = ""
    if message.is_forwarded and message.original_sender:
        forwarded_info = f"\nForwarded from: {message.original_sender}"
    
    return Task(
        description=f"""Classify this Telegram message's urgency.

Message Details:
From: {message.sender} (@{message.sender_username or 'unknown'})
Text: {message.text}{forwarded_info}

URGENT indicators:
- Time-sensitive requests (today, tomorrow, ASAP, now)
- Emergency or crisis situations
- Messages from important people (boss, family, professors)
- Financial matters requiring immediate action
- Health or safety concerns
- Job/interview related urgent matters
- Explicit urgency words (urgent, emergency, important, help)

NOT_URGENT indicators:
- Casual conversation
- General updates that can wait
- Memes, jokes, or entertainment
- Non-time-sensitive questions
- Social chit-chat

You MUST respond with ONLY valid JSON in this exact format:
{{"urgency": "URGENT", "reason": "brief explanation"}}
or
{{"urgency": "NOT_URGENT", "reason": "brief explanation"}}""",
        expected_output='JSON object with urgency classification: {"urgency": "URGENT" or "NOT_URGENT", "reason": "explanation"}',
        agent=agent,
    )


def create_telegram_alert_task(agent: Agent, message: TelegramMessage) -> Task:
    """Create alert formatting task for a Telegram message.
    
    Args:
        agent: The Alert Agent to assign this task to.
        message: The Telegram message to format as SMS.
    
    Returns:
        Configured alert formatting Task.
    """
    return Task(
        description=f"""Based on the classification, format an SMS alert if the message is URGENT.

Telegram Message:
From: {message.sender} (@{message.sender_username or 'unknown'})
Text: {message.text}

Rules:
1. If NOT_URGENT: respond with {{"sms": null}}
2. If URGENT: create an SMS message that:
   - Is UNDER 160 characters total
   - Starts with "TG:" to indicate Telegram source
   - Includes sender name (shortened if needed)
   - Includes key message content (truncated if needed)
   - Is clear and actionable

Example format: "TG: [Sender] - [Message truncated...]"

You MUST respond with ONLY valid JSON:
{{"sms": "your message here"}} or {{"sms": null}}""",
        expected_output='JSON object with SMS message: {"sms": "message"} or {"sms": null}',
        agent=agent,
    )
