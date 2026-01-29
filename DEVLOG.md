<div align="center">

# Development Log

### ProjectX - Smart Notification Bridge

**Duration**: January 11-28, 2026  
**Hackathon**: Dynamous + Kiro Hackathon

</div>

---

## At a Glance

<div align="center">

| Metric | Value |
|:------:|:-----:|
| Development Period | 18 days |
| Lines of Code | 8,000+ |
| Property Tests | 17 |
| Feature Specs | 8 |
| Deployment | Railway |

</div>

---

## What We Built

A smart notification bridge that monitors Gmail and Android app notifications (WhatsApp, Telegram, etc.), uses AI to detect urgent messages, and forwards alerts via SMS to a basic keypad phone.

<div align="center">
<img src="docs/images/projectx_architecture.png" alt="Architecture" width="800"/>
</div>

---

## Tech Stack

<div align="center">

| Component | Technology |
|:---------:|:----------:|
| Backend | FastAPI (Python 3.11) |
| AI/LLM | GPT-4o-mini via OpenRouter |
| AI Framework | CrewAI (with fallback) |
| Database | PostgreSQL (Railway) |
| SMS | Twilio API |
| Email | Gmail API (OAuth 2.0) |
| Mobile | Native Android (Kotlin) |
| CLI | Typer + Rich |

</div>

---

## Key Features

- Multi-source monitoring (Gmail + Android notifications)
- AI-powered urgency classification with VIP/keyword fast-path
- SMS alerts to keypad phone
- Web dashboard with analytics
- CLI tool (`pip install projectx-cli`)
- Cross-platform monitoring control

---

## The Classification Pipeline

<div align="center">
<img src="docs/images/classification.png" alt="Classification Pipeline" width="800"/>
</div>

---

## Development Timeline

<div align="center">

| Date | Milestone |
|:----:|:----------|
| Jan 11 | Project ideation, MVP, Gmail + Twilio working |
| Jan 11 | CrewAI integration, property tests, CLI tool |
| Jan 11 | Web dashboard, PostgreSQL, Railway deployment |
| Jan 12 | API key authentication, CLI published to PyPI |
| Jan 16 | Android notification monitor app |
| Jan 17 | UI overhaul, codebase modularization |
| Jan 17 | Cross-platform monitoring control |
| Jan 28 | Final polish, analytics, demo ready |

</div>

---

## Challenges & Solutions

<div align="center">

| Challenge | Solution |
|:---------:|:---------|
| Python 3.13 + CrewAI | Built fallback classifier |
| WhatsApp API restrictions | Android NotificationListener |
| Railway DNS issues | Cloudflare DNS workaround |
| Jinja2 linter errors | Data attributes pattern |

</div>

---

## Live URLs

<div align="center">

| Resource | Link |
|:--------:|:-----|
| Web Dashboard | https://projectx-solai.up.railway.app |
| CLI Package | `pip install projectx-cli` |

</div>

---

<div align="center">

# Detailed Timeline

</div>

---

## January 11, 2026

### The Idea

> *As a final year student doing a software engineering internship, I want to use a basic keypad phone during work hours for focus, but I can't completely disconnect — urgent emails from college/work need to reach me.*

This personal problem became the project.

---

### What's Possible vs What's Not

<div align="center">

**Can Monitor:**

| Source | API Access |
|:------:|:----------:|
| Gmail | ✅ Full access |
| Outlook | ✅ Full access |
| Telegram | ✅ Full access |
| Twilio SMS | ✅ Full access |

**Cannot Monitor (API Restrictions):**

| Source | Issue |
|:------:|:------|
| WhatsApp | No personal API, ban risk |
| Instagram | No DM access |
| X/Twitter | Paid tier required |

</div>

**Decision:** Focus on email first, solve WhatsApp later with Android app.

---

### Tech Stack Decision

Evaluated multiple options:

| Category | Options Considered | Choice |
|:--------:|:-------------------|:------:|
| AI Framework | LangChain, LangGraph, CrewAI, AutoGen | **CrewAI** |
| Deployment | Railway, Render, Cloud Run, Fly.io | **Railway** |
| CLI | Click, Argparse, Typer | **Typer** |

**Why CrewAI?** Clear agent roles, easy to explain in demo, good docs.

**Why Railway?** Always-on (no cold starts), simple setup, good free tier.

---

### MVP Implementation

Built the core in one day:

