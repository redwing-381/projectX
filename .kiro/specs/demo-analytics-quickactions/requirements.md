# Requirements Document

## Introduction

This document specifies requirements for three high-value features to enhance ProjectX for hackathon presentation: Demo Mode for judges to test without Gmail connection, Analytics Dashboard for visual insights, and Quick Actions for improved UX.

## Glossary

- **Demo_Mode**: A sandboxed environment with sample emails that allows users to experience the full classification flow without connecting their Gmail account
- **Analytics_Dashboard**: A visual representation of email processing statistics including charts and metrics
- **Quick_Actions**: Contextual action buttons on alerts that allow users to quickly perform common operations
- **Sample_Email**: Pre-defined email data used in Demo Mode to simulate real email classification
- **Classification_Pipeline**: The system that processes emails through VIP/keyword checks and AI classification

## Requirements

### Requirement 1: Demo Mode Activation

**User Story:** As a hackathon judge, I want to try the classification system without connecting my Gmail, so that I can evaluate the product quickly.

#### Acceptance Criteria

1. WHEN a user visits the dashboard without Gmail configured, THE System SHALL display a prominent "Try Demo Mode" button
2. WHEN a user clicks "Try Demo Mode", THE System SHALL activate demo mode and display a demo indicator banner
3. WHILE demo mode is active, THE System SHALL use sample emails instead of fetching from Gmail
4. WHEN demo mode is active, THE System SHALL allow the user to exit demo mode at any time
5. THE System SHALL provide at least 10 diverse sample emails covering urgent and non-urgent scenarios

### Requirement 2: Demo Email Classification

**User Story:** As a user in demo mode, I want to see realistic email classification results, so that I understand how the system works.

#### Acceptance Criteria

1. WHEN "Check Emails" is clicked in demo mode, THE System SHALL process sample emails through the real classification pipeline
2. WHEN sample emails are classified, THE System SHALL display results identical to real email processing
3. THE Sample_Emails SHALL include examples that trigger VIP sender rules
4. THE Sample_Emails SHALL include examples that trigger keyword rules
5. THE Sample_Emails SHALL include examples that require AI classification
6. WHEN an email is classified as URGENT in demo mode, THE System SHALL simulate SMS sending (not actually send)

### Requirement 3: Analytics Dashboard

**User Story:** As a user, I want to see visual analytics of my email processing history, so that I can understand patterns and system effectiveness.

#### Acceptance Criteria

1. THE Analytics_Dashboard SHALL display a line chart showing emails processed over the last 7 days
2. THE Analytics_Dashboard SHALL display a pie chart showing urgent vs non-urgent ratio
3. THE Analytics_Dashboard SHALL display a bar chart showing top 5 senders by email count
4. THE Analytics_Dashboard SHALL display key metrics: total emails, total alerts, alert rate percentage
5. WHEN no data exists, THE Analytics_Dashboard SHALL display appropriate empty states with helpful messages
6. THE Analytics_Dashboard SHALL be accessible from the main navigation

### Requirement 4: Quick Actions on Alerts

**User Story:** As a user, I want to quickly add senders to VIP list from alert history, so that I can efficiently manage my rules.

#### Acceptance Criteria

1. WHEN viewing an alert, THE System SHALL display a "Add to VIP" quick action button
2. WHEN "Add to VIP" is clicked, THE System SHALL extract the sender email and add to VIP list
3. WHEN a sender is already in VIP list, THE System SHALL disable the "Add to VIP" button and show "Already VIP"
4. WHEN "Add to VIP" succeeds, THE System SHALL show a success confirmation without page reload
5. THE Quick_Actions SHALL be available on dashboard recent alerts and history page

### Requirement 5: Demo Mode Data Isolation

**User Story:** As a system administrator, I want demo mode data to be isolated from real data, so that demo usage doesn't pollute production statistics.

#### Acceptance Criteria

1. WHEN in demo mode, THE System SHALL NOT save classification results to the database
2. WHEN in demo mode, THE System SHALL NOT send actual SMS alerts
3. WHEN in demo mode, THE System SHALL display demo results in a temporary session-based store
4. WHEN demo mode is exited, THE System SHALL clear all demo session data
5. THE Analytics_Dashboard SHALL NOT include demo mode data in its calculations
