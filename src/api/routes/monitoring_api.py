"""Monitoring API routes for CLI."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_db_optional, verify_api_key
from src.db import crud

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/monitoring")


@router.get("")
async def get_monitoring_status(
    authenticated: bool = Depends(verify_api_key),
    db: Session | None = Depends(get_db_optional),
):
    """Get current monitoring status (for CLI)."""
    from src.main import monitoring_running
    
    enabled = False
    interval = 5
    
    if db is not None:
        try:
            enabled = crud.get_monitoring_enabled(db)
            interval = crud.get_check_interval(db)
        except Exception as e:
            logger.warning(f"Could not fetch monitoring status: {e}")
    
    return {
        "enabled": enabled,
        "running": monitoring_running,
        "interval_minutes": interval,
    }


@router.get("/unified")
async def get_unified_monitoring_status(
    authenticated: bool = Depends(verify_api_key),
    db: Session | None = Depends(get_db_optional),
):
    """Get unified monitoring status across all platforms (email + mobile)."""
    from src.main import monitoring_running
    
    if db is None:
        return {"error": "Database not connected"}
    
    try:
        status = crud.get_global_monitoring_status(db)
        status["email_monitoring"]["running"] = monitoring_running
        return status
    except Exception as e:
        logger.error(f"Could not fetch unified status: {e}")
        return {"error": str(e)}


@router.post("/start")
async def start_monitoring(
    include_mobile: bool = Query(False, description="Also start mobile monitoring"),
    authenticated: bool = Depends(verify_api_key),
    db: Session | None = Depends(get_db_optional),
):
    """Enable scheduled monitoring (for CLI)."""
    if db is not None:
        try:
            crud.set_monitoring_enabled(db, True)
            message = "Scheduled email monitoring enabled"
            
            # Optionally start mobile monitoring too
            if include_mobile:
                count = crud.set_all_devices_monitoring(db, True)
                crud.queue_mobile_command(db, "start_monitoring", None)
                message += f", mobile monitoring enabled for {count} devices"
            
            return {"success": True, "message": message}
        except Exception as e:
            logger.error(f"Could not enable monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Database not connected"}


@router.post("/stop")
async def stop_monitoring(
    include_mobile: bool = Query(False, description="Also stop mobile monitoring"),
    authenticated: bool = Depends(verify_api_key),
    db: Session | None = Depends(get_db_optional),
):
    """Disable scheduled monitoring (for CLI)."""
    if db is not None:
        try:
            crud.set_monitoring_enabled(db, False)
            message = "Scheduled email monitoring disabled"
            
            # Optionally stop mobile monitoring too
            if include_mobile:
                count = crud.set_all_devices_monitoring(db, False)
                crud.queue_mobile_command(db, "stop_monitoring", None)
                message += f", mobile monitoring disabled for {count} devices"
            
            return {"success": True, "message": message}
        except Exception as e:
            logger.error(f"Could not disable monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Database not connected"}


@router.post("/start-all")
async def start_all_monitoring(
    authenticated: bool = Depends(verify_api_key),
    db: Session | None = Depends(get_db_optional),
):
    """Start monitoring on ALL platforms (email + mobile)."""
    if db is None:
        return {"success": False, "error": "Database not connected"}
    
    try:
        # Start email monitoring
        crud.set_monitoring_enabled(db, True)
        
        # Start mobile monitoring
        device_count = crud.set_all_devices_monitoring(db, True)
        crud.queue_mobile_command(db, "start_monitoring", None)
        
        return {
            "success": True,
            "message": f"All monitoring started (email + {device_count} mobile devices)",
        }
    except Exception as e:
        logger.error(f"Could not start all monitoring: {e}")
        return {"success": False, "error": str(e)}


@router.post("/stop-all")
async def stop_all_monitoring(
    authenticated: bool = Depends(verify_api_key),
    db: Session | None = Depends(get_db_optional),
):
    """Stop monitoring on ALL platforms (email + mobile)."""
    if db is None:
        return {"success": False, "error": "Database not connected"}
    
    try:
        # Stop email monitoring
        crud.set_monitoring_enabled(db, False)
        
        # Stop mobile monitoring
        device_count = crud.set_all_devices_monitoring(db, False)
        crud.queue_mobile_command(db, "stop_monitoring", None)
        
        return {
            "success": True,
            "message": f"All monitoring stopped (email + {device_count} mobile devices)",
        }
    except Exception as e:
        logger.error(f"Could not stop all monitoring: {e}")
        return {"success": False, "error": str(e)}


@router.post("/interval")
async def set_monitoring_interval(
    minutes: int = Form(...),
    authenticated: bool = Depends(verify_api_key),
    db: Session | None = Depends(get_db_optional),
):
    """Set monitoring interval (for CLI)."""
    if minutes < 1 or minutes > 1440:
        return {"success": False, "error": "Interval must be between 1 and 1440 minutes"}
    
    if db is not None:
        try:
            crud.set_check_interval(db, minutes)
            return {"success": True, "message": f"Interval set to {minutes} minutes"}
        except Exception as e:
            logger.error(f"Could not set interval: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Database not connected"}
