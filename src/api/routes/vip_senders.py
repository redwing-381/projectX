"""VIP senders management routes."""

import logging

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.api.deps import get_db_optional
from src.db import crud

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/vip-senders", response_class=HTMLResponse)
async def vip_senders_page(request: Request, db: Session | None = Depends(get_db_optional)):
    """VIP senders management page."""
    senders = []
    
    if db is not None:
        try:
            senders = crud.get_vip_senders(db)
        except Exception as e:
            logger.warning(f"Could not fetch VIP senders: {e}")
    
    return templates.TemplateResponse("vip_senders.html", {
        "request": request,
        "active_page": "vip",
        "senders": senders,
    })


@router.post("/vip-senders/add")
async def add_vip_sender(
    email: str = Form(...),
    db: Session | None = Depends(get_db_optional),
):
    """Add a new VIP sender."""
    if db is not None:
        try:
            crud.add_vip_sender(db, email)
        except IntegrityError:
            db.rollback()
            logger.info(f"VIP sender already exists: {email}")
        except Exception as e:
            logger.error(f"Could not add VIP sender: {e}")
    
    return RedirectResponse("/vip-senders", status_code=303)


@router.post("/vip-senders/delete/{id}")
async def delete_vip_sender(id: int, db: Session | None = Depends(get_db_optional)):
    """Delete a VIP sender."""
    if db is not None:
        try:
            crud.remove_vip_sender(db, id)
        except Exception as e:
            logger.error(f"Could not delete VIP sender: {e}")
    
    return RedirectResponse("/vip-senders", status_code=303)
