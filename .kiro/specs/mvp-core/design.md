# Design Document: ProjectX MVP

## Overview

Minimal proof of concept for the email-to-SMS alert pipeline. The MVP validates the core flow: fetch Gmail → AI classifies urgency → send SMS for urgent emails.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST /check                                             │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Gmail   │───▶│  Classifier  │───▶│   Twilio     │  │
│  │ Service  │    │    Agent     │    │   Service    │  │
│  └──────────┘    └──────────────┘    └──────────────┘  │
│       │                │                    │           │
│   Gmail API        OpenAI API          Twilio API      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Gmail Service (`src/services/gmail.py`)

```python
class GmailService:
    def __init__(self, credentials_path: str):
        """Initialize with OAuth credentials."""
        
    async def get_unread_emails(self, max_results: int = 10) -> list[Email]:
        """Fetch unread emails from inbox."""
        
    def extract_email_data(self, raw_message: dict) -> Email:
        """Extract sender, subject, snippet from raw Gmail message."""
```

### 2. Classifier Agent (`src/agents/classifier.py`)

```python
class ClassifierAgent:
    def __init__(self, openai_api_key: str):
        """Initialize with OpenAI API key."""
        
    async def classify(self, email: Email) -> Classification:
        """Classify email urgency using LLM."""
```

### 3. Twilio Service (`src/services/twilio_sms.py`)

```python
class TwilioService:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """Initialize Twilio client."""
        
    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS, return success status."""
        
    def format_alert(self, email: Email) -> str:
        """Format email into SMS message (max 160 chars)."""
```

### 4. Pipeline Orchestrator (`src/services/pipeline.py`)

```python
class Pipeline:
    def __init__(self, gmail: GmailService, classifier: ClassifierAgent, twilio: TwilioService):
        """Initialize with all services."""
        
    async def run(self) -> PipelineResult:
        """Execute full pipeline: fetch → classify → alert."""
```

### 5. FastAPI App (`src/main.py`)

```python
@app.get("/health")
async def health() -> dict:
    """Return health status."""

@app.post("/check")
async def check_emails() -> dict:
    """Run pipeline and return results."""
```

## Data Models

```python
from pydantic import BaseModel
from enum import Enum

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

### Property 1: Email extraction completeness

*For any* raw Gmail message with sender, subject, and body, the `extract_email_data` function SHALL return an Email object with all three fields populated (non-empty strings).

**Validates: Requirements 1.3**

### Property 2: Classification output validity

*For any* email input, the Classifier Agent SHALL return a Classification with:
- `urgency` being exactly URGENT or NOT_URGENT
- `reason` being a non-empty string

**Validates: Requirements 2.2, 2.3**

### Property 3: SMS message length constraint

*For any* email with any sender name and subject, the `format_alert` function SHALL return a string of 160 characters or fewer.

**Validates: Requirements 3.2**

### Property 4: API response format

*For any* request to /check endpoint, the response SHALL be valid JSON conforming to PipelineResult schema.

**Validates: Requirements 4.3**

## Error Handling

| Error | Handling |
|-------|----------|
| Gmail OAuth expired | Log error, return 503 |
| Gmail API rate limit | Log error, return 429 |
| OpenAI API failure | Log error, mark email as NOT_URGENT with reason "Classification failed" |
| Twilio API failure | Log error, mark sms_sent as false |
| Invalid email format | Skip email, log warning |

## Testing Strategy

### Unit Tests
- Test `extract_email_data` with various raw message formats
- Test `format_alert` with edge cases (long subjects, special chars)
- Test Classification model validation

### Property-Based Tests (using Hypothesis)
- Property 1: Generate random email data, verify extraction
- Property 2: Mock LLM responses, verify output format
- Property 3: Generate random sender/subject strings, verify length
- Property 4: Test API responses conform to schema

### Integration Tests
- Mock Gmail API, test full pipeline
- Mock all external APIs, test /check endpoint

### Configuration
- Use pytest with pytest-asyncio
- Minimum 100 iterations for property tests
- Mock external APIs (Gmail, OpenAI, Twilio) in all tests
