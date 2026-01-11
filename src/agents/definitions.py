"""CrewAI agent definitions for email processing."""

import logging
from crewai import Agent, LLM

logger = logging.getLogger(__name__)


def create_monitor_agent(llm: LLM, verbose: bool = False) -> Agent:
    """Create the email monitor agent.
    
    Analyzes email metadata and provides context for classification.
    
    Args:
        llm: The LLM instance to use.
        verbose: Whether to enable verbose logging.
    
    Returns:
        Configured Monitor Agent.
    """
    return Agent(
        role="Email Monitor",
        goal="Analyze email metadata and provide context for urgency classification",
        backstory="""You are an expert at analyzing email patterns and identifying 
        important signals. You examine sender information, subject lines, and 
        timestamps to provide context that helps determine if an email needs 
        immediate attention. You are concise and focus on actionable insights.""",
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )


def create_classifier_agent(llm: LLM, verbose: bool = False) -> Agent:
    """Create the urgency classifier agent.
    
    Determines if an email requires immediate attention.
    
    Args:
        llm: The LLM instance to use.
        verbose: Whether to enable verbose logging.
    
    Returns:
        Configured Classifier Agent.
    """
    return Agent(
        role="Urgency Classifier",
        goal="Determine if an email requires immediate attention and classify as URGENT or NOT_URGENT",
        backstory="""You are an expert at identifying urgent communications. You 
        understand that URGENT emails include: time-sensitive deadlines, emergencies, 
        messages from important people (boss, family, professors), financial matters 
        requiring immediate action, and health/safety concerns. NOT_URGENT emails 
        include: marketing, newsletters, social notifications, and routine updates. 
        You always provide a brief reason for your classification.""",
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )


def create_alert_agent(llm: LLM, verbose: bool = False) -> Agent:
    """Create the SMS alert formatting agent.
    
    Formats urgent emails into concise SMS messages.
    
    Args:
        llm: The LLM instance to use.
        verbose: Whether to enable verbose logging.
    
    Returns:
        Configured Alert Agent.
    """
    return Agent(
        role="Alert Formatter",
        goal="Create concise SMS alerts for urgent emails that fit within 160 characters",
        backstory="""You are an expert at condensing information into brief, 
        actionable SMS messages. You know that SMS messages must be under 160 
        characters to avoid splitting. You always include the sender and subject 
        in a clear, readable format. You prioritize clarity over completeness.""",
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )
