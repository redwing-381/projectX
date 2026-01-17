# Project Structure

## Directory Layout
```
projectx/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration and settings
│   ├── agents/              # AI agents
│   │   ├── __init__.py
│   │   ├── classifier.py    # Direct urgency classifier
│   │   ├── crew.py          # CrewAI crew orchestration
│   │   ├── definitions.py   # CrewAI agent definitions
│   │   ├── tasks.py         # CrewAI task definitions
│   │   └── mobile_notification_agent.py  # Mobile notification classifier
│   ├── api/                 # FastAPI routes (modular)
│   │   ├── __init__.py
│   │   ├── deps.py          # Shared dependencies (db, auth)
│   │   └── routes/          # Route modules
│   │       ├── __init__.py
│   │       ├── dashboard.py
│   │       ├── history.py
│   │       ├── settings.py
│   │       ├── vip_senders.py
│   │       ├── keywords.py
│   │       ├── notifications.py
│   │       ├── architecture.py
│   │       ├── mobile_api.py
│   │       └── monitoring_api.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── gmail.py         # Gmail API integration
│   │   ├── twilio_sms.py    # Twilio SMS integration
│   │   └── pipeline.py      # Email processing pipeline
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models (ALL API models here)
│   ├── db/                  # Database
│   │   ├── __init__.py
│   │   ├── database.py      # DB connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── crud.py          # CRUD operations
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── dashboard.html
│       ├── history.html
│       ├── settings.html
│       ├── notifications.html
│       ├── architecture.html
│       ├── vip_senders.html
│       └── keywords.html
├── cli/
│   ├── __init__.py
│   └── main.py              # Typer CLI app
├── cli-package/             # Distributable CLI package
├── mobile-app/              # Android notification monitor
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── .kiro/
│   ├── steering/
│   ├── specs/
│   └── prompts/
├── .env.example
├── .gitignore
├── Dockerfile
├── pyproject.toml
├── README.md
├── DEVLOG.md
└── railway.toml
```

## Module Organization Rules

### Route Modules (`src/api/routes/`)
- One file per feature/page (max 100 lines)
- Use dependency injection via `src/api/deps.py`
- Import Pydantic models from `src/models/schemas.py`
- Never create SessionLocal() directly - use `Depends(get_db)`

### Dependencies (`src/api/deps.py`)
- Shared FastAPI dependencies
- Database session management
- Authentication/authorization
- Common utility functions

### Schemas (`src/models/schemas.py`)
- ALL Pydantic models in one place
- Request/response models
- Internal data transfer objects
- Keep models simple and focused

### Services (`src/services/`)
- Business logic layer
- External API integrations
- No HTTP concerns (no Request/Response)
- Can be used by routes and CLI

### CRUD (`src/db/crud.py`)
- Database operations only
- No business logic
- Simple, focused functions
- Type hints required

## File Size Limits
- Route modules: max 100 lines
- Service modules: max 200 lines
- CRUD modules: max 300 lines
- Any file exceeding limits should be split

## File Naming Conventions
- Python files: snake_case (e.g., `mobile_api.py`)
- Classes: PascalCase (e.g., `MobileNotificationAgent`)
- Functions: snake_case (e.g., `process_notifications`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- Templates: snake_case.html (e.g., `dashboard.html`)

## Import Order (isort)
1. Standard library
2. Third-party packages
3. Local imports (src.*)

## Configuration Files
- `.env`: Environment variables (not committed)
- `.env.example`: Template for environment variables
- `pyproject.toml`: Python dependencies and project metadata
- `railway.toml`: Railway deployment configuration
- `Dockerfile`: Container definition
