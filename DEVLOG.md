# Development Log - Digital Detox Gateway

**Project**: Digital Detox Gateway - Smart Notification Bridge for Focus Mode  
**Duration**: January 11-23, 2026  
**Hackathon**: Dynamous + Kiro Hackathon ($17,000 prize pool)

---

## January 11, 2026

### Brainstorming Session - Project Ideation [~1h]

**Initial exploration:**
- Reviewed hackathon requirements and judging criteria
- Considered web + CLI combo to maximize Kiro CLI Usage points (20%)
- Explored various ideas: snippet managers, task managers, API testers, etc.

**Rejected ideas:**
- Generic developer tools — too common, low innovation score
- Social media integrations — API access is restricted/risky

**The winning idea emerged from a personal problem:**

As a final year student doing a software engineering internship, I want to use a basic keypad phone during work hours for focus, but I can't completely disconnect — urgent emails from college/work need to reach me.

### Concept: Digital Detox Gateway

**The Problem:**
- Smartphones are distracting during work
- But you can't miss truly urgent messages
- Keypad phones have SMS/calls but no email/apps

**The Solution:**
A monitoring system that:
1. Watches email (Gmail API)
2. Detects urgent messages based on rules (VIP senders, keywords)
3. Forwards alerts via SMS to a basic keypad phone (Twilio)
4. Provides CLI for quick control while working at computer
5. Web dashboard for setup and history

### Technical Feasibility Analysis

**What's possible:**
| Source | API Access | Verdict |
|--------|-----------|---------|
| Gmail | ✅ Full access | Easy - primary focus |
| Outlook | ✅ Full access | Possible future addition |
| Telegram | ✅ Full access | Easy if needed |
| Twilio SMS | ✅ Full access | Easy - for alerts |

**What's NOT possible (documented for presentation):**
| Source | Issue | Verdict |
|--------|-------|---------|
| WhatsApp | No official API for personal accounts, ban risk | Skip |
| Instagram | No DM access via API | Skip |
| X/Twitter | DM access requires paid tier ($100+/month) | Skip |

**Decision:** Focus on email as primary source — it's where most important stuff lands anyway (college, work, family).

### CLI Justification

Initially questioned whether CLI makes sense, but realized:
- User is at computer during work hours
- CLI allows quick checks without breaking flow
- Commands: `status`, `pause`, `resume`, `history`, `add-vip`, `test`
- Less distracting than opening a web app

### Scope Definition

**MVP Features:**
- [ ] Email monitoring (Gmail API)
- [ ] Urgency rules (VIP senders, keyword matching)
- [ ] SMS alerts via Twilio
- [ ] CLI tool for control
- [ ] Web dashboard for setup

**Deferred:**
- WhatsApp/social media (API limitations)
- Call forwarding (too complex)
- Mobile app (defeats the purpose)

### Why This Idea Works for the Hackathon

✅ **Real-world value** — solves a genuine personal problem  
✅ **Unique angle** — digital detox for developers  
✅ **Web + CLI combo** — hits both interface requirements  
✅ **Achievable scope** — can be polished in timeframe  
✅ **Innovation** — not another todo app or code reviewer  

### Tech Stack Discussion

**AI Agent Framework options considered:**
- LangChain — too verbose for our needs
- LangGraph — good but steeper learning curve
- CrewAI — simple multi-agent setup, role-based ✅
- Pydantic AI — lightweight but less impressive for demo
- AutoGen — more research-oriented

**Decision:** CrewAI — clear agent roles, easy to explain in demo, good documentation.

**Deployment options considered:**
- Railway — simple, always-on, good free tier ✅
- Render — free tier sleeps (not ideal for monitoring)
- Cloud Run — request-based, would need scheduler
- Fly.io — good but more setup

**Decision:** Railway — simpler for hackathon, supports background workers.

### Final Tech Stack

| Component | Choice |
|-----------|--------|
| AI Agents | CrewAI |
| LLM | OpenAI GPT-4o-mini |
| Backend/API | FastAPI |
| CLI | Typer |
| Web Dashboard | FastAPI + Jinja2 |
| Database | PostgreSQL (Railway) |
| SMS | Twilio |
| Email | Gmail API |
| Deployment | Railway |

### Agent Architecture

```
┌──────────────┐    ┌──────────────┐    ┌────────────┐
│   Monitor    │───▶│  Classifier  │───▶│   Alert    │
│    Agent     │    │    Agent     │    │   Agent    │
└──────────────┘    └──────────────┘    └────────────┘
      │                    │                   │
  Gmail API          LLM (GPT-4o)          Twilio
```

### Original vs MVP Scope

**Original idea (future):**
- Email monitoring ✅
- WhatsApp monitoring ❌ (API risk)
- Instagram/X DMs ❌ (no API)
- Call forwarding ❌ (too complex)
- SMS alerts ✅

**MVP for hackathon:**
- Gmail monitoring + AI urgency detection + SMS alerts
- Web dashboard + CLI control

