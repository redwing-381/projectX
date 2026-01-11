# Design Document: Telegram Monitor

## Overview

This design adds Telegram message monitoring to ProjectX using a dedicated CrewAI agent architecture. Messages forwarded to a Telegram bot are processed by TelegramMonitorAgent, classified for urgency, and forwarded via SMS if urgent.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ProjectX Server                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Telegram API ──webhook──▶ /telegram/webhook                    │
│                                   │                              │
│                                   ▼                              │
│                          TelegramService                         │
│                          (parse webhook)                         │
│                                   │                              │
│                                   ▼                              │
│                      TelegramProcessingCrew                      │
│                    ┌─────────────────────────┐                  │
│                    │  TelegramMonitorAgent   │                  │
│                    │  (classify urgency)     │                  │
│                    └───────────┬─────────────┘                  │
│                                │                                 │
│                    ┌───────────▼─────────────┐                  │
│                    │      AlertAgent         │                  │
│                    │   (send SMS if urgent)  │                  │
│                    └─────────────────────────┘                  │
│                                │                                 │
│                                ▼                                 │
│                          PostgreSQL                              │
│                       (alert history)                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### TelegramMessage Model

```python
class TelegramMessage(BaseModel):
    """Represents a Telegram message."""
    id: str                    # Telegram message ID
    sender: str                # Sender name or username
    sender_username: Optional[str]  # @username if available
    text: str                  # Message text content
    timestamp: datetime        # When message was sent
    is_forwarded: bool = False # Whether this was forwarded
    original_sender: Optional[str] = None  # Original sender if forwarded
```

### TelegramService

```python
class TelegramService:
    """Service for Telegram bot operations."""
    
    def __init__(self, bot_token: str):
        """Initialize with bot token."""
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """Register webhook URL with Telegram API."""
    
    def parse_update(self, update: dict) -> Optional[TelegramMessage]:
        """Parse Telegram webhook update into TelegramMessage."""
    
    async def send_message(self, chat_id: str, text: str) -> bool:
        """Send a message back to user (for confirmations)."""
```

### TelegramMonitorAgent (CrewAI)

```python
def create_telegram_monitor_agent(llm) -> Agent:
    """Create the Telegram Monitor agent."""
    return Agent(
        role="Telegram Message Monitor",
        goal="Monitor and classify Telegram messages for urgency",
        backstory="""You are an expert at analyzing Telegram messages 
        to determine if they require immediate attention. You understand
        context, urgency indicators, and can distinguish between casual
        messages and urgent communications.""",
        llm=llm,
        verbose=True,
    )
```

### TelegramProcessingCrew

```python
class TelegramProcessingCrew:
    """CrewAI crew for processing Telegram messages."""
    
    def __init__(self, api_key: str, model: str, verbose: bool = False):
        """Initialize crew with LLM settings."""
    
    def process_message(self, message: TelegramMessage) -> Classification:
        """Process a Telegram message through the crew."""
```

### Webhook Endpoint

```python
@router.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    """Handle incoming Telegram webhook updates."""
```

## Data Models

### Database Changes

Add `source` field to AlertHistory model:

```python
class AlertHistory(Base):
    # ... existing fields ...
    source: str = Column(String, default="email")  # "email" or "telegram"
```

### Configuration

New environment variables:
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `TELEGRAM_WEBHOOK_SECRET` - Optional secret for webhook verification

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system.*

### Property 1: Webhook parsing preserves message content

*For any* valid Telegram webhook update containing a text message, parsing it into a TelegramMessage SHALL preserve the sender, text, and timestamp without data loss.

**Validates: Requirements 2.1, 2.2**

### Property 2: VIP sender detection for Telegram usernames

*For any* TelegramMessage where the sender_username matches a VIP sender entry (with or without @ prefix), the TelegramMonitorAgent SHALL classify it as URGENT.

**Validates: Requirements 6.1, 6.2**

### Property 3: Classification output validity

*For any* TelegramMessage processed by TelegramMonitorAgent, the Classification result SHALL have urgency as exactly URGENT or NOT_URGENT, and reason as a non-empty string.

**Validates: Requirements 3.3**

### Property 4: Alert history source distinction

*For any* alert saved to the database from Telegram processing, the source field SHALL be "telegram", distinguishing it from email alerts.

**Validates: Requirements 5.3**

## Error Handling

| Error | Handling |
|-------|----------|
| Invalid webhook signature | Return 401, log warning |
| Malformed update JSON | Return 400, log error |
| Non-text message (media) | Ignore silently, return 200 |
| LLM classification fails | Default to NOT_URGENT |
| SMS send fails | Log error, still save to history |
| Database unavailable | Log warning, continue processing |

## Testing Strategy

### Unit Tests
- TelegramService.parse_update with various webhook formats
- VIP sender matching with @ prefix variations
- TelegramMessage model validation

### Property Tests (Hypothesis)
- Property 1: Webhook parsing round-trip
- Property 2: VIP detection consistency
- Property 3: Classification output validity
- Property 4: Source field correctness

### Integration Tests
- Full webhook → classify → SMS flow
- Dashboard displays Telegram alerts correctly