```
✅ Config and models (~10 min)
✅ Gmail Service (~15 min)
✅ Classifier Agent (~15 min)
✅ Twilio Service (~10 min)
✅ Pipeline Orchestrator (~10 min)
✅ FastAPI endpoints (~15 min)
```

**Total MVP time:** ~75 minutes

---

### MVP Testing

```bash
POST /check → 10 emails checked, 0 alerts (all correctly NOT_URGENT)
POST /test-urgent → SMS sent successfully to keypad phone!
```

**Result:** MVP fully functional on day 1.

---

### CrewAI Integration

**Problem:** Python 3.13 breaks CrewAI due to removed `cgi` module in LiteLLM.

```
ModuleNotFoundError: No module named 'cgi'
```

**Solution:** Built fallback mechanism — try CrewAI, fall back to direct classifier.

```python
try:
    classifier = EmailProcessingCrew(...)
except Exception:
    classifier = ClassifierAgent(...)  # Fallback
```

---

### Property-Based Tests

Implemented 17 tests using Hypothesis:

- Classification output validity
- SMS format validity (≤160 chars)
- Pipeline result schema conformance
- Error handling graceful degradation

```bash
17 passed in 1.94s
```

---

### CLI Published to PyPI

```bash
pip install projectx-cli
projectx status
projectx check
projectx test
```

**PyPI URL:** https://pypi.org/project/projectx-cli/

---

### Web Dashboard Deployed

- Dashboard with stats
- Alert history with pagination
- VIP senders management
- Keywords management
- Settings page

**Live:** https://projectx-solai.up.railway.app

---

## January 12, 2026

### API Key Authentication

**Problem:** Anyone with the URL could access the API.

**Solution:** Added Bearer token authentication.

```bash
projectx login   # Enter API key
projectx check   # Now authenticated
projectx logout  # Remove saved key
```

---

## January 16, 2026

### Android App - The WhatsApp Solution

**Problem:** WhatsApp has no personal messaging API.

**Solution:** Built an Android app using `NotificationListenerService` to capture notifications from ANY app.

<div align="center">
<img src="docs/images/android_app.png" alt="Android App" width="300"/>
</div>

```
mobile-app/
├── MainActivity.kt
├── service/NotificationService.kt
├── api/ProjectXApiClient.kt
├── worker/SyncWorker.kt
└── data/
    ├── Models.kt
    ├── SupportedApps.kt
    └── NotificationRepository.kt
```

**Supported Apps:**
- WhatsApp
- Telegram
- Instagram
- Slack
- Discord
- Messenger
- SMS

---

## January 17, 2026

### UI Overhaul

- Removed Telegram userbot (replaced by Android app)
- Added notifications page with source filtering
- Added architecture visualization page
- Professional sidebar layout
- Neutral color scheme (no emojis)

---

### Codebase Modularization

Refactored 700+ line `web.py` into modular routes:

```
src/api/routes/
├── dashboard.py
├── history.py
├── settings.py
├── vip_senders.py
├── keywords.py
├── notifications.py
├── architecture.py
├── mobile_api.py
└── monitoring_api.py
```

Each file under 100 lines.

---

### Cross-Platform Monitoring Control

Start/stop monitoring from anywhere:

```bash
# CLI
projectx monitor start --all
projectx monitor stop --all

# Web
Settings → Unified Monitoring Control

# Mobile
App polls for remote commands
```

---

### Performance Optimizations

- In-memory caching (30s TTL)
- Database connection pooling
- GZip compression middleware
- Async Gmail API calls

---

## January 28, 2026

### Final Polish

- Neutral color palette
- Analytics source breakdown
- Fixed chart rendering
- Demo mode for presentations

---

## Analytics Dashboard

<div align="center">
<img src="docs/images/analytics.png" alt="Analytics" width="800"/>
</div>

---

## CLI Tool

<div align="center">
<img src="docs/images/cli.png" alt="CLI" width="700"/>
</div>

---

## Lessons Learned

1. **Always build fallbacks** — CrewAI failed on Python 3.13, but the fallback saved the project
2. **API restrictions aren't blockers** — WhatsApp has no API, so we captured notifications instead
3. **Spec-driven development works** — 8 specs kept the project organized
4. **Property tests catch edge cases** — Hypothesis found issues unit tests missed

---

## What's Next

- Voice control via keypad phone calls
- Reply to messages via voice commands
- Full personal assistant agent

---

<div align="center">

**Built with Kiro for the Dynamous + Kiro Hackathon 2026**

*Stay focused. Stay reachable.*

</div>
