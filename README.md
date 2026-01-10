# ProjectX - Smart Notification Bridge

> Stay focused at work without missing what matters.

ProjectX monitors your Gmail inbox, uses AI agents to detect urgent messages, and forwards alerts via SMS to your basic keypad phone. Perfect for developers and students who want to minimize smartphone distractions during work hours.

## 🎯 The Problem

You want to focus during work hours. Smartphones are distracting. But you can't miss urgent emails from college, work, or family.

## 💡 The Solution

A smart notification bridge that:
1. **Monitors** your Gmail inbox in real-time
2. **Evaluates** each email using AI agents
3. **Alerts** you via SMS when something is truly urgent
4. **Gives you control** via CLI and web dashboard

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌────────────┐
│   Monitor    │───▶│  Classifier  │───▶│   Alert    │
│    Agent     │    │    Agent     │    │   Agent    │
└──────────────┘    └──────────────┘    └────────────┘
      │                    │                   │
  Gmail API          LLM (GPT-4o)          Twilio
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Gmail account
- Twilio account
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/projectx
cd projectx

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

1. Set up Gmail OAuth credentials in Google Cloud Console
2. Get Twilio credentials from Twilio Console
3. Get OpenAI API key from OpenAI Platform
4. Update `.env` with all credentials

### Running

```bash
# Start the web server
uvicorn src.main:app --reload

# Or use the CLI
projectx status
projectx start
projectx pause
```

## 📱 CLI Commands

```bash
projectx status      # Check monitoring status
projectx start       # Start email monitoring
projectx pause       # Pause monitoring
projectx resume      # Resume monitoring
projectx history     # View alert history
projectx add-vip     # Add VIP sender
projectx test        # Send test SMS
```

## 🌐 Web Dashboard

Access at `http://localhost:8000` to:
- Connect your Gmail account
- Configure urgency rules
- Manage VIP sender list
- View alert history

## 🛠️ Tech Stack

- **AI Agents**: CrewAI
- **LLM**: OpenAI GPT-4o-mini
- **Backend**: FastAPI
- **CLI**: Typer
- **Database**: PostgreSQL
- **SMS**: Twilio
- **Email**: Gmail API

## 📝 Development

```bash
# Run tests
pytest

# Format code
black src/ cli/ tests/
isort src/ cli/ tests/

# Type checking
mypy src/ cli/

# Linting
ruff check src/ cli/ tests/
```

## 🚢 Deployment

Deployed on Railway. See `railway.toml` for configuration.

## 📄 License

MIT

---

Built for the Dynamous + Kiro Hackathon 2026
