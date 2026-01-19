"""Demo mode routes for hackathon presentation."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from src.services.demo import activate_demo, deactivate_demo

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/demo/activate")
async def activate_demo_mode(request: Request):
    """Activate demo mode and redirect to dashboard."""
    activate_demo(request.session)
    logger.info("Demo mode activated")
    return RedirectResponse(url="/", status_code=303)


@router.post("/demo/deactivate")
async def deactivate_demo_mode(request: Request):
    """Deactivate demo mode and redirect to dashboard."""
    deactivate_demo(request.session)
    logger.info("Demo mode deactivated")
    return RedirectResponse(url="/", status_code=303)
