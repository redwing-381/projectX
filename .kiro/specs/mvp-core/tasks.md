# Implementation Plan: ProjectX MVP

## Overview

Build the minimal email-to-SMS pipeline: Gmail → AI Classification → Twilio SMS.

## Tasks

- [x] 1. Set up configuration and data models
  - Create `src/config.py` with environment variable loading
  - Create `src/models/schemas.py` with Pydantic models (Email, Classification, Urgency, AlertResult, PipelineResult)
  - _Requirements: 1.3, 2.2, 2.3_

- [x] 2. Implement Gmail Service
  - [x] 2.1 Create `src/services/gmail.py` with GmailService class
    - OAuth credential loading from .env
    - `get_unread_emails()` method using Gmail API
    - `extract_email_data()` method to parse raw messages
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ]* 2.2 Write property test for email extraction
    - **Property 1: Email extraction completeness**
    - **Validates: Requirements 1.3**

- [x] 3. Implement Classifier Agent
  - [x] 3.1 Create `src/agents/classifier.py` with ClassifierAgent class
    - OpenAI client initialization
    - `classify()` method with LLM prompt
    - Return Classification with urgency and reason
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ]* 3.2 Write property test for classification output
    - **Property 2: Classification output validity**
    - **Validates: Requirements 2.2, 2.3**

- [x] 4. Implement Twilio Service
  - [x] 4.1 Create `src/services/twilio_sms.py` with TwilioService class
    - Twilio client initialization
    - `send_sms()` method
    - `format_alert()` method (max 160 chars)
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ]* 4.2 Write property test for SMS formatting
    - **Property 3: SMS message length constraint**
    - **Validates: Requirements 3.2**

- [x] 5. Implement Pipeline Orchestrator
  - [x] 5.1 Create `src/services/pipeline.py` with Pipeline class
    - Wire together Gmail, Classifier, Twilio
    - `run()` method executes full flow
    - Return PipelineResult with all results
    - _Requirements: 1.1, 2.1, 3.1_

- [x] 6. Implement FastAPI endpoints
  - [x] 6.1 Create `src/main.py` with FastAPI app
    - GET /health endpoint
    - POST /check endpoint that runs pipeline
    - Return JSON responses
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ]* 6.2 Write property test for API response format
    - **Property 4: API response format**
    - **Validates: Requirements 4.3**

- [x] 7. Checkpoint - Verify MVP works
  - Run `uvicorn src.main:app --reload`
  - Test /health endpoint
  - Test /check endpoint with real Gmail (requires OAuth setup)
  - Verify SMS is received on phone
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property tests
- OAuth credentials must be set up in Google Cloud Console before testing
- Twilio credentials must be configured before SMS testing
- For local testing, use `.env` file with all API keys