### Next Steps
- [ ] Set up project structure
- [ ] Configure Kiro steering documents
- [ ] Start with `@quickstart` wizard
- [ ] Plan architecture with `@plan-feature`

---


### Project Setup Complete

**Time spent:** ~30 min

**What was created:**

1. **Kiro Steering Documents** (`.kiro/steering/`)
   - `product.md` — Product overview, target users, features, success criteria
   - `tech.md` — Tech stack, architecture, code standards
   - `structure.md` — Directory layout, naming conventions

2. **Kiro Prompts** (`.kiro/prompts/`)
   - `prime.md` — Load project context
   - `plan-feature.md` — Create implementation plans
   - `execute.md` — Execute plans
   - `code-review.md` — Technical code review

3. **Project Structure**
   ```
   projectx/
   ├── src/
   │   ├── agents/      # CrewAI agents
   │   ├── api/         # FastAPI routes
   │   ├── services/    # Gmail, Twilio integrations
   │   ├── models/      # Pydantic schemas
   │   └── db/          # Database
   ├── cli/             # Typer CLI
   ├── tests/           # pytest tests
   ├── .kiro/           # Kiro config
   ├── pyproject.toml   # Dependencies
   ├── Dockerfile       # Container
   └── railway.toml     # Deployment
   ```

4. **Configuration Files**
   - `pyproject.toml` — All dependencies defined
   - `.env.example` — Environment variable template
   - `.gitignore` — Standard Python ignores
   - `Dockerfile` — Container definition
   - `railway.toml` — Railway deployment config
   - `README.md` — Project documentation

**Ready for:** Feature implementation using Kiro workflow

---

### Architecture Decision: CLI as API Client

**Decision:** Option A — CLI talks to deployed server

```
Any Machine                          Railway (Cloud)
┌─────────────┐                      ┌─────────────────┐
│ pip install │  ───HTTP/API───▶     │ FastAPI Server  │
│  projectx   │                      │ + Agents + DB   │
│             │  ◀───Response───     │ + Gmail/Twilio  │
└─────────────┘                      └─────────────────┘
```

**Why:**
- Can use CLI from office laptop without exposing credentials
- Monitoring runs 24/7 on Railway
- CLI is just a thin API client
- Only need API token, not full credentials

**MVP Approach:**
- Build everything locally first to verify it works
- Then split into server + CLI client
- Deploy server to Railway
- Publish CLI to PyPI (optional for hackathon)

### Kiro Hook Added

Created `.kiro/settings/hooks.json` — reminds to update DEVLOG after each session.

Created `.kiro/prompts/update-devlog.md` — prompt to help update the log.

---

## MVP Implementation Plan

### Phase 1: Core Backend (Priority)
1. FastAPI app with health endpoint
2. Gmail OAuth + email fetching
3. Basic urgency rules (VIP list, keywords)
4. Twilio SMS sending
5. SQLite for MVP (PostgreSQL later)

### Phase 2: AI Agents
1. CrewAI setup
2. Monitor Agent — fetch emails
3. Classifier Agent — determine urgency
4. Alert Agent — send SMS

### Phase 3: CLI + API
1. API endpoints for CLI
2. Typer CLI commands
3. Authentication (API token)

### Phase 4: Web Dashboard
1. OAuth flow UI
2. Rules configuration
3. Alert history

### Phase 5: Deploy
1. Railway deployment
2. PostgreSQL migration
3. Environment setup

---

## MVP Implementation - January 11, 2026

### Task 1: Configuration and Data Models

**Time spent:** ~10 min

**Files created:**
- `src/config.py` — Pydantic settings with env var loading
- `src/models/schemas.py` — Email, Classification, Urgency, AlertResult, PipelineResult models

### Task 2: Gmail Service

**Time spent:** ~15 min

**Files created:**
- `src/services/gmail.py` — GmailService class with OAuth, email fetching, data extraction

**Key features:**
- OAuth 2.0 authentication with token caching
- Fetch unread emails from inbox
- Extract sender, subject, snippet from raw messages

### Task 3: Classifier Agent

**Time spent:** ~15 min

**Files created:**
- `src/agents/classifier.py` — ClassifierAgent using OpenAI GPT-4o-mini

**Key features:**
- LLM-based urgency classification
- Returns URGENT or NOT_URGENT with reason
- Graceful error handling (defaults to NOT_URGENT on failure)

### Task 4: Twilio Service

**Time spent:** ~10 min

**Files created:**
- `src/services/twilio_sms.py` — TwilioService for SMS alerts

**Key features:**
- Format email into SMS (max 160 chars)
- Send SMS via Twilio API
- Error handling with logging

### Task 5: Pipeline Orchestrator

**Time spent:** ~10 min

**Files created:**
- `src/services/pipeline.py` — Pipeline class orchestrating the flow

**Key features:**
- Wires Gmail → Classifier → Twilio
- Processes each email and tracks results
- Returns PipelineResult with stats

