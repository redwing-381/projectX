# Project Structure

## Directory Layout
```
projectx/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration and settings
│   ├── agents/              # CrewAI agents
│   │   ├── __init__.py
│   │   ├── monitor.py       # Email monitor agent
│   │   ├── classifier.py    # Urgency classifier agent
│   │   ├── alerter.py       # SMS alert agent
│   │   └── crew.py          # Crew orchestration
│   ├── api/                 # FastAPI routes
│   │   ├── __init__.py
│   │   ├── routes.py        # API endpoints
│   │   └── auth.py          # OAuth handlers
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── gmail.py         # Gmail API integration
│   │   ├── twilio.py        # Twilio SMS integration
│   │   └── rules.py         # Urgency rules engine
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── db/                  # Database
│   │   ├── __init__.py
│   │   ├── database.py      # DB connection
│   │   └── crud.py          # CRUD operations
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── dashboard.html
│       └── settings.html
├── cli/
│   ├── __init__.py
│   └── main.py              # Typer CLI app
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_api.py
│   └── test_services.py
├── .kiro/
│   ├── steering/
│   └── prompts/
├── .env.example
├── .gitignore
├── Dockerfile
├── pyproject.toml
├── README.md
├── DEVLOG.md
└── railway.toml
```

## File Naming Conventions
- Python files: snake_case (e.g., `gmail_service.py`)
- Classes: PascalCase (e.g., `EmailMonitorAgent`)
- Functions: snake_case (e.g., `check_new_emails`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- Templates: snake_case.html (e.g., `dashboard.html`)

## Module Organization
- `src/agents/`: CrewAI agent definitions and crew orchestration
- `src/api/`: FastAPI routes and request handlers
- `src/services/`: External API integrations (Gmail, Twilio)
- `src/models/`: Pydantic schemas and database models
- `src/db/`: Database connection and CRUD operations
- `cli/`: Typer CLI application (separate from web)

## Configuration Files
- `.env`: Environment variables (not committed)
- `.env.example`: Template for environment variables
- `pyproject.toml`: Python dependencies and project metadata
- `railway.toml`: Railway deployment configuration
- `Dockerfile`: Container definition

## Documentation Structure
- `README.md`: Project overview, setup, usage
- `DEVLOG.md`: Development timeline and decisions
- `.kiro/steering/`: Kiro context documents
- Inline docstrings for code documentation

## Build Artifacts
- `dist/`: Built packages (if any)
- `.pytest_cache/`: Test cache
- `__pycache__/`: Python bytecode
- `.mypy_cache/`: Type checking cache

## Environment-Specific Files
- `.env.development`: Local development settings
- `.env.production`: Production settings (Railway)
- Environment variables override config defaults
