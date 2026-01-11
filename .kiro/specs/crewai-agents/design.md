# Design Document: CrewAI Agents

## Overview

Refactor ProjectX to use CrewAI for multi-agent orchestration. The system will use three specialized agents (Monitor, Classifier, Alert) working together as a crew to process emails. This replaces the current single direct-OpenAI classifier while maintaining API compatibility.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       CrewAI Crew                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Monitor    │───▶│  Classifier  │───▶│    Alert     │      │
│  │    Agent     │    │    Agent     │    │    Agent     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │                │
│    Analyze email      Determine urgency    Format SMS           │
│    metadata           URGENT/NOT_URGENT    (if urgent)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   OpenRouter     │
                    │  (GPT-4o-mini)   │
                    └──────────────────┘
```

## Components and Interfaces

### 1. Agent Definitions (`src/agents/definitions.py`)

```python
from crewai import Agent, LLM

def create_monitor_agent(llm: LLM) -> Agent:
    """Create the email monitor agent."""
    return Agent(
        role="Email Monitor",
        goal="Analyze email metadata and provide context for classification",
        backstory="Expert at analyzing email patterns and identifying important signals",
        llm=llm,
        verbose=False,
    )

def create_classifier_agent(llm: LLM) -> Agent:
    """Create the urgency classifier agent."""
    return Agent(
        role="Urgency Classifier",
        goal="Determine if an email requires immediate attention",
        backstory="Expert at identifying urgent communications that need immediate action",
        llm=llm,
        verbose=False,
    )

def create_alert_agent(llm: LLM) -> Agent:
    """Create the SMS alert formatting agent."""
    return Agent(
        role="Alert Formatter",
        goal="Create concise SMS alerts for urgent emails",
        backstory="Expert at condensing information into brief, actionable SMS messages",
        llm=llm,
        verbose=False,
    )
```

### 2. Task Definitions (`src/agents/tasks.py`)

```python
from crewai import Task

def create_monitor_task(agent: Agent, email: Email) -> Task:
    """Create monitoring task for an email."""
    return Task(
        description=f"""Analyze this email and provide context:
        From: {email.sender}
        Subject: {email.subject}
        Preview: {email.snippet}
        
        Identify: sender type, subject urgency signals, time sensitivity.""",
        expected_output="Brief context summary about the email",
        agent=agent,
    )

def create_classifier_task(agent: Agent, email: Email) -> Task:
    """Create classification task."""
    return Task(
        description=f"""Based on the context, classify this email's urgency.
        
        URGENT indicators: deadlines, emergencies, important people, financial matters
        NOT_URGENT indicators: marketing, newsletters, social notifications
        
        Respond with JSON: {{"urgency": "URGENT" or "NOT_URGENT", "reason": "brief explanation"}}""",
        expected_output="JSON with urgency classification",
        agent=agent,
    )

def create_alert_task(agent: Agent, email: Email) -> Task:
    """Create alert formatting task."""
    return Task(
        description=f"""If the email is URGENT, format an SMS alert.
        Include sender and subject. Keep under 160 characters.
        
        From: {email.sender}
        Subject: {email.subject}
        
        If NOT_URGENT, respond with: {{"sms": null}}
        If URGENT, respond with: {{"sms": "your message here"}}""",
        expected_output="JSON with SMS message or null",
        agent=agent,
    )
```

### 3. Crew Orchestration (`src/agents/crew.py`)

```python
from crewai import Crew, Process, LLM

