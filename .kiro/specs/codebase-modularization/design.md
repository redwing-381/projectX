# Codebase Modularization Design

## Architecture

### New Directory Structure
```
src/
├── api/
│   ├── __init__.py
│   ├── deps.py              # Shared dependencies (db, auth)
│   └── routes/
│       ├── __init__.py
│       ├── dashboard.py     # GET /, POST /web/check
│       ├── history.py       # GET /history
│       ├── settings.py      # GET /settings, POST /settings/*
│       ├── vip_senders.py   # GET/POST /vip-senders/*
│       ├── keywords.py      # GET/POST /keywords/*
│       ├── notifications.py # GET /notifications
│       ├── architecture.py  # GET /architecture
│       ├── mobile_api.py    # POST /api/notifications
│       └── monitoring_api.py # GET/POST /api/monitoring/*
├── services/
│   ├── notification_service.py  # Mobile notification processing
│   └── monitoring_service.py    # Monitoring control logic
└── models/
    └── schemas.py           # All Pydantic models
```

## Component Design

### 1. Dependencies Module (`src/api/deps.py`)
```python
from typing import Generator
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.config import get_settings

security = HTTPBearer(auto_error=False)

def get_db() -> Generator[Session, None, None]:
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """API key verification dependency."""
    settings = get_settings()
    if not settings.api_key:
        return True
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    if credentials.credentials != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True
```

### 2. Route Module Pattern
Each route module follows this pattern:
```python
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.api.deps import get_db, verify_api_key

router = APIRouter()

@router.get("/path")
async def handler(request: Request, db: Session = Depends(get_db)):
    # Route logic using injected db session
    pass
```

### 3. Service Layer Pattern
```python
# src/services/notification_service.py
from sqlalchemy.orm import Session
from src.db import crud
from src.models.schemas import NotificationBatchRequest, NotificationBatchResponse

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def process_batch(self, request: NotificationBatchRequest) -> NotificationBatchResponse:
        # Business logic here
        pass
```

### 4. Router Registration
```python
# src/api/__init__.py
from fastapi import APIRouter
from src.api.routes import (
    dashboard, history, settings, vip_senders,
    keywords, notifications, architecture,
    mobile_api, monitoring_api
)

router = APIRouter()
router.include_router(dashboard.router)
router.include_router(history.router)
# ... etc
```

## Migration Strategy

1. Create `src/api/deps.py` with shared dependencies
2. Create `src/api/routes/` directory structure
3. Move routes one module at a time (dashboard first)
4. Update imports in `src/main.py`
5. Delete old `src/api/web.py`
6. Add service layer for complex logic
7. Update steering docs

## Backward Compatibility
- All URL paths remain unchanged
- API contracts unchanged
- No database schema changes
