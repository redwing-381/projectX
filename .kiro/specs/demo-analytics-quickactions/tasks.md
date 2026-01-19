# Implementation Plan: Demo Mode, Analytics Dashboard & Quick Actions

## Overview

Implementation of three features to enhance ProjectX for hackathon presentation. Tasks are ordered to build incrementally with demo mode first (most critical for judges), then analytics, then quick actions.

## Tasks

- [x] 1. Set up session middleware for demo mode
  - Add session middleware to FastAPI app
  - Configure session secret key from environment
  - _Requirements: 5.3_

- [ ] 2. Create Demo Mode Service
  - [x] 2.1 Create demo service with sample emails
    - Create `src/services/demo.py`
    - Define 10 diverse sample emails (VIP, keyword, AI classification scenarios)
    - Implement `get_sample_emails()`, `is_demo_mode()`, `activate_demo()`, `deactivate_demo()`
    - _Requirements: 1.5, 2.3, 2.4, 2.5_

  - [x] 2.2 Implement demo results session storage
    - Implement `store_demo_results()` and `get_demo_results()`
    - Add result rotation (keep last 20)
    - _Requirements: 5.3_

- [ ] 3. Integrate demo mode into pipeline
  - [x] 3.1 Modify pipeline to support demo mode
    - Add `demo_mode` parameter to pipeline.run()
    - Skip DB save when demo_mode=True
    - Skip real SMS when demo_mode=True (simulate instead)
    - _Requirements: 2.6, 5.1, 5.2_

  - [ ]* 3.2 Write property test for demo isolation
    - **Property 1: Demo Mode Data Isolation**
    - **Validates: Requirements 2.6, 5.1, 5.2**

- [ ] 4. Create demo mode UI
  - [x] 4.1 Add demo mode banner and controls to base template
    - Add demo indicator banner (yellow/orange)
    - Add "Exit Demo" button when active
    - _Requirements: 1.2, 1.4_

  - [x] 4.2 Add "Try Demo Mode" button to dashboard
    - Show when Gmail not configured OR always as option
    - Style prominently for judges
    - _Requirements: 1.1_

  - [x] 4.3 Create demo mode routes
    - POST `/demo/activate` - activate demo mode
    - POST `/demo/deactivate` - deactivate demo mode
    - Modify `/web/check` to use demo pipeline when active
    - _Requirements: 1.2, 1.4, 2.1_

- [x] 5. Checkpoint - Demo Mode Complete
  - Ensure demo mode works end-to-end
  - Test: activate → check emails → see results → deactivate

- [x] 6. Create Analytics Service
  - [x] 6.1 Implement analytics calculations
    - Create `src/services/analytics.py`
    - Implement `get_emails_by_day()` with date grouping
    - Implement `get_urgency_ratio()` with count aggregation
    - Implement `get_top_senders()` with sender extraction and grouping
    - Implement `get_summary_metrics()` for dashboard cards
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 6.2 Write property test for analytics calculations
    - **Property 3: Analytics Calculations Correctness**
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [x] 7. Create Analytics Dashboard UI
  - [x] 7.1 Create analytics page template
    - Create `src/templates/analytics.html`
    - Add Chart.js for visualizations
    - Create line chart for emails by day
    - Create pie chart for urgency ratio
    - Create bar chart for top senders
    - Add summary metric cards
    - Handle empty states
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 7.2 Create analytics route
    - Create `src/api/routes/analytics.py`
    - GET `/analytics` - render analytics page
    - GET `/api/analytics/data` - return JSON for charts
    - _Requirements: 3.6_

  - [x] 7.3 Add analytics to navigation
    - Add "Analytics" link to sidebar
    - Position between History and Architecture
    - _Requirements: 3.6_

- [x] 8. Checkpoint - Analytics Complete
  - Ensure charts render correctly
  - Test with real data and empty state

- [x] 9. Create Quick Actions
  - [x] 9.1 Create quick actions API
    - Create `src/api/routes/quick_actions.py`
    - POST `/api/quick-actions/add-vip` - add sender to VIP
    - GET `/api/quick-actions/check-vip` - check if sender is VIP
    - Implement email extraction from sender string
    - _Requirements: 4.2_

  - [ ]* 9.2 Write property test for VIP addition
    - **Property 4: Quick Action VIP Addition**
    - **Validates: Requirements 4.2, 4.3**

  - [x] 9.3 Add quick action buttons to dashboard
    - Add "Add to VIP" button to recent alerts
    - Implement AJAX call on click
    - Show success/already VIP feedback
    - _Requirements: 4.1, 4.3, 4.4, 4.5_

  - [x] 9.4 Add quick action buttons to history page
    - Add "Add to VIP" button to history table
    - Reuse same AJAX logic
    - _Requirements: 4.5_

- [x] 10. Final Checkpoint
  - Ensure all features work together
  - Test demo mode → analytics → quick actions flow
  - Verify no regressions in existing functionality

## Notes

- Tasks marked with `*` are optional property tests
- Demo mode is highest priority (critical for hackathon judges)
- Chart.js will be loaded from CDN for simplicity
- Session uses signed cookies (no server-side storage needed)
