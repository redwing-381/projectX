"""Keyword rules management routes."""

import logging

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.api.deps import get_db_optional
from src.db import crud
from src.config import cache

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/keywords", response_class=HTMLResponse)
async def keywords_page(request: Request, db: Session | None = Depends(get_db_optional)):
    """Keyword rules management page."""
    keywords = []
    
    if db is not None:
        try:
            keywords = crud.get_keywords(db)
        except Exception as e:
            logger.warning(f"Could not fetch keywords: {e}")
    
    return templates.TemplateResponse("keywords.html", {
        "request": request,
        "active_page": "keywords",
        "keywords": keywords,
    })


@router.post("/keywords/add")
async def add_keyword(
    keyword: str = Form(...),
    db: Session | None = Depends(get_db_optional),
):
    """Add a new keyword rule."""
    if db is not None:
        try:
            crud.add_keyword(db, keyword)
            cache.invalidate("keywords")  # Invalidate cache
        except IntegrityError:
            db.rollback()
            logger.info(f"Keyword already exists: {keyword}")
        except Exception as e:
            logger.error(f"Could not add keyword: {e}")
    
    return RedirectResponse("/keywords", status_code=303)


@router.post("/keywords/delete/{id}")
async def delete_keyword(id: int, db: Session | None = Depends(get_db_optional)):
    """Delete a keyword rule."""
    if db is not None:
        try:
            crud.remove_keyword(db, id)
            cache.invalidate("keywords")  # Invalidate cache
        except Exception as e:
            logger.error(f"Could not delete keyword: {e}")
    
    return RedirectResponse("/keywords", status_code=303)
