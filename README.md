# ProjectX - Smart Notification Bridge

> Stay focused at work without missing what matters.

ProjectX monitors your Gmail inbox and Telegram messages, uses AI agents to detect urgent messages, and forwards alerts via SMS to your basic keypad phone. Perfect for developers and students who want to minimize smartphone distractions during work hours.

## 🎯 The Problem

You want to focus during work hours. Smartphones are distracting. But you can't miss urgent emails or messages from college, work, or family.

## 💡 The Solution

A smart notification bridge that:
1. **Monitors** your Gmail inbox and Telegram messages in real-time
2. **Evaluates** each message using AI agents
3. **Alerts** you via SMS when something is truly urgent
4. **Gives you control** via CLI and web dashboard

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌────────────┐
│   Monitor    │───▶│  Classifier  │───▶│   Alert    │
│    Agent     │    │    Agent     │    │   Agent    │
└──────────────┘    └──────────────┘    └────────────┘
      │                    │                   │
Gmail/Telegram       LLM (GPT-4o)          Twilio
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or 3.12 (NOT 3.13 - CrewAI compatibility)
- Gmail account
- Telegram account (for Telegram monitoring)
- Twilio account
- OpenRouter/OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/projectx
cd projectx

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Telegram Setup

1. Go to https://my.telegram.org/apps and create an app
2. Note your `api_id` and `api_hash`
3. Generate a session string:
   ```bash
   python scripts/generate_telegram_session.py
   ```
4. Add credentials to `.env`:
   ```
   TELEGRAM_API_ID=your-api-id
   TELEGRAM_API_HASH=your-api-hash
   TELEGRAM_SESSION=your-session-string
   ```

### Running

```bash
# Start the server (includes Telegram monitoring)
uvicorn src.main:app --reload

# Or use the CLI
projectx status
projectx check
projectx test
```

## 📱 CLI Commands

```bash
projectx status      # Check server and pipeline status
projectx check       # Trigger email check
projectx test        # Send test urgent SMS
projectx config show # Show configuration
```

## 🌐 Web Dashboard

Access at `http://localhost:8000` to:
- View dashboard with stats
- See alert history (email + Telegram)
- Manage VIP senders
- Configure keyword rules

## 🛠️ Tech Stack

- **AI Agents**: CrewAI (with fallback)
- **LLM**: OpenAI GPT-4o-mini via OpenRouter
- **Backend**: FastAPI
- **CLI**: Typer
- **Database**: PostgreSQL
- **SMS**: Twilio
- **Email**: Gmail API
- **Telegram**: Telethon (MTProto API)
- **Deployment**: Railway

## 📝 Development

```bash
# Run tests
pytest

# Format code
black src/ cli/ tests/
isort src/ cli/ tests/
```

## 🚢 Deployment

Deployed on Railway. Required environment variables:
- `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `ALERT_PHONE_NUMBER`
- `DATABASE_URL`
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION`

## 📄 License

MIT

---

Built for the Dynamous + Kiro Hackathon 2026
