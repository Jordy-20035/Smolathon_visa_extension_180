from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.database import get_db
from app import models
from app.routers.auth import require_role
from app.services.content_service import ContentService
from app.schemas.content import ContentPage, ContentPageCreate, ContentPageUpdate, ContentPageList

router = APIRouter(prefix="/content", tags=["content"])

# Public endpoints (no authentication required)
@router.get("/pages", response_model=List[ContentPage])
def get_public_pages(
    page_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get published content pages for public access"""
    service = ContentService(db)
    return service.get_public_pages(page_type)

@router.get("/pages/{slug}", response_model=ContentPage)
def get_page_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a specific published page by slug"""
    service = ContentService(db)
    page = service.get_page_by_slug(slug)
    if not page or not page.is_published:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.get("/news", response_model=List[ContentPage])
def get_news_list(db: Session = Depends(get_db)):
    """Get published news articles"""
    service = ContentService(db)
    return service.get_public_pages("news")

# Admin endpoints (require authentication)
@router.post("/pages", response_model=ContentPage)
def create_page(
    page_data: ContentPageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("redactor"))
):
    """Create a new content page (admin only)"""
    service = ContentService(db)
    
    # Check if slug already exists
    existing_page = service.get_page_by_slug(page_data.slug)
    if existing_page:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    return service.create_page(page_data.model_dump(), current_user.id)

@router.put("/pages/{page_id}", response_model=ContentPage)
def update_page(
    page_id: uuid.UUID,
    page_data: ContentPageUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("redactor"))
):
    """Update a content page (admin only)"""
    service = ContentService(db)
    
    page = service.update_page(page_id, page_data.model_dump(exclude_unset=True))
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return page

@router.delete("/pages/{page_id}")
def delete_page(
    page_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Delete a content page (admin only)"""
    service = ContentService(db)
    
    if not service.delete_page(page_id):
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"message": "Page deleted successfully"}

@router.get("/admin/pages", response_model=ContentPageList)
def get_all_pages_admin(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("redactor"))
):
    """Get all pages for admin panel with pagination"""
    service = ContentService(db)
    result = service.get_all_pages_admin(page, per_page)
    
    return ContentPageList(
        items=result["items"],
        total=result["total"]
    )