# Implementation Plan: UI Overhaul & Mobile Integration

## Overview

This implementation plan covers removing Telegram userbot, creating mobile notification API and agent, building new UI pages (Notifications, Architecture), and modernizing the dashboard to industry standards.

## Tasks

- [x] 1. Remove Telegram Userbot Integration
  - [x] 1.1 Delete Telegram-related files
    - Delete `src/services/telegram_userbot.py`
    - Delete `src/services/telegram.py`
    - Delete `src/api/telegram.py`
    - Delete `src/agents/telegram_crew.py`
    - Delete `scripts/generate_telegram_session.py`
    - Delete `.kiro/specs/telegram-monitor/` directory
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 1.2 Update main.py to remove Telegram initialization
    - Remove Telegram userbot import and startup code
    - Remove Telegram shutdown handling
    - _Requirements: 1.1_
  - [x] 1.3 Update config.py to remove Telegram settings
    - Remove telegram_api_id, telegram_api_hash, telegram_session fields
    - _Requirements: 1.1_
  - [x] 1.4 Update .env.example to remove Telegram variables
    - Remove TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION
    - _Requirements: 1.1_

- [x] 2. Database Schema Updates
  - [x] 2.1 Add MobileDevice model
    - Create model with device_id, device_name, last_sync_at, notification_count, created_at
    - Add unique index on device_id
    - _Requirements: 10.2, 10.4_
  - [x] 2.2 Add CRUD functions for mobile devices
    - get_or_create_device(device_id)
    - update_device_sync(device_id, notification_count)
    - get_all_devices()
    - _Requirements: 10.4_
  - [x] 2.3 Add notification query functions
    - get_notifications_by_source(source_prefix)
    - get_notification_counts_by_source()
    - _Requirements: 10.5_
  - [ ]* 2.4 Write property test for database source tracking
    - **Property 5: Database Source Tracking**
    - **Validates: Requirements 2.5, 10.1**

- [x] 3. Mobile Notification Agent
  - [x] 3.1 Create MobileNotificationAgent class
    - Create `src/agents/mobile_notification_agent.py`
    - Implement classify() method with VIP → Keywords → LLM pipeline
    - Implement format_sms() method with app prefix
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6_
  - [ ]* 3.2 Write property test for VIP/keyword fast-path
    - **Property 3: VIP and Keyword Fast-Path Classification**
    - **Validates: Requirements 3.2, 3.3, 3.4**
  - [ ]* 3.3 Write property test for SMS format validity
    - **Property 4: SMS Format Validity**
    - **Validates: Requirements 3.6**
  - [ ]* 3.4 Write property test for classification output validity
    - **Property 2: Classification Output Validity**
    - **Validates: Requirements 2.3, 3.1**

- [x] 4. Mobile Notification API Endpoint
  - [x] 4.1 Create notification endpoint in web.py
    - Add POST /api/notifications endpoint
    - Implement NotificationPayload and NotificationBatchRequest models
    - Implement NotificationBatchResponse model
    - _Requirements: 2.1, 2.2, 2.6_
  - [x] 4.2 Implement notification processing logic
    - Validate request structure
    - Register/update device
    - Process each notification through MobileNotificationAgent
    - Store in database with correct source format
    - Send SMS for urgent notifications
    - Return processed and urgent counts
    - _Requirements: 2.3, 2.4, 2.5_
  - [ ]* 4.3 Write property test for API validation and response
    - **Property 1: API Endpoint Validation and Response**
    - **Validates: Requirements 2.1, 2.2, 2.6**

- [x] 5. Checkpoint - Backend Complete
  - Ensure all backend tests pass
  - Test API endpoint with sample requests
  - Verify database records are created correctly

