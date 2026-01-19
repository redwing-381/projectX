"""Route modules for the web application."""

from fastapi import APIRouter

from src.api.routes import (
    dashboard,
    history,
    settings,
    vip_senders,
    keywords,
    notifications,
    architecture,
    mobile_api,
    monitoring_api,
    demo,
    analytics,
    quick_actions,
)

# Aggregate all routers
router = APIRouter()

# Web pages
router.include_router(dashboard.router, tags=["dashboard"])
router.include_router(history.router, tags=["history"])
router.include_router(analytics.router, tags=["analytics"])
router.include_router(settings.router, tags=["settings"])
router.include_router(vip_senders.router, tags=["vip-senders"])
router.include_router(keywords.router, tags=["keywords"])
router.include_router(notifications.router, tags=["notifications"])
router.include_router(architecture.router, tags=["architecture"])
router.include_router(demo.router, tags=["demo"])

# API endpoints
router.include_router(mobile_api.router, tags=["mobile-api"])
router.include_router(monitoring_api.router, tags=["monitoring-api"])
router.include_router(quick_actions.router, tags=["quick-actions"])
