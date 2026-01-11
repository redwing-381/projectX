# Implementation Plan: Telegram Monitor

## Overview

Add Telegram message monitoring with a dedicated TelegramMonitorAgent in CrewAI. Messages forwarded to a bot are classified for urgency and forwarded via SMS if urgent.

## Tasks

- [x] 1. Add Telegram configuration
  - [x] 1.1 Update `src/config.py` with Telegram settings
    - Add telegram_bot_token, telegram_webhook_secret
    - _Requirements: 1.1_

  - [x] 1.2 Update `.env.example` with Telegram variables
    - Add TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET
    - _Requirements: 1.1_

- [x] 2. Create TelegramMessage model
  - [x] 2.1 Add TelegramMessage to `src/models/schemas.py`
    - Fields: id, sender, sender_username, text, timestamp, is_forwarded, original_sender
    - _Requirements: 2.1, 2.2, 2.4_

- [x] 3. Create TelegramService
  - [x] 3.1 Create `src/services/telegram.py`
    - __init__ with bot_token
    - set_webhook method to register with Telegram API
    - parse_update method to convert webhook to TelegramMessage
    - send_message method for confirmations
    - _Requirements: 1.2, 2.1, 2.2, 2.3, 2.4_

  - [ ]* 3.2 Write property test for webhook parsing
    - **Property 1: Webhook parsing preserves message content**
    - **Validates: Requirements 2.1, 2.2, 2.4**

- [x] 4. Create TelegramMonitorAgent
  - [x] 4.1 Add create_telegram_monitor_agent to `src/agents/definitions.py`
    - Role: "Telegram Message Monitor"
    - Goal: "Monitor and classify Telegram messages for urgency"
    - _Requirements: 3.1, 3.2_

  - [x] 4.2 Add telegram classification task to `src/agents/tasks.py`
    - Task to classify TelegramMessage urgency
    - _Requirements: 3.3_

- [x] 5. Create TelegramProcessingCrew
  - [x] 5.1 Create `src/agents/telegram_crew.py`
    - TelegramProcessingCrew class
    - Include TelegramMonitorAgent and AlertAgent
    - process_message method returning Classification
    - Check VIP senders and keywords before LLM
    - _Requirements: 3.3, 3.4, 4.1, 4.2, 4.3_

  - [ ]* 5.2 Write property test for VIP sender detection
    - **Property 2: VIP sender detection for Telegram usernames**
    - **Validates: Requirements 3.4, 6.2**

  - [ ]* 5.3 Write property test for classification output
    - **Property 3: Classification output validity**
    - **Validates: Requirements 3.3, 4.3**

- [x] 6. Update database for source tracking
  - [x] 6.1 Add source field to AlertHistory model in `src/db/models.py`
    - source: String, default "email"
    - _Requirements: 5.3_

  - [x] 6.2 Update crud.create_alert to accept source parameter
    - _Requirements: 5.1, 5.3_

  - [ ]* 6.3 Write property test for source distinction
    - **Property 4: Alert history source distinction**
    - **Validates: Requirements 5.1, 5.3**

- [x] 7. Create webhook endpoint
  - [x] 7.1 Create `src/api/telegram.py` with webhook route
    - POST /telegram/webhook endpoint
    - Parse update, process through crew, send SMS if urgent
    - Save to alert history with source="telegram"
    - _Requirements: 1.3, 3.5, 5.1_

  - [x] 7.2 Include telegram router in `src/main.py`
    - Import and include router
    - Initialize TelegramService and TelegramProcessingCrew
    - _Requirements: 1.2, 1.3_

- [x] 8. Update dashboard for Telegram alerts
  - [x] 8.1 Update history template to show source
    - Add source column/badge to history table
    - _Requirements: 5.2_

- [x] 9. Checkpoint - Test locally
  - Test webhook endpoint with curl
  - Verify TelegramMessage parsing
  - Verify classification works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Deploy and configure
  - Add TELEGRAM_BOT_TOKEN to Railway
  - Set webhook URL via Telegram API
  - Test with real Telegram bot
  - _Requirements: 1.1, 1.2_

## Notes

- Tasks marked with `*` are optional property tests
- Create bot via @BotFather on Telegram
- Webhook URL format: https://your-domain.com/telegram/webhook
- Use python-telegram-bot or httpx for Telegram API calls