- [x] 6. Update Base Template and Navigation
  - [x] 6.1 Update base.html navigation
    - Add Notifications link
    - Add Architecture link
    - Update menu order: Dashboard, Notifications, History, VIP Senders, Keywords, Architecture, Settings
    - _Requirements: 7.1_
  - [x] 6.2 Add responsive mobile menu
    - Add hamburger menu button for mobile
    - Add slide-out drawer for mobile navigation
    - _Requirements: 7.3_
  - [x] 6.3 Update footer
    - Add version number
    - Ensure project name is displayed
    - _Requirements: 7.4_
  - [ ]* 6.4 Write property test for navigation active state
    - **Property 9: Navigation Active State**
    - **Validates: Requirements 7.2**

- [x] 7. Create Notifications Page
  - [x] 7.1 Create notifications.html template
    - Add filter tabs for each app (All, WhatsApp, Instagram, Telegram, Slack, Discord, SMS, Messenger, Email)
    - Add count badges on each tab
    - Create notification card component with app badge, sender, preview, urgency, timestamp
    - Add pagination controls
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  - [x] 7.2 Create /notifications route in web.py
    - Accept app filter parameter
    - Accept page parameter
    - Query notifications with filter
    - Return paginated results with counts
    - _Requirements: 4.3, 4.6, 4.7_
  - [ ]* 7.3 Write property test for notification filtering
    - **Property 6: Notification Filtering Correctness**
    - **Validates: Requirements 4.3, 4.7**
  - [ ]* 7.4 Write property test for pagination bounds
    - **Property 7: Pagination Bounds**
    - **Validates: Requirements 4.6**

- [x] 8. Create Architecture Page
  - [x] 8.1 Create architecture.html template
    - Add Mermaid.js CDN script
    - Create architecture diagram showing data flow
    - Add component descriptions
    - Add real-time status indicators
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  - [x] 8.2 Create /architecture route in web.py
    - Gather component status (server, database, mobile devices)
    - Return status data to template
    - _Requirements: 5.4_

- [x] 9. Update Dashboard
  - [x] 9.1 Update dashboard.html template
    - Remove Telegram status card
    - Add Mobile App Sync card (last sync time, device count)
    - Update stats cards layout
    - Add notification breakdown by source
    - _Requirements: 6.1, 6.2, 6.3_
  - [x] 9.2 Update dashboard route in web.py
    - Fetch mobile device sync info
    - Fetch notification counts by source
    - Pass data to template
    - _Requirements: 6.2, 6.3_
  - [ ]* 9.3 Write property test for notification display completeness
    - **Property 10: Notification Display Completeness**
    - **Validates: Requirements 4.4, 4.5**

- [x] 10. Update Settings Page
  - [x] 10.1 Update settings.html template
    - Remove Telegram Monitoring section
    - Add Mobile App section with device list
    - Show last sync time per device
    - Show total notifications from mobile
    - Show API key status
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  - [x] 10.2 Update settings route in web.py
    - Fetch mobile device data
    - Calculate mobile notification count
    - Check API key configuration status
    - _Requirements: 8.3, 8.4, 8.6_

- [x] 11. Checkpoint - UI Complete
  - Ensure all pages render correctly
  - Test navigation between pages
  - Test filter functionality on notifications page
  - Verify responsive design on mobile viewport

- [x] 12. Device Sync Tracking
  - [x] 12.1 Implement device sync tracking in API endpoint
    - Update last_sync_at on each sync
    - Increment notification_count
    - _Requirements: 10.4_
  - [ ]* 12.2 Write property test for device sync tracking
    - **Property 8: Device Sync Tracking**
    - **Validates: Requirements 10.4**

- [x] 13. Final Checkpoint
  - Run all tests (unit and property-based)
  - Verify end-to-end flow: Mobile sync → Classification → SMS → Dashboard display
  - Test all filter combinations on notifications page
  - Verify architecture page shows correct status
  - Ensure no Telegram references remain in codebase

## Notes

- Tasks marked with `*` are optional property-based tests
- Telegram historical data (source="telegram") is preserved in database
- Mobile app badge colors defined in design document
- Use Tailwind CSS for all styling
- Mermaid.js loaded from CDN for architecture diagram
