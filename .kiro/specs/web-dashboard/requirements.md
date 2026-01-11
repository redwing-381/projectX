# Requirements Document

## Introduction

A web dashboard for ProjectX that provides a browser-based interface for viewing alert history, configuring VIP senders and keyword rules, and monitoring system status. Uses PostgreSQL on Railway for persistent storage.

## Glossary

- **Dashboard**: The main web interface for ProjectX
- **User**: Person accessing the dashboard
- **Alert_History**: Record of all processed emails and their classifications
- **VIP_Sender**: Email address or domain that automatically triggers URGENT classification
- **Keyword_Rule**: Word or phrase that triggers URGENT classification when found in email
- **PostgreSQL**: Relational database hosted on Railway

## Requirements

### Requirement 1: Dashboard Home Page

**User Story:** As a user, I want to see an overview of my email monitoring status, so that I can quickly understand system health and recent activity.

#### Acceptance Criteria

1. WHEN the User visits the dashboard home page, THE Dashboard SHALL display the current server status (online/offline)
2. WHEN the User visits the dashboard home page, THE Dashboard SHALL display the count of emails checked today
3. WHEN the User visits the dashboard home page, THE Dashboard SHALL display the count of alerts sent today
4. WHEN the User visits the dashboard home page, THE Dashboard SHALL display the last 5 alerts with sender, subject, and timestamp

### Requirement 2: Alert History Page

**User Story:** As a user, I want to view the history of all processed emails, so that I can review what was classified as urgent and verify the system is working correctly.

#### Acceptance Criteria

1. WHEN the User visits the alert history page, THE Dashboard SHALL display a paginated list of all processed emails
2. THE Dashboard SHALL display for each email: sender, subject, classification (URGENT/NOT_URGENT), reason, timestamp, and SMS status
3. WHEN the User filters by classification, THE Dashboard SHALL show only emails matching that classification
4. WHEN the User searches by sender or subject, THE Dashboard SHALL show only matching emails

### Requirement 3: VIP Senders Management

**User Story:** As a user, I want to manage a list of VIP senders, so that emails from important contacts are always classified as urgent.

#### Acceptance Criteria

1. WHEN the User visits the VIP senders page, THE Dashboard SHALL display all configured VIP senders
2. WHEN the User adds a VIP sender email or domain, THE Dashboard SHALL save it to the database
3. WHEN the User removes a VIP sender, THE Dashboard SHALL delete it from the database
4. WHEN an email arrives from a VIP sender, THE Classifier SHALL automatically classify it as URGENT

### Requirement 4: Keyword Rules Management

**User Story:** As a user, I want to manage keyword rules, so that emails containing specific words are classified as urgent.

#### Acceptance Criteria

1. WHEN the User visits the keyword rules page, THE Dashboard SHALL display all configured keywords
2. WHEN the User adds a keyword, THE Dashboard SHALL save it to the database
3. WHEN the User removes a keyword, THE Dashboard SHALL delete it from the database
4. WHEN an email contains a configured keyword in subject or body, THE Classifier SHALL classify it as URGENT

### Requirement 5: Database Persistence

**User Story:** As a user, I want my settings and history to persist, so that I don't lose data when the server restarts.

#### Acceptance Criteria

1. THE System SHALL store all alert history in PostgreSQL
2. THE System SHALL store VIP senders in PostgreSQL
3. THE System SHALL store keyword rules in PostgreSQL
4. WHEN the server restarts, THE System SHALL retain all stored data

### Requirement 6: Settings Page

**User Story:** As a user, I want to configure system settings, so that I can customize the notification behavior.

#### Acceptance Criteria

1. WHEN the User visits the settings page, THE Dashboard SHALL display current phone number (masked)
2. THE Dashboard SHALL allow the User to update the alert phone number
3. THE Dashboard SHALL display the current monitoring status (active/paused)
4. THE Dashboard SHALL allow the User to pause/resume monitoring