### Task 6: FastAPI Endpoints

**Time spent:** ~15 min

**Files created:**
- `src/main.py` — FastAPI app with /health and /check endpoints

**Key features:**
- GET /health — returns status
- POST /check — runs full pipeline
- Lifespan handler initializes all services

### MVP Status

**Completed:**
- [x] Config and models
- [x] Gmail Service
- [x] Classifier Agent
- [x] Twilio Service
- [x] Pipeline Orchestrator
- [x] FastAPI endpoints

**Next:** Test with real credentials

---

### MVP Testing Complete! 🎉

**Time spent:** ~45 min

**What was tested:**

1. **Gmail OAuth Flow**
   - Created Google Cloud project with Gmail API enabled
   - Set up OAuth consent screen (test mode)
   - Created Desktop app credentials
   - Successfully authenticated and created `token.json`

2. **Email Fetching**
   - Fetched 10 unread emails from inbox
   - Correctly extracted sender, subject, snippet

3. **AI Classification**
   - All 10 emails correctly classified as NOT_URGENT:
     - Bank alerts → NOT_URGENT ✅
     - LinkedIn notifications → NOT_URGENT ✅
     - Promotional emails → NOT_URGENT ✅
     - Hackathon updates → NOT_URGENT ✅
   - Test urgent email classified as URGENT ✅

4. **SMS Alerts**
   - Purchased Twilio trial number: +1 878 222 3364
   - Verified recipient number (keypad phone)
   - Successfully sent SMS alert to keypad phone!

**Test Results:**
```
POST /check → 10 emails checked, 0 alerts (all correctly NOT_URGENT)
POST /test-urgent → Simulated urgent email, SMS sent successfully!
```

**MVP is fully functional:**
- ✅ Gmail OAuth authentication
- ✅ Email fetching (unread from inbox)
- ✅ AI urgency classification (GPT-4o-mini via OpenRouter)
- ✅ SMS alerts via Twilio

**Next Steps:**
- [ ] Deploy to Railway
- [ ] Build CLI client
- [ ] Add VIP sender rules
- [ ] Add keyword rules
- [ ] Web dashboard

---

## CrewAI Integration - January 11, 2026

### Task: Implement Multi-Agent Architecture

**Goal:** Replace direct OpenAI classifier with CrewAI multi-agent crew (Monitor → Classifier → Alert)

### Issues Encountered

#### Issue 1: Python 3.13 Compatibility with LiteLLM
**Problem:** CrewAI 1.8.0 requires LiteLLM, but LiteLLM uses the deprecated `cgi` module which was removed in Python 3.13.

**Error:**
```
ModuleNotFoundError: No module named 'cgi'
```

**Root cause:** `litellm/litellm_core_utils/prompt_templates/factory.py` imports `from cgi import parse_header`

**Solution:** Added fallback mechanism in `main.py` to use direct ClassifierAgent when CrewAI fails.

#### Issue 2: Dependency Version Conflicts
**Problem:** Multiple conflicting version requirements:
- `crewai 1.8.0` requires `openai~=1.83.0`
- `litellm 1.80.13` requires `openai>=2.8.0`
- `instructor 1.12.0` requires `openai<2.0.0,>=1.70.0`

**Solution:** Installed `litellm>=1.50.0,<1.60.0` which is compatible with `openai 1.83.0`

#### Issue 3: Port Already in Use
**Problem:** When restarting uvicorn, port 8000/8001 remained occupied by zombie processes.

**Solution:** Kill processes before starting:
```bash
pkill -f uvicorn
# or
lsof -ti:8001 | xargs kill -9
```

#### Issue 4: Virtual Environment Not Activated
**Problem:** Commands like `uvicorn` and `python` not found.

**Solution:** Always activate venv before running:
```bash
source .venv/bin/activate && uvicorn src.main:app --reload
```

### Implementation Outcome

**Files Created:**
- `src/agents/definitions.py` — Agent factory functions (Monitor, Classifier, Alert)
- `src/agents/tasks.py` — Task factory functions for each agent
- `src/agents/crew.py` — EmailProcessingCrew class orchestrating agents

**Files Modified:**
- `src/config.py` — Added CrewAI settings (crewai_model, crewai_verbose)
- `src/services/pipeline.py` — Support both ClassifierAgent and EmailProcessingCrew
- `src/main.py` — Fallback logic: try CrewAI, fall back to direct classifier

**Current Status:**
- ✅ CrewAI code is ready and correct
- ⚠️ CrewAI doesn't work on Python 3.13 due to litellm compatibility
- ✅ Fallback to direct ClassifierAgent works perfectly
- ✅ Local testing passed (/health, /test-urgent)

### Recommendations for Future

1. **Use Python 3.11 or 3.12** for CrewAI projects until litellm is updated
2. **Always implement fallback mechanisms** for AI framework integrations
3. **Pin dependency versions** to avoid conflicts
4. **Test locally before deploying** to catch compatibility issues early

---
