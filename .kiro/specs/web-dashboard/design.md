# Design Document: Web Dashboard

## Overview

A FastAPI + Jinja2 web dashboard for ProjectX with PostgreSQL persistence. Provides pages for viewing alert history, managing VIP senders and keyword rules, and configuring settings.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Dashboard    Alert History    VIP Senders    Keywords    Settings
│     │              │               │             │           │   │
│     └──────────────┴───────────────┴─────────────┴───────────┘   │
│                              │                                    │
│                    ┌─────────▼─────────┐                         │
│                    │   FastAPI Routes  │                         │
│                    │  (src/api/web.py) │                         │
│                    └─────────┬─────────┘                         │
│                              │                                    │
│              ┌───────────────┼───────────────┐                   │
│              ▼               ▼               ▼                   │
│     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│     │   Database   │ │   Pipeline   │ │  Templates   │          │
│     │   (CRUD)     │ │  (Classify)  │ │  (Jinja2)    │          │
│     └──────┬───────┘ └──────────────┘ └──────────────┘          │
│            │                                                      │
└────────────┼──────────────────────────────────────────────────────┘
             │
             ▼
    ┌──────────────────┐
    │   PostgreSQL     │
    │   (Railway)      │
    └──────────────────┘
```

## Components and Interfaces

### 1. Database Models (`src/db/models.py`)

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True)
    email_id = Column(String, unique=True)
    sender = Column(String)
    subject = Column(String)
    snippet = Column(String)
    urgency = Column(String)  # URGENT or NOT_URGENT
    reason = Column(String)
    sms_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class VIPSender(Base):
    __tablename__ = "vip_senders"
    
    id = Column(Integer, primary_key=True)
    email_or_domain = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class KeywordRule(Base):
    __tablename__ = "keyword_rules"
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(String)
```

### 2. Database Connection (`src/db/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```


### 3. CRUD Operations (`src/db/crud.py`)

```python
from sqlalchemy.orm import Session

# Alert History
def create_alert(db: Session, alert: AlertHistory) -> AlertHistory:
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def get_alerts(db: Session, skip: int = 0, limit: int = 20, 
               urgency: str = None) -> list[AlertHistory]:
    query = db.query(AlertHistory)
    if urgency:
        query = query.filter(AlertHistory.urgency == urgency)
    return query.order_by(AlertHistory.created_at.desc()).offset(skip).limit(limit).all()

def get_today_stats(db: Session) -> dict:
    today = datetime.utcnow().date()
    # Return emails_checked, alerts_sent for today

# VIP Senders
def get_vip_senders(db: Session) -> list[VIPSender]:
    return db.query(VIPSender).all()

def add_vip_sender(db: Session, email_or_domain: str) -> VIPSender:
    vip = VIPSender(email_or_domain=email_or_domain)
    db.add(vip)
    db.commit()
    return vip

def remove_vip_sender(db: Session, id: int) -> bool:
    vip = db.query(VIPSender).filter(VIPSender.id == id).first()
    if vip:
        db.delete(vip)
        db.commit()
        return True
    return False

def is_vip_sender(db: Session, email: str) -> bool:
    # Check if email matches any VIP sender or domain

# Keyword Rules
def get_keywords(db: Session) -> list[KeywordRule]:
    return db.query(KeywordRule).all()

def add_keyword(db: Session, keyword: str) -> KeywordRule:
    rule = KeywordRule(keyword=keyword.lower())
    db.add(rule)
    db.commit()
    return rule

def remove_keyword(db: Session, id: int) -> bool:
    # Similar to remove_vip_sender

def has_urgent_keyword(db: Session, text: str) -> tuple[bool, str]:
    # Check if text contains any keyword, return (found, keyword)
```

### 4. Web Routes (`src/api/web.py`)

```python
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    stats = get_today_stats(db)
    recent_alerts = get_alerts(db, limit=5)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_alerts": recent_alerts,
    })

@router.get("/history", response_class=HTMLResponse)
async def history(request: Request, page: int = 1, 
                  urgency: str = None, db: Session = Depends(get_db)):
    alerts = get_alerts(db, skip=(page-1)*20, limit=20, urgency=urgency)
    return templates.TemplateResponse("history.html", {...})

@router.get("/vip-senders", response_class=HTMLResponse)
async def vip_senders_page(request: Request, db: Session = Depends(get_db)):
    senders = get_vip_senders(db)
    return templates.TemplateResponse("vip_senders.html", {...})

@router.post("/vip-senders/add")
async def add_vip(email: str = Form(...), db: Session = Depends(get_db)):
    add_vip_sender(db, email)
    return RedirectResponse("/vip-senders", status_code=303)

@router.post("/vip-senders/delete/{id}")
async def delete_vip(id: int, db: Session = Depends(get_db)):
    remove_vip_sender(db, id)
    return RedirectResponse("/vip-senders", status_code=303)

# Similar routes for keywords and settings
```

### 5. Templates (`src/templates/`)

- `base.html` - Base template with navigation
- `dashboard.html` - Home page with stats and recent alerts
- `history.html` - Paginated alert history with filters
- `vip_senders.html` - VIP sender management
- `keywords.html` - Keyword rules management
- `settings.html` - System settings

## Data Models

Using existing Pydantic models plus SQLAlchemy models for persistence.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system.*

### Property 1: VIP sender round-trip persistence

*For any* valid email address or domain, adding it as a VIP sender and then querying VIP senders SHALL return that email/domain in the list.

**Validates: Requirements 3.2, 5.2**

### Property 2: Keyword rule round-trip persistence

*For any* valid keyword string, adding it as a keyword rule and then querying keywords SHALL return that keyword in the list.

**Validates: Requirements 4.2, 5.3**

### Property 3: VIP sender classification override

*For any* email from a sender matching a VIP sender entry, the classification SHALL be URGENT regardless of email content.

**Validates: Requirements 3.4**

### Property 4: Keyword classification override

*For any* email containing a configured keyword in subject or snippet, the classification SHALL be URGENT.

**Validates: Requirements 4.4**

### Property 5: Alert history filter correctness

*For any* filter applied to alert history (by urgency or search term), all returned results SHALL match the filter criteria.

**Validates: Requirements 2.3, 2.4**

### Property 6: Delete removes from database

*For any* VIP sender or keyword that is deleted, subsequent queries SHALL NOT return that item.

**Validates: Requirements 3.3, 4.3**

## Error Handling

| Error | Handling |
|-------|----------|
| Database connection failure | Display error page, log error |
| Duplicate VIP sender | Show "already exists" message |
| Duplicate keyword | Show "already exists" message |
| Invalid email format | Show validation error |
| Empty keyword | Reject with validation error |

## Testing Strategy

### Unit Tests
- Test CRUD operations with test database
- Test VIP/keyword matching logic
- Test pagination calculations

### Property-Based Tests (using Hypothesis)
- Property 1-2: Generate random emails/keywords, verify round-trip
- Property 3-4: Generate emails, verify classification override
- Property 5: Generate filters, verify result correctness
- Property 6: Add then delete, verify removal

### Integration Tests
- Test web routes with test client
- Test full flow: add VIP → check email → verify URGENT

### Configuration
- Use pytest with test PostgreSQL database
- Minimum 100 iterations for property tests
