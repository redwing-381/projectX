# Design Document

## Overview

This design document describes the implementation of three features to enhance ProjectX for hackathon presentation: Demo Mode, Analytics Dashboard, and Quick Actions. These features work together to provide a polished, demonstrable product that judges can evaluate without requiring Gmail setup.

## Architecture

The features integrate into the existing FastAPI application with minimal changes to core architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Dashboard                           │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│  Dashboard  │  Analytics  │   History   │    Demo Mode     │
│  + Quick    │   Charts    │  + Quick    │    Banner        │
│   Actions   │             │   Actions   │                  │
└─────────────┴─────────────┴─────────────┴──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Demo Mode Service                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Sample    │  │   Session   │  │   Mock SMS          │ │
│  │   Emails    │  │   Store     │  │   Service           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Existing Classification Pipeline                │
│  (VIP Check → Keyword Check → AI Classification)            │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Demo Mode Service

**File:** `src/services/demo.py`

```python
class DemoService:
    """Manages demo mode state and sample data."""
    
    SAMPLE_EMAILS: list[Email]  # 10+ diverse sample emails
    
    def get_sample_emails() -> list[Email]:
        """Return sample emails for demo mode."""
    
    def is_demo_mode(session: dict) -> bool:
        """Check if demo mode is active in session."""
    
    def activate_demo(session: dict) -> None:
        """Activate demo mode in session."""
    
    def deactivate_demo(session: dict) -> None:
        """Deactivate demo mode and clear session data."""
    
    def store_demo_results(session: dict, results: list[AlertResult]) -> None:
        """Store classification results in session (not DB)."""
    
    def get_demo_results(session: dict) -> list[AlertResult]:
        """Retrieve demo results from session."""
```

### Analytics Service

**File:** `src/services/analytics.py`

```python
class AnalyticsService:
    """Calculates analytics data from alert history."""
    
    def get_emails_by_day(db: Session, days: int = 7) -> list[dict]:
        """Get email counts grouped by day for line chart."""
        # Returns: [{"date": "2026-01-19", "count": 15}, ...]
    
    def get_urgency_ratio(db: Session) -> dict:
        """Get urgent vs non-urgent counts for pie chart."""
        # Returns: {"urgent": 25, "not_urgent": 175}
    
    def get_top_senders(db: Session, limit: int = 5) -> list[dict]:
        """Get top senders by email count for bar chart."""
        # Returns: [{"sender": "boss@company.com", "count": 12}, ...]
    
    def get_summary_metrics(db: Session) -> dict:
        """Get key metrics for dashboard cards."""
        # Returns: {"total_emails": 200, "total_alerts": 25, "alert_rate": 12.5}
```

### Quick Actions API

**File:** `src/api/routes/quick_actions.py`

```python
@router.post("/api/quick-actions/add-vip")
async def add_sender_to_vip(sender: str, db: Session) -> dict:
    """Add sender to VIP list via AJAX."""
    # Extract email from sender string (e.g., "John <john@example.com>")
    # Check if already VIP
    # Add to VIP list
    # Return success/already_vip status

@router.get("/api/quick-actions/check-vip")
async def check_if_vip(sender: str, db: Session) -> dict:
    """Check if sender is already in VIP list."""
```

### Sample Emails Data

**File:** `src/services/demo.py` (SAMPLE_EMAILS constant)

10 diverse sample emails covering:
1. VIP sender match (boss@company.com)
2. Keyword match ("URGENT" in subject)
3. Time-sensitive deadline
4. Marketing/promotional (not urgent)
5. Newsletter (not urgent)
6. Family emergency
7. Job interview follow-up
8. Social media notification (not urgent)
9. Financial alert
10. System notification (not urgent)

## Data Models

### Demo Session Data

```python
# Stored in FastAPI session (cookie-based)
{
    "demo_mode": True,
    "demo_results": [
        {
            "email_id": "demo-001",
            "sender": "Boss <boss@company.com>",
            "subject": "URGENT: Project deadline moved",
            "urgency": "URGENT",
            "reason": "VIP sender: boss@company.com",
            "sms_sent": True,  # Simulated
            "timestamp": "2026-01-19T10:30:00"
        },
        ...
    ]
}
```

### Analytics Response Models

```python
class EmailsByDayResponse(BaseModel):
    data: list[dict]  # [{"date": str, "count": int}]

class UrgencyRatioResponse(BaseModel):
    urgent: int
    not_urgent: int

class TopSendersResponse(BaseModel):
    data: list[dict]  # [{"sender": str, "count": int}]

class SummaryMetricsResponse(BaseModel):
    total_emails: int
    total_alerts: int
    alert_rate: float
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Demo Mode Data Isolation

*For any* operation performed while demo mode is active, the database alert_history table SHALL NOT be modified, and no SMS SHALL be sent via Twilio.

**Validates: Requirements 2.6, 5.1, 5.2**

### Property 2: Demo Mode Uses Real Classification

*For any* sample email processed in demo mode, the classification result SHALL be produced by the real classification pipeline (VIP check → Keyword check → AI classification).

**Validates: Requirements 1.3, 2.1**

### Property 3: Analytics Calculations Correctness

*For any* set of alert history records, the analytics service SHALL correctly calculate:
- Emails by day: count of records grouped by created_at date
- Urgency ratio: count of URGENT vs NOT_URGENT records
- Top senders: senders ordered by frequency, limited to top N
- Alert rate: (urgent_count / total_count) * 100

**Validates: Requirements 3.2, 3.3, 3.4**

### Property 4: Quick Action VIP Addition

*For any* sender string from an alert, clicking "Add to VIP" SHALL result in:
- If sender not in VIP list: sender added and success returned
- If sender already in VIP list: no duplicate added and "already_vip" returned

**Validates: Requirements 4.2, 4.3**

### Property 5: Demo Session Cleanup

*For any* demo session, when demo mode is deactivated, all demo_results SHALL be cleared from the session.

**Validates: Requirements 5.4**

## Error Handling

| Scenario | Handling |
|----------|----------|
| Demo mode with no sample emails | Return empty list, show "No sample emails configured" |
| Analytics with no data | Show empty state with "No data yet" message |
| Quick action on invalid sender | Return error, show "Could not extract email" |
| Session storage full | Limit demo results to last 20, rotate oldest |
| Database unavailable for analytics | Show cached data or "Analytics unavailable" |

## Testing Strategy

### Unit Tests

- Test email extraction from sender strings (e.g., "John <john@example.com>" → "john@example.com")
- Test analytics calculations with known data sets
- Test demo mode session management

### Property-Based Tests

Using Hypothesis library with minimum 100 iterations:

1. **Demo Isolation Test**: Generate random emails, process in demo mode, verify DB unchanged
2. **Analytics Calculation Test**: Generate random alert histories, verify calculations match expected
3. **VIP Addition Test**: Generate random sender strings, verify correct extraction and addition

### Integration Tests

- Full demo mode flow: activate → check emails → view results → deactivate
- Analytics page with various data states
- Quick action from dashboard and history pages
