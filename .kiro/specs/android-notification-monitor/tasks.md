# Implementation Plan: Android Notification Monitor

## Overview

Build an Android app that captures notifications from messaging apps and sends them to the ProjectX backend for urgency classification.

## Tasks

- [x] 1. Set up Android project structure
  - Create app module with Kotlin
  - Configure Gradle dependencies (Retrofit, WorkManager, Coroutines)
  - Set up Android manifest with required permissions
  - _Requirements: 1.3, 6.1, 6.2_

- [x] 2. Implement data models and storage
  - [x] 2.1 Create data classes for CapturedNotification, AppConfig, ServerConfig
    - Define all fields as per design document
    - _Requirements: 1.1_
  - [x] 2.2 Implement NotificationRepository with SharedPreferences
    - Queue management (add, get unsynced, mark synced, clear)
    - JSON serialization for notification list
    - _Requirements: 1.2, 4.3, 4.4_

- [x] 3. Implement NotificationListenerService
  - [x] 3.1 Create NotificationService extending NotificationListenerService
    - Override onNotificationPosted
    - Extract app name, sender, text from StatusBarNotification
    - _Requirements: 1.1_
  - [x] 3.2 Implement app filtering logic
    - Check if notification source is in selected apps
    - _Requirements: 1.4, 2.3_
  - [x] 3.3 Implement duplicate detection
    - Track recent notifications (app + sender + text + time)
    - Ignore duplicates within 60 seconds
    - _Requirements: 1.5_

- [x] 4. Implement settings and configuration
  - [x] 4.1 Create SettingsManager for persisting configuration
    - Server URL and API key storage
    - Selected apps storage
    - Sync interval storage
    - _Requirements: 2.2, 3.2_
  - [x] 4.2 Create list of supported apps with package names
    - WhatsApp, Instagram, Telegram, Slack, Discord, SMS, Messenger
    - _Requirements: 2.1_

- [x] 5. Implement API client
  - [x] 5.1 Create ProjectXApiClient with Retrofit
    - POST /api/notifications endpoint
    - Include Authorization header with API key
    - _Requirements: 4.2_
  - [x] 5.2 Implement test connection method
    - GET /health endpoint
    - _Requirements: 3.4_

- [x] 6. Implement SyncWorker
  - [x] 6.1 Create SyncWorker extending CoroutineWorker
    - Fetch unsynced notifications from repository
    - Send to server via API client
    - Mark as synced on success, retain on failure
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 6.2 Implement WorkManager scheduling
    - Periodic work request with configurable interval
    - Network constraint (requires connectivity)
    - _Requirements: 4.1, 4.5, 6.2_

- [x] 7. Implement MainActivity UI
  - [x] 7.1 Create settings screen layout
    - Server URL input
    - API key input (password field)
    - Test connection button
    - App selection checkboxes
    - Sync interval selector
    - Sync now button
    - _Requirements: 2.1, 3.1, 3.4, 4.6_
  - [x] 7.2 Create status display section
    - Notification access status
    - Queue size
    - Last sync time and result
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - [x] 7.3 Implement permission request flow
    - Check notification listener permission
    - Navigate to settings if not granted
    - _Requirements: 1.3_

- [ ] 8. Implement foreground service notification
  - Create persistent notification for background operation
  - Show monitoring status
  - _Requirements: 6.3_

- [x] 9. Implement boot receiver
  - Create BroadcastReceiver for BOOT_COMPLETED
  - Restart monitoring if it was enabled
  - _Requirements: 6.4_

- [x] 10. Add backend API endpoint
  - [x] 10.1 Create POST /api/notifications endpoint in FastAPI
    - Accept batch of notifications
    - Classify each for urgency
    - Send SMS for urgent ones
    - Return processed count
    - _Requirements: 4.2_

- [ ] 11. Checkpoint - Test end-to-end flow
  - Install app on Android device
  - Configure server URL and API key
  - Enable notification access
  - Send test WhatsApp message
  - Verify notification captured and synced
  - Verify SMS sent for urgent messages

## Notes

- The app requires Android 5.0+ (API 21) for NotificationListenerService
- Users must manually grant notification access in Android settings
- WorkManager handles battery optimization automatically
- Test on real device (emulator doesn't receive real notifications)
