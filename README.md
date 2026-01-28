# ProjectX

**Smart Notification Bridge for Focus Mode**

ProjectX monitors your Gmail inbox and Android app notifications (WhatsApp, Telegram, etc.), uses AI to detect urgent messages, and forwards alerts via SMS to a basic keypad phone. Stay focused during work hours without missing critical communications.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Mobile App](#mobile-app)
- [Deployment](#deployment)
- [Development](#development)
- [License](#license)

---

## Overview

### The Problem

You want to focus during work hours. Smartphones are distracting. But you can't miss urgent emails or messages from college, work, or family.

### The Solution

A smart notification bridge that:

1. **Monitors** your Gmail inbox and Android app notifications in real-time
2. **Classifies** each message using AI (GPT-4o-mini) with VIP/keyword fast-path
3. **Alerts** you via SMS when something is truly urgent
4. **Gives you control** via CLI, web dashboard, and mobile app

---

## Features

| Feature | Description |
|---------|-------------|
| Multi-Source Monitoring | Gmail + Android notifications (WhatsApp, Telegram, Slack, Discord, SMS, Messenger) |
| AI Classification | GPT-4o-mini powered urgency detection with VIP sender and keyword fast-path |
| SMS Alerts | Twilio integration sends condensed alerts to any phone |
| Web Dashboard | Analytics, history, VIP/keyword management, architecture visualization |
| CLI Tool | Terminal commands for status checks and monitoring control |
| Mobile App | Native Android app for notification capture and sync |
| Cross-Platform Control | Start/stop monitoring from any interface (Web, CLI, Mobile) |

---

## Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Data Sources   │────▶│   FastAPI        │────▶│  AI Classifier   │────▶│   SMS Alert      │
│                  │     │   Backend        │     │  (GPT-4o-mini)   │     │   (Twilio)       │
│  - Gmail API     │     │                  │     │                  │     │                  │
│  - Android App   │     │  - REST API      │     │  - VIP Check     │     │  - Format SMS    │
│                  │     │  - Web Dashboard │     │  - Keyword Match │     │  - Send to Phone │
└──────────────────┘     └────────┬─────────┘     │  - LLM Fallback  │     └──────────────────┘
                                  │               └──────────────────┘
                         ┌────────▼─────────┐
                         │   PostgreSQL     │
                         │                  │
                         │  - Alert History │
                         │  - VIP Senders   │
                         │  - Keywords      │
                         │  - Devices       │
                         └──────────────────┘
```

### Classification Pipeline

```
Incoming Message
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  VIP Check   │────▶│   Keyword    │────▶│     LLM      │
│  (instant)   │     │   Match      │     │  Analysis    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
   URGENT              URGENT              URGENT/NOT_URGENT
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.11) |
| AI/LLM | GPT-4o-mini via OpenRouter |
| AI Framework | CrewAI (with fallback classifier) |
| Database | PostgreSQL |
| SMS | Twilio API |
| Email | Gmail API (OAuth 2.0) |
| Mobile | Native Android (Kotlin) |
| CLI | Typer + Rich |
| Deployment | Railway |

---

## Getting Started

### Prerequisites

- Python 3.11 or 3.12 (NOT 3.13 due to CrewAI compatibility)
- Gmail account with API access
- Twilio account for SMS
- OpenRouter API key (or OpenAI)
- PostgreSQL database

### Installation

```bash
# Clone the repository
git clone https://github.com/redwing-381/projectx
cd projectx

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
```

### Quick Start

```bash
# Start the server
source .venv/bin/activate && uvicorn src.main:app --reload --port 8000

# Access the dashboard
open http://localhost:8000
```

---

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
LLM_API_KEY=your-openrouter-or-openai-key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini
DATABASE_URL=postgresql://user:pass@host:5432/dbname
API_KEY=your-generated-api-key

# Gmail OAuth
GMAIL_CREDENTIALS_FILE=credentials.json

# SMS Alerts
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBER=+0987654321
```

### Gmail Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json` to project root
5. Run the server and complete OAuth flow in browser

---

## Usage

### Web Dashboard

Access at `http://localhost:8000` (or your deployed URL):

- **Dashboard** - Stats, recent alerts, quick actions
- **Notifications** - Filter by source (WhatsApp, Email, etc.)
- **History** - Paginated alert history with filters
- **VIP Senders** - Manage priority contacts
- **Keywords** - Configure urgency trigger words
- **Architecture** - System visualization
- **Settings** - Monitoring controls, device management
- **Analytics** - Charts and source breakdown

### CLI Tool

Install from PyPI:

```bash
pip install projectx-cli
```

Commands:

```bash
# Authentication
projectx login              # Enter API key
projectx logout             # Remove saved key

# Status
projectx status             # Server and pipeline status
projectx help               # List all commands

# Email Operations
projectx check              # Trigger email check
projectx test               # Send test urgent SMS

# Monitoring Control
projectx monitor status     # Show monitoring status
projectx monitor start      # Enable email monitoring
projectx monitor stop       # Disable email monitoring
projectx monitor start --all  # Start all platforms
projectx monitor stop --all   # Stop all platforms
projectx monitor set-interval 5  # Set check interval (minutes)

# Configuration
projectx config show        # Display configuration
projectx config set-url URL # Set server URL
```

---

## API Reference

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/status` | Pipeline status |

### Protected Endpoints (require API key)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/check` | Trigger email check |
| POST | `/test-urgent` | Send test SMS |
| GET | `/api/monitoring` | Get monitoring status |
| POST | `/api/monitoring/start` | Enable monitoring |
| POST | `/api/monitoring/stop` | Disable monitoring |
| POST | `/api/monitoring/interval` | Set check interval |
| GET | `/api/monitoring/unified` | Get all platform status |
| POST | `/api/monitoring/start-all` | Start all platforms |
| POST | `/api/monitoring/stop-all` | Stop all platforms |
| POST | `/api/notifications` | Mobile app notification sync |

### Authentication

Include API key in request header:

```
Authorization: Bearer your-api-key
```

---

## Mobile App

The Android app captures notifications from messaging apps and syncs them to the backend.

### Supported Apps

- WhatsApp
- Instagram
- Telegram
- Slack
- Discord
- Facebook Messenger
- SMS

### Features

- Notification capture via `NotificationListenerService`
- Local queuing with duplicate detection
- Background sync via WorkManager
- Configurable sync interval
- Remote start/stop from web/CLI

### Setup

1. Build APK from `mobile-app/` directory
2. Install on Android device
3. Grant notification access permission
4. Configure server URL and API key
5. Select apps to monitor

See `mobile-app/README.md` for detailed instructions.

---

## Deployment

### Railway

The project is configured for Railway deployment:

```bash
# railway.toml is pre-configured
railway up
```

Required environment variables in Railway dashboard:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `DATABASE_URL` (auto-provisioned with PostgreSQL add-on)
- `API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `ALERT_PHONE_NUMBER`

### Docker

```bash
docker build -t projectx .
docker run -p 8000:8000 --env-file .env projectx
```

---

## Development

### Project Structure

```
projectx/
├── src/
│   ├── agents/          # AI classification agents
│   ├── api/
│   │   ├── deps.py      # Shared dependencies
│   │   └── routes/      # Modular route handlers
│   ├── db/              # Database models and CRUD
│   ├── models/          # Pydantic schemas
│   ├── services/        # Gmail, Twilio, pipeline
│   └── templates/       # Jinja2 HTML templates
├── cli/                 # Typer CLI application
├── cli-package/         # PyPI distributable CLI
├── mobile-app/          # Android notification monitor
├── tests/               # Property-based tests
└── .kiro/               # Kiro IDE configuration
```

### Running Tests

```bash
source .venv/bin/activate && pytest
```

### Code Style

```bash
# Format code
black src/ cli/ tests/
isort src/ cli/ tests/

# Type checking
mypy src/
```

### Known Issues

- Python 3.13 is not supported (CrewAI/LiteLLM compatibility)
- Gmail token expires periodically - delete `token.json` to re-authenticate
- Some networks block Railway DNS - use Cloudflare DNS (1.1.1.1) or VPN

---

## License

MIT

---

## Links

- **Live Demo**: https://projectx-solai.up.railway.app
- **CLI Package**: https://pypi.org/project/projectx-cli/
- **Development Log**: See `DEVLOG.md` for detailed development history

---

Built for the Dynamous + Kiro Hackathon 2026
