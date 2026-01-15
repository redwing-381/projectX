# Requirements Document

## Introduction

The Android Notification Monitor is a companion mobile app for ProjectX that captures notifications from messaging apps (WhatsApp, Instagram, Slack, etc.) and sends them to the ProjectX backend for urgency classification. This enables users to receive SMS alerts for urgent messages even when their smartphone is put away.

## Glossary

- **Notification_Listener**: Android service that captures system notifications
- **Notification_Queue**: Local storage for captured notifications pending sync
- **Sync_Worker**: Background worker that periodically sends notifications to server
- **ProjectX_Server**: The backend server running on Railway
- **App_Filter**: User-configurable list of apps to monitor

## Requirements

### Requirement 1: Notification Capture

**User Story:** As a user, I want the app to capture notifications from selected messaging apps, so that urgent messages can be forwarded to my keypad phone.

#### Acceptance Criteria

1. WHEN a notification arrives from a monitored app, THE Notification_Listener SHALL capture the app name, sender, message text, and timestamp
2. WHEN a notification is captured, THE Notification_Listener SHALL store it in the Notification_Queue
3. WHEN the app lacks notification access permission, THE App SHALL prompt the user to grant permission
4. THE Notification_Listener SHALL filter notifications to only capture from user-selected apps
5. WHEN a notification is a duplicate (same app, sender, text within 1 minute), THE Notification_Listener SHALL ignore it

### Requirement 2: App Selection

**User Story:** As a user, I want to select which apps to monitor, so that I only receive alerts for relevant messaging apps.

#### Acceptance Criteria

1. THE App SHALL display a list of common messaging apps (WhatsApp, Instagram, Telegram, Slack, Discord, SMS)
2. WHEN a user toggles an app, THE App SHALL persist the selection locally
3. THE Notification_Listener SHALL only capture notifications from selected apps
4. THE App SHALL allow selecting/deselecting all apps at once

### Requirement 3: Server Configuration

**User Story:** As a user, I want to configure the server URL and API key, so that notifications are sent to my ProjectX instance.

#### Acceptance Criteria

1. THE App SHALL provide input fields for server URL and API key
2. WHEN the user saves configuration, THE App SHALL persist it locally
3. WHEN configuration is missing, THE App SHALL display a warning and disable sync
4. THE App SHALL provide a "Test Connection" button to verify server connectivity

### Requirement 4: Periodic Sync

**User Story:** As a user, I want notifications to be sent to the server periodically, so that urgent messages are processed in batches.

#### Acceptance Criteria

1. THE Sync_Worker SHALL run at a configurable interval (default 10 minutes)
2. WHEN the Sync_Worker runs, THE App SHALL send all queued notifications to the server
3. WHEN sync succeeds, THE App SHALL clear the synced notifications from the queue
4. WHEN sync fails, THE App SHALL retain notifications and retry on next interval
5. IF the device has no internet connection, THE Sync_Worker SHALL skip and retry later
6. THE App SHALL allow manual sync via a "Sync Now" button

### Requirement 5: Status Display

**User Story:** As a user, I want to see the app status, so that I know if monitoring is working correctly.

#### Acceptance Criteria

1. THE App SHALL display whether notification access is granted
2. THE App SHALL display the number of notifications in queue
3. THE App SHALL display the last sync time and result
4. THE App SHALL display the configured sync interval
5. THE App SHALL display connection status to the server

### Requirement 6: Background Operation

**User Story:** As a user, I want the app to work in the background, so that I can put my phone away and still have notifications captured.

#### Acceptance Criteria

1. THE Notification_Listener SHALL continue running when the app is in background
2. THE Sync_Worker SHALL continue running when the app is in background
3. THE App SHALL display a persistent notification indicating monitoring is active
4. WHEN the device restarts, THE App SHALL automatically resume monitoring if it was enabled
