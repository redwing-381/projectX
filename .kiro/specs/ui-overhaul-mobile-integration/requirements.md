# Requirements Document

## Introduction

This feature overhauls the ProjectX web dashboard to integrate mobile app notifications, remove deprecated Telegram userbot functionality, add an architecture visualization page, and modernize the UI to industry-level standards. The goal is to create a professional, user-friendly interface that displays notifications from all sources (email, mobile apps) with proper categorization and real-time sync visualization.

## Glossary

- **Dashboard**: The main web interface showing system status and recent alerts
- **Mobile_App**: The Android notification monitor app that captures notifications from messaging apps
- **Notification**: A message captured from either email (Gmail API) or mobile app (WhatsApp, Instagram, Telegram, etc.)
- **Sync**: The process of mobile app sending batched notifications to the backend
- **Architecture_Page**: A new page showing system architecture diagram and data flow
- **App_Filter**: UI component to filter notifications by source app
- **Classifier_Agent**: AI agent that determines notification urgency

## Requirements

### Requirement 1: Remove Telegram Userbot Integration

**User Story:** As a developer, I want to remove the deprecated Telegram userbot code, so that the codebase is cleaner and mobile app handles Telegram monitoring.

#### Acceptance Criteria

1. WHEN the server starts, THE System SHALL NOT attempt to connect to Telegram userbot
2. THE System SHALL remove all Telegram-related configuration from settings page
3. THE System SHALL remove Telegram status card from dashboard
4. THE System SHALL retain database records with source="telegram" for historical data

### Requirement 2: Mobile App Notification API Endpoint

**User Story:** As a mobile app user, I want to sync notifications to the backend, so that they can be classified and displayed in the web UI.

#### Acceptance Criteria

1. WHEN the mobile app sends a POST request to /api/notifications, THE System SHALL accept a batch of notifications
2. THE System SHALL validate the request contains device_id and notifications array
3. WHEN a notification is received, THE Classifier_Agent SHALL classify its urgency
4. WHEN a notification is classified as URGENT, THE System SHALL send an SMS alert
5. THE System SHALL store all notifications in the database with source field indicating the app (e.g., "android:whatsapp")
6. THE System SHALL return a response with processed count and urgent count

### Requirement 3: Mobile App Notification Agent

**User Story:** As a system architect, I want a dedicated agent for mobile app notifications, so that classification is optimized for messaging app content.

#### Acceptance Criteria

1. THE Mobile_Notification_Agent SHALL accept notification with app, sender, text, and timestamp fields
2. THE Mobile_Notification_Agent SHALL check VIP senders list before LLM classification
3. THE Mobile_Notification_Agent SHALL check urgent keywords before LLM classification
4. WHEN VIP or keyword match occurs, THE Mobile_Notification_Agent SHALL return URGENT immediately
5. WHEN no rule matches, THE Mobile_Notification_Agent SHALL use LLM for classification
6. THE Mobile_Notification_Agent SHALL format SMS message appropriate for the source app

### Requirement 4: Notifications Page with App Filtering

**User Story:** As a user, I want to view all notifications grouped by source app, so that I can see what messages came from each platform.

#### Acceptance Criteria

1. WHEN a user visits /notifications, THE System SHALL display all notifications from mobile apps
2. THE System SHALL provide filter buttons for each app (WhatsApp, Instagram, Telegram, Slack, Discord, SMS, Messenger)
3. WHEN a filter is selected, THE System SHALL show only notifications from that app
4. THE System SHALL display notification sender, text preview, urgency status, and timestamp
5. THE System SHALL show app icon/badge for each notification
6. THE System SHALL paginate results with 20 items per page
7. THE System SHALL show total count for each app filter

### Requirement 5: Architecture Visualization Page

**User Story:** As a user, I want to see the system architecture, so that I understand how the notification flow works.

#### Acceptance Criteria

1. WHEN a user visits /architecture, THE System SHALL display an interactive architecture diagram
2. THE Architecture_Page SHALL show the data flow from sources (Gmail, Mobile App) to SMS alerts
3. THE Architecture_Page SHALL display the AI agent pipeline (Monitor → Classifier → Alert)
4. THE Architecture_Page SHALL show current connection status for each component
5. THE Architecture_Page SHALL include brief descriptions of each component
6. THE Architecture_Page SHALL use Mermaid.js or similar for diagram rendering

### Requirement 6: Dashboard Modernization

**User Story:** As a user, I want a modern, professional dashboard, so that the interface feels polished and trustworthy.

#### Acceptance Criteria

1. THE Dashboard SHALL display stats cards for: Server Status, Mobile App Sync, Emails Checked, Alerts Sent
2. THE Dashboard SHALL show last sync time from mobile app
3. THE Dashboard SHALL show notification count by source (Email, WhatsApp, Instagram, etc.)
4. THE Dashboard SHALL use consistent color scheme and spacing
5. THE Dashboard SHALL be responsive on mobile devices
6. THE Dashboard SHALL show real-time status indicators with appropriate colors

### Requirement 7: Navigation and Layout Updates

**User Story:** As a user, I want intuitive navigation, so that I can easily access all features.

#### Acceptance Criteria

1. THE Navigation SHALL include: Dashboard, Notifications, History, VIP Senders, Keywords, Architecture, Settings
2. THE Navigation SHALL highlight the current active page
3. THE Navigation SHALL be responsive with mobile hamburger menu
4. THE Footer SHALL display version and project name
5. THE Layout SHALL use consistent max-width and padding across all pages

### Requirement 8: Settings Page Updates

**User Story:** As a user, I want updated settings that reflect the new architecture, so that I can configure the system correctly.

#### Acceptance Criteria

1. THE Settings_Page SHALL remove Telegram userbot configuration section
2. THE Settings_Page SHALL add Mobile App section showing sync status
3. THE Settings_Page SHALL display last sync time and device info
4. THE Settings_Page SHALL show count of notifications received from mobile app
5. THE Settings_Page SHALL maintain existing email monitoring controls
6. THE Settings_Page SHALL show API key status (configured/not configured)

### Requirement 9: UI Design Standards

**User Story:** As a user, I want a professional UI that follows industry standards, so that the application feels polished.

#### Acceptance Criteria

1. THE UI SHALL use a consistent dark theme with gray-900 background
2. THE UI SHALL use Tailwind CSS for styling
3. THE UI SHALL use consistent border-radius (rounded-xl for cards)
4. THE UI SHALL use consistent spacing (space-y-6 for sections)
5. THE UI SHALL use appropriate color coding (green=success, red=urgent, blue=info, gray=neutral)
6. THE UI SHALL include hover states for interactive elements
7. THE UI SHALL use appropriate font weights (bold for headings, medium for buttons)
8. THE UI SHALL include loading states for async operations

### Requirement 10: Database Schema Updates

**User Story:** As a developer, I want proper database schema for mobile notifications, so that data is stored correctly.

#### Acceptance Criteria

1. THE AlertHistory model SHALL support source field with values like "email", "android:whatsapp", "android:instagram"
2. THE System SHALL add MobileDevice model to track connected devices
3. THE System SHALL add MobileNotification model for raw notification storage
4. THE System SHALL track last_sync_time per device
5. THE System SHALL support querying notifications by source app
