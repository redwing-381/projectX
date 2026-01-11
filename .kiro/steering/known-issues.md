# Known Issues and Solutions

## Python Environment

### Virtual Environment Activation
Always activate the virtual environment before running commands:
```bash
source .venv/bin/activate && <command>
```

### Port Already in Use
If uvicorn fails with "Address already in use":
```bash
pkill -f uvicorn
# or for specific port
lsof -ti:8000 | xargs kill -9
```

## CrewAI Integration

### Python 3.13 Compatibility Issue
**Status:** CrewAI 1.8.0 does NOT work with Python 3.13

**Root Cause:** LiteLLM (required by CrewAI) uses the deprecated `cgi` module which was removed in Python 3.13.

**Error:**
```
ModuleNotFoundError: No module named 'cgi'
```

**Workarounds:**
1. Use Python 3.11 or 3.12 for full CrewAI support
2. Use the fallback mechanism in `main.py` (direct ClassifierAgent)

### Dependency Version Conflicts
CrewAI has strict version requirements. Known compatible versions:
- `crewai==1.8.0`
- `openai~=1.83.0`
- `litellm>=1.50.0,<1.60.0`

Do NOT install `litellm>=1.80.0` as it requires `openai>=2.8.0` which conflicts with crewai.

## Railway Deployment

### Port Configuration
Railway provides `$PORT` environment variable. Use shell expansion:
```toml
startCommand = "sh -c 'uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}'"
```

### Environment Variables
All secrets must be set in Railway dashboard, not in code:
- LLM_API_KEY
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- etc.

## Testing Locally

### Start Server
```bash
source .venv/bin/activate && uvicorn src.main:app --reload --port 8000
```

### Test Endpoints
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/test-urgent
curl -X POST http://localhost:8000/check
```
