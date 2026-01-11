# Requirements Document

## Introduction

Add Telegram message monitoring to ProjectX using a dedicated CrewAI agent. The system will receive messages via a Telegram bot, use a TelegramMonitorAgent to process and classify urgency, and forward urgent messages via SMS to the user's keypad phone.

## Glossary

- **Telegram_Bot**: A bot created via BotFather that receives messages forwarded by the user
- **Telegram_Service**: Service that handles incoming Telegram webhook events
- **TelegramMonitorAgent**: CrewAI agent dedicated to processing Telegram messages
- **Message**: A Telegram message with sender, text, and metadata
- **TelegramMessage**: Pydantic model representing a Telegram message (similar to Email model)

## Requirements

### Requirement 1: Telegram Bot Setup

**User Story:** As a user, I want to connect a Telegram bot to ProjectX, so that I can forward messages to be monitored.

#### Acceptance Criteria

1. THE System SHALL accept a TELEGRAM_BOT_TOKEN environment variable for bot authentication
2. WHEN the server starts, THE Telegram_Service SHALL register a webhook with Telegram API
3. THE System SHALL provide a /telegram/webhook endpoint to receive Telegram updates

### Requirement 2: Message Reception

**User Story:** As a user, I want to forward Telegram messages to my bot, so that they can be classified for urgency.

#### Acceptance Criteria

1. WHEN a message is received via webhook, THE Telegram_Service SHALL extract sender name, message text, and timestamp
2. WHEN a forwarded message is received, THE Telegram_Service SHALL extract the original sender information
3. THE System SHALL support text messages (not media/stickers initially)
4. THE Telegram_Service SHALL convert webhook data into a TelegramMessage model

### Requirement 3: TelegramMonitorAgent

**User Story:** As a developer, I want a dedicated CrewAI agent for Telegram monitoring, so that the multi-agent architecture is demonstrated.

#### Acceptance Criteria

1. THE TelegramMonitorAgent SHALL be a CrewAI agent with role "Telegram Message Monitor"
2. THE TelegramMonitorAgent SHALL have a goal to "Monitor and classify Telegram messages for urgency"
3. THE TelegramMonitorAgent SHALL process TelegramMessage objects and return Classification results
4. THE TelegramMonitorAgent SHALL check VIP senders and keywords before LLM classification
5. WHEN classified as URGENT, THE TelegramMonitorAgent SHALL trigger the AlertAgent to send SMS

### Requirement 4: Telegram Processing Crew

**User Story:** As a developer, I want a TelegramProcessingCrew that orchestrates Telegram message handling.

#### Acceptance Criteria

1. THE TelegramProcessingCrew SHALL include TelegramMonitorAgent and AlertAgent
2. THE TelegramProcessingCrew SHALL process messages in sequence: monitor → classify → alert
3. THE TelegramProcessingCrew SHALL return a Classification result with urgency and reason

### Requirement 5: Alert History

**User Story:** As a user, I want to see Telegram message history in the dashboard, so that I can review what was processed.

#### Acceptance Criteria

1. WHEN a Telegram message is processed, THE System SHALL save it to the alert history database
2. THE Dashboard SHALL display Telegram messages alongside email alerts
3. THE System SHALL distinguish between email and Telegram sources in the history with a "source" field

### Requirement 6: VIP Telegram Senders

**User Story:** As a user, I want to mark certain Telegram senders as VIP, so that their messages are always urgent.

#### Acceptance Criteria

1. THE System SHALL allow adding Telegram usernames (with @ prefix) to the VIP sender list
2. WHEN a message is from a VIP Telegram sender, THE TelegramMonitorAgent SHALL mark it as URGENT immediately
