# Technical Architecture

## Technology Stack
- **Language**: Python 3.11+
- **AI Framework**: CrewAI for multi-agent orchestration
- **LLM**: OpenAI GPT-4o-mini
- **Backend**: FastAPI (async, modern, auto-docs)
- **CLI**: Typer (modern Python CLI framework)
- **Web**: FastAPI + Jinja2 templates
- **Database**: PostgreSQL (via Railway)
- **SMS**: Twilio API
- **Email**: Gmail API (OAuth 2.0)
- **Deployment**: Railway

## Architecture Overview
```
┌─────────────────────────────────────────────────────────┐
│                      Railway                             │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │  FastAPI    │     │  Background │     │ PostgreSQL│ │
│  │  (Web/API)  │     │   Worker    │     │    DB     │ │
│  └─────────────┘     └─────────────┘     └───────────┘ │
└─────────────────────────────────────────────────────────┘

Agent Architecture:
┌──────────────┐    ┌──────────────┐    ┌────────────┐
│   Monitor    │───▶│  Classifier  │───▶│   Alert    │
│    Agent     │    │    Agent     │    │   Agent    │
└──────────────┘    └──────────────┘    └────────────┘
```

## Development Environment
- Python 3.11+
- Poetry or pip for dependency management
- PostgreSQL (local or Railway)
- Environment variables via .env file
- VS Code or Kiro IDE

## Code Standards
- PEP 8 compliance
- Type hints required (mypy compatible)
- Docstrings for public functions
- Black for formatting
- isort for imports
- Async/await for I/O operations

## Testing Strategy
- pytest for unit tests
- pytest-asyncio for async tests
- Minimum 70% coverage for core logic
- Mock external APIs (Gmail, Twilio, OpenAI) in tests

## Deployment Process
- GitHub repo connected to Railway
- Auto-deploy on push to main
- Environment variables in Railway dashboard
- PostgreSQL provisioned via Railway

## Performance Requirements
- Email check latency: <5 seconds
- Classification time: <10 seconds
- SMS delivery: <30 seconds after classification
- API response time: <500ms
- Support 100+ emails/day per user

## Security Considerations
- OAuth 2.0 for Gmail (no password storage)
- API keys in environment variables only
- HTTPS for all endpoints
- Database credentials via Railway secrets
- No PII logged (email content not stored long-term)
