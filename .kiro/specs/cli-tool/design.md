# Design Document: CLI Tool

## Overview

A Typer-based command-line interface that acts as a thin API client for the ProjectX server. The CLI enables developers to check server status, trigger email checks, test the classification flow, and manage configuration—all without leaving the terminal.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Terminal                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  $ projectx status    $ projectx check    $ projectx test       │
│         │                    │                   │               │
│         └────────────────────┼───────────────────┘               │
│                              ▼                                   │
│                    ┌──────────────────┐                         │
│                    │   Typer CLI App  │                         │
│                    │   (cli/main.py)  │                         │
│                    └────────┬─────────┘                         │
│                             │                                    │
│                    ┌────────▼─────────┐                         │
│                    │   API Client     │                         │
│                    │ (cli/client.py)  │                         │
│                    └────────┬─────────┘                         │
│                             │ HTTP                               │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Railway Server  │
                    │   (FastAPI)      │
                    └──────────────────┘
```

## Components and Interfaces

### 1. CLI Application (`cli/main.py`)

```python
import typer
from rich.console import Console

app = typer.Typer(
    name="projectx",
    help="Smart notification bridge - CLI for ProjectX",
)
console = Console()

@app.command()
def status(json_output: bool = typer.Option(False, "--json")):
    """Check if the ProjectX server is running."""
    pass

@app.command()
def check(json_output: bool = typer.Option(False, "--json")):
    """Trigger an email check and display results."""
    pass

@app.command()
def test(json_output: bool = typer.Option(False, "--json")):
    """Test the urgency classification with a sample email."""
    pass

@app.command()
def config():
    """Manage CLI configuration."""
    pass
```

### 2. API Client (`cli/client.py`)

```python
import httpx
from typing import Optional

class ProjectXClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
    
    def health(self) -> dict:
        """GET /health - Check server health."""
        response = httpx.get(f"{self.base_url}/health", timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def status(self) -> dict:
        """GET /status - Get detailed status."""
        response = httpx.get(f"{self.base_url}/status", timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def check(self) -> dict:
        """POST /check - Trigger email check."""
        response = httpx.post(f"{self.base_url}/check", timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def test_urgent(self) -> dict:
        """POST /test-urgent - Test classification flow."""
        response = httpx.post(f"{self.base_url}/test-urgent", timeout=self.timeout)
        response.raise_for_status()
        return response.json()
```

### 3. Configuration Manager (`cli/config.py`)

```python
import json
from pathlib import Path
from pydantic import BaseModel

CONFIG_DIR = Path.home() / ".projectx"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_URL = "https://projectx-production-0eeb.up.railway.app"

class CLIConfig(BaseModel):
    server_url: str = DEFAULT_URL

def load_config() -> CLIConfig:
    """Load configuration from file or return defaults."""
    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text())
        return CLIConfig(**data)
    return CLIConfig()

def save_config(config: CLIConfig) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(config.model_dump_json(indent=2))
```

## Data Models

```python
# Response models for type safety
class HealthResponse(BaseModel):
    status: str
    app_name: str

class StatusResponse(BaseModel):
    status: str
    pipeline_ready: bool
    startup_error: Optional[str]

class CheckResponse(BaseModel):
    success: bool
    message: str
    data: PipelineResult

class TestResponse(BaseModel):
    success: bool
    message: str
    data: dict  # Contains email, classification, sms_sent, sms_error
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do.*

### Property 1: Configuration round-trip

*For any* valid URL string, setting the URL via `config set-url` and then retrieving it via `config show` SHALL return the same URL.

**Validates: Requirements 4.1**

### Property 2: Check response display completeness

*For any* successful check response containing emails_checked, alerts_sent, and a list of results, the CLI output SHALL contain all these values and each alert's sender and subject.

**Validates: Requirements 2.2, 2.3**

### Property 3: JSON output validity

*For any* command executed with the `--json` flag, the output SHALL be valid JSON that can be parsed without errors.

**Validates: Requirements 5.4**

### Property 4: Error message safety

*For any* error condition (network failure, HTTP error, or exception), the CLI output SHALL NOT contain Python stack traces when running without --debug flag.

**Validates: Requirements 6.1, 6.2, 6.4**

### Property 5: Classification display completeness

*For any* test-urgent response containing urgency and reason, the CLI output SHALL display both the urgency level and the reason text.

**Validates: Requirements 3.2**

## Error Handling

| Error | Handling |
|-------|----------|
| Network timeout | Display "Connection failed: Request timed out" |
| Connection refused | Display "Connection failed: Server unreachable" |
| HTTP 4xx | Display error detail from response body |
| HTTP 5xx | Display "Server error: <detail>" |
| Invalid JSON response | Display "Invalid response from server" |
| Missing config | Prompt to run `projectx config set-url` |

## Testing Strategy

### Unit Tests
- Test config load/save with various URLs
- Test API client methods with mocked responses
- Test CLI output formatting
- Test error handling for various failure modes

### Property-Based Tests (using Hypothesis)
- Property 1: Generate random valid URLs, verify round-trip
- Property 2: Generate random check responses, verify output completeness
- Property 3: Run commands with --json, verify JSON validity
- Property 4: Generate various errors, verify no stack traces
- Property 5: Generate classification responses, verify display

### Integration Tests
- Test full CLI commands against mock server
- Test real server connectivity (manual)

### Configuration
- Use pytest with typer.testing.CliRunner
- Mock httpx for API client tests
- Minimum 100 iterations for property tests
