# Requirements Document

## Introduction

ProjectX MVP - Minimal proof of concept to validate: fetch email → AI classifies urgency → send SMS. No web UI, minimal CLI, hardcoded config.

## Glossary

- **System**: The ProjectX application
- **Email**: A Gmail message
- **Alert**: An SMS sent to keypad phone
- **Classifier_Agent**: CrewAI agent that determines urgency using LLM

## Requirements

### Requirement 1: Email Fetching

**User Story:** As a user, I want to fetch my recent unread emails, so that they can be analyzed.

#### Acceptance Criteria

1. THE System SHALL connect to Gmail using OAuth credentials (from .env)
2. THE System SHALL fetch unread emails from the inbox
3. THE System SHALL extract sender, subject, and body snippet from each email

### Requirement 2: AI Urgency Classification

**User Story:** As a user, I want AI to determine if an email is urgent.

#### Acceptance Criteria

1. THE Classifier_Agent SHALL analyze email content using LLM (GPT-4o-mini)
2. THE Classifier_Agent SHALL return urgency: URGENT or NOT_URGENT
3. THE Classifier_Agent SHALL provide a one-line reason

### Requirement 3: SMS Alert

**User Story:** As a user, I want to receive SMS for urgent emails.

#### Acceptance Criteria

1. WHEN an email is classified as URGENT, THE System SHALL send an SMS via Twilio
2. THE SMS SHALL contain sender and subject (under 160 chars)
3. THE System SHALL log the alert to console

### Requirement 4: Basic API

**User Story:** As a developer, I want a simple API to trigger the check.

#### Acceptance Criteria

1. THE System SHALL provide GET /health returning {"status": "ok"}
2. THE System SHALL provide POST /check that runs the email check pipeline
3. THE System SHALL return results as JSON
