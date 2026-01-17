# Codebase Modularization Requirements

## Overview
Refactor the ProjectX codebase to follow industry-standard modular architecture patterns, improving maintainability, testability, and scalability.

## Current Issues
1. **Monolithic web.py** - 700+ lines with all routes mixed together
2. **Repeated patterns** - Database session handling duplicated across routes
3. **Mixed concerns** - Web pages, API endpoints, and mobile API in one file
4. **Inline models** - Pydantic models defined in route files instead of schemas
5. **No dependency injection** - Direct SessionLocal() calls everywhere
6. **No service layer** - Routes directly call CRUD functions

## Requirements

### REQ-1: Split Route Modules
Split `src/api/web.py` into focused route modules:
- `src/api/routes/dashboard.py` - Dashboard and home page
- `src/api/routes/history.py` - Alert history page
- `src/api/routes/settings.py` - Settings management
- `src/api/routes/vip_senders.py` - VIP sender management
- `src/api/routes/keywords.py` - Keyword rules management
- `src/api/routes/notifications.py` - Notifications page
- `src/api/routes/architecture.py` - Architecture page
- `src/api/routes/mobile_api.py` - Mobile app API endpoints
- `src/api/routes/monitoring_api.py` - CLI monitoring API endpoints

### REQ-2: Dependency Injection for Database
Create proper FastAPI dependency injection for database sessions:
- `src/api/deps.py` - Shared dependencies (db session, auth)
- Use `Depends(get_db)` pattern consistently
- Remove all direct `SessionLocal()` calls from routes

### REQ-3: Move Pydantic Models to Schemas
Move all API request/response models to `src/models/schemas.py`:
- `NotificationPayload`
- `NotificationBatchRequest`
- `NotificationBatchResponse`
- Any other inline models

### REQ-4: Create Service Layer
Add service layer between routes and CRUD:
- `src/services/notification_service.py` - Notification processing logic
- `src/services/monitoring_service.py` - Monitoring control logic
- Services handle business logic, routes handle HTTP concerns

### REQ-5: Update Steering Documentation
Update `.kiro/steering/` docs to enforce new standards:
- Module size limits (max 200 lines per file)
- Separation of concerns guidelines
- Dependency injection patterns
- Code organization standards

## Success Criteria
- No single Python file exceeds 200 lines
- All database access uses dependency injection
- Clear separation between routes, services, and data access
- All Pydantic models in schemas.py
- Updated steering docs enforce standards
