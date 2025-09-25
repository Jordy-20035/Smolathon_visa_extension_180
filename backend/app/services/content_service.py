from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app import models
import uuid

class ContentService:
    def __init__(self, db: Session):
        self.db = db

    def get_public_pages(self, page_type: Optional[str] = None) -> List[models.ContentPage]:
        """Get published pages for public access"""
        query = self.db.query(models.ContentPage).filter(
            models.ContentPage.is_published == True
        )
        
        if page_type:
            query = query.filter(models.ContentPage.page_type == page_type)
            
        return query.order_by(models.ContentPage.created_at.desc()).all()

    def get_page_by_slug(self, slug: str) -> Optional[models.ContentPage]:
        """Get a single page by slug (public or admin)"""
        return self.db.query(models.ContentPage).filter(
            models.ContentPage.slug == slug
        ).first()

    def create_page(self, page_data: dict, author_id: uuid.UUID) -> models.ContentPage:
        """Create a new content page"""
        page = models.ContentPage(**page_data, author_id=author_id)
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page

    def update_page(self, page_id: uuid.UUID, update_data: dict) -> Optional[models.ContentPage]:
        """Update a content page"""
        page = self.db.query(models.ContentPage).filter(models.ContentPage.id == page_id).first()
        if not page:
            return None
            
        for field, value in update_data.items():
            setattr(page, field, value)
            
        self.db.commit()
        self.db.refresh(page)
        return page

    def delete_page(self, page_id: uuid.UUID) -> bool:
        """Delete a content page"""
        page = self.db.query(models.ContentPage).filter(models.ContentPage.id == page_id).first()
        if not page:
            return False
            
        self.db.delete(page)
        self.db.commit()
        return True

    def get_all_pages_admin(self, page: int = 1, per_page: int = 20) -> dict:
        """Get all pages for admin panel with pagination"""
        query = self.db.query(models.ContentPage)
        total = query.count()
        
        items = query.order_by(models.ContentPage.created_at.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }