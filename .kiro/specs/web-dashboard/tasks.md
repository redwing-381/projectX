# Implementation Plan: Web Dashboard

## Overview

Build a FastAPI + Jinja2 web dashboard with PostgreSQL persistence for alert history, VIP senders, and keyword rules.

## Tasks

- [x] 1. Set up PostgreSQL database
  - [x] 1.1 Create `src/db/database.py` with SQLAlchemy engine and session
    - Configure DATABASE_URL from environment
    - Create engine with connection pooling
    - Create SessionLocal and get_db dependency
    - _Requirements: 5.1_

  - [x] 1.2 Create `src/db/models.py` with SQLAlchemy models
    - AlertHistory model (email_id, sender, subject, urgency, reason, sms_sent, created_at)
    - VIPSender model (email_or_domain, created_at)
    - KeywordRule model (keyword, created_at)
    - Settings model (key, value)
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 1.3 Add DATABASE_URL to config and .env.example
    - Update src/config.py with database_url setting
    - _Requirements: 5.1_

- [x] 2. Implement CRUD operations
  - [x] 2.1 Create `src/db/crud.py` with database operations
    - Alert history: create, get_all, get_by_id, get_today_stats
    - VIP senders: get_all, add, remove, is_vip_sender
    - Keywords: get_all, add, remove, has_urgent_keyword
    - _Requirements: 2.1, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

  - [ ]* 2.2 Write property test for VIP sender round-trip
    - **Property 1: VIP sender round-trip persistence**
    - **Validates: Requirements 3.2, 5.2**

  - [ ]* 2.3 Write property test for keyword round-trip
    - **Property 2: Keyword rule round-trip persistence**
    - **Validates: Requirements 4.2, 5.3**

- [x] 3. Update classifier with VIP/keyword rules
  - [x] 3.1 Update `src/agents/classifier.py` to check VIP senders and keywords
    - Before LLM classification, check if sender is VIP
    - Before LLM classification, check if subject/snippet contains keyword
    - If VIP or keyword match, return URGENT immediately
    - _Requirements: 3.4, 4.4_

  - [ ]* 3.2 Write property test for VIP classification override
    - **Property 3: VIP sender classification override**
    - **Validates: Requirements 3.4**

  - [ ]* 3.3 Write property test for keyword classification override
    - **Property 4: Keyword classification override**
    - **Validates: Requirements 4.4**

- [x] 4. Update pipeline to save alert history
  - [x] 4.1 Update `src/services/pipeline.py` to save results to database
    - After processing each email, save AlertHistory record
    - Include all classification details
    - _Requirements: 5.1_

- [x] 5. Create HTML templates
  - [x] 5.1 Create `src/templates/base.html` with navigation
    - Include Tailwind CSS via CDN
    - Navigation: Dashboard, History, VIP Senders, Keywords, Settings
    - _Requirements: 1.1_

  - [x] 5.2 Create `src/templates/dashboard.html`
    - Display server status, emails checked today, alerts sent today
    - Display last 5 alerts in a table
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 5.3 Create `src/templates/history.html`
    - Paginated table of all alerts
    - Filter by urgency dropdown
    - Search by sender/subject
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 5.4 Create `src/templates/vip_senders.html`
    - List all VIP senders with delete buttons
    - Form to add new VIP sender
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 5.5 Create `src/templates/keywords.html`
    - List all keywords with delete buttons
    - Form to add new keyword
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.6 Create `src/templates/settings.html`
    - Display masked phone number
    - Pause/resume monitoring toggle
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6. Create web routes
  - [x] 6.1 Create `src/api/web.py` with FastAPI router
    - GET / - Dashboard home
    - GET /history - Alert history with pagination
    - GET /vip-senders - VIP senders page
    - POST /vip-senders/add - Add VIP sender
    - POST /vip-senders/delete/{id} - Delete VIP sender
    - GET /keywords - Keywords page
    - POST /keywords/add - Add keyword
    - POST /keywords/delete/{id} - Delete keyword
    - GET /settings - Settings page
    - POST /settings/update - Update settings
    - _Requirements: All_

  - [ ]* 6.2 Write property test for filter correctness
    - **Property 5: Alert history filter correctness**
    - **Validates: Requirements 2.3, 2.4**

- [x] 7. Integrate web routes into main app
  - [x] 7.1 Update `src/main.py` to include web router
    - Mount static files if needed
    - Include web router
    - Initialize database tables on startup
    - _Requirements: All_

- [x] 8. Checkpoint - Test locally
  - Run locally with `uvicorn src.main:app --reload`
  - Visit http://localhost:8000/ - verify dashboard loads
  - Add VIP sender, verify it appears
  - Add keyword, verify it appears
  - Run /check, verify alert history updates
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Deploy and verify
  - Add DATABASE_URL to Railway environment variables
  - Push to GitHub for auto-deploy
  - Verify dashboard works on Railway
  - _Requirements: 5.1_

## Notes

- Tasks marked with `*` are optional property tests
- Use Tailwind CSS via CDN for styling (no build step)
- PostgreSQL connection string format: `postgresql://user:pass@host:port/db`
- Railway provides DATABASE_URL automatically when PostgreSQL is added