class EmailProcessingCrew:
    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the crew with LLM configuration."""
        self.llm = LLM(
            model=model,
            api_key=api_key,
            base_url=base_url,
        )
        self.monitor = create_monitor_agent(self.llm)
        self.classifier = create_classifier_agent(self.llm)
        self.alerter = create_alert_agent(self.llm)
    
    def process_email(self, email: Email) -> Classification:
        """Process a single email through the crew."""
        tasks = [
            create_monitor_task(self.monitor, email),
            create_classifier_task(self.classifier, email),
            create_alert_task(self.alerter, email),
        ]
        
        crew = Crew(
            agents=[self.monitor, self.classifier, self.alerter],
            tasks=tasks,
            process=Process.sequential,
            verbose=False,
        )
        
        result = crew.kickoff()
        return self._parse_result(result)
    
    def _parse_result(self, result) -> Classification:
        """Parse crew output into Classification."""
        # Extract urgency and reason from crew output
        pass
```

### 4. Updated Pipeline (`src/services/pipeline.py`)

```python
class Pipeline:
    def __init__(self, gmail: GmailService, crew: EmailProcessingCrew, twilio: TwilioService):
        """Initialize with CrewAI crew instead of single classifier."""
        self.gmail = gmail
        self.crew = crew
        self.twilio = twilio
    
    async def run(self) -> PipelineResult:
        """Execute pipeline using CrewAI crew."""
        emails = await self.gmail.get_unread_emails()
        results = []
        alerts_sent = 0
        
        for email in emails:
            classification = self.crew.process_email(email)
            sms_sent = False
            
            if classification.urgency == Urgency.URGENT:
                message = self.twilio.format_alert(email)
                sms_sent = self.twilio.send_sms(self.to_number, message)
                if sms_sent:
                    alerts_sent += 1
            
            results.append(AlertResult(...))
        
        return PipelineResult(
            emails_checked=len(emails),
            alerts_sent=alerts_sent,
            results=results,
        )
```

## Data Models

Existing models remain unchanged:

```python
class Urgency(str, Enum):
    URGENT = "URGENT"
    NOT_URGENT = "NOT_URGENT"

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    snippet: str

class Classification(BaseModel):
    urgency: Urgency
    reason: str

class AlertResult(BaseModel):
    email_id: str
    sender: str
    subject: str
    urgency: Urgency
    reason: str
    sms_sent: bool

class PipelineResult(BaseModel):
    emails_checked: int
    alerts_sent: int
    results: list[AlertResult]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do.*

### Property 1: Monitor context completeness

*For any* email with sender, subject, and snippet, the Monitor Agent SHALL produce a non-empty context string that references the email's key attributes.

**Validates: Requirements 2.1, 2.3**

### Property 2: Classification output validity

*For any* email processed by the Classifier Agent, the output SHALL contain:
- `urgency` being exactly URGENT or NOT_URGENT
- `reason` being a non-empty string

**Validates: Requirements 3.3, 3.4**

### Property 3: SMS format validity

*For any* email classified as URGENT with any sender name and subject, the Alert Agent SHALL produce an SMS message that:
- Is 160 characters or fewer
- Contains the sender information
- Contains the subject information

**Validates: Requirements 4.2, 4.3, 4.4**

### Property 4: Crew result schema conformance

*For any* crew execution, the final output SHALL be valid JSON conforming to the PipelineResult schema with all required fields populated.

**Validates: Requirements 5.3**

### Property 5: Error handling graceful degradation

*For any* agent failure during crew execution, the system SHALL return a valid Classification with urgency=NOT_URGENT and a reason indicating the failure, rather than crashing.

**Validates: Requirements 5.4**

## Error Handling

| Error | Handling |
|-------|----------|
| CrewAI initialization failure | Log error, fall back to direct OpenAI call |
| Monitor Agent timeout | Skip monitoring, proceed with classification |
| Classifier Agent failure | Return NOT_URGENT with "Classification failed" reason |
| Alert Agent failure | Use default format_alert function |
| LLM rate limit | Retry with exponential backoff (max 3 attempts) |
| Invalid JSON from agent | Parse best effort, use defaults for missing fields |

## Testing Strategy

### Unit Tests
- Test agent creation with correct roles and goals
- Test task creation with proper descriptions
- Test result parsing with various JSON formats
- Test error handling for malformed responses

### Property-Based Tests (using Hypothesis)
- Property 1: Generate random emails, verify monitor produces context
- Property 2: Mock classifier responses, verify output format
- Property 3: Generate random sender/subject, verify SMS constraints
- Property 4: Test crew output conforms to schema
- Property 5: Inject failures, verify graceful degradation

### Integration Tests
- Test full crew execution with mocked LLM
- Test pipeline with CrewAI crew
- Test backward compatibility of /check endpoint

### Configuration
- Use pytest with pytest-asyncio
- Minimum 100 iterations for property tests
- Mock LLM responses for deterministic testing
