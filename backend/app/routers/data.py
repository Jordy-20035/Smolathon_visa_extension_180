from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/data", tags=["data"])

@router.get("/fines/", response_model=List[schemas.Fine])
def get_fines(
    skip: int = 0,
    limit: int = 100,
    visibility: str = "public",  # Only show public data to unauthorized users
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Citizens can only see public data
    if current_user.role == "citizen":
        visibility = "public"
    
    query = db.query(models.Fine).filter(models.Fine.visibility == visibility)
    return query.offset(skip).limit(limit).all()

@router.post("/fines/", response_model=schemas.Fine)
def create_fine(
    fine: schemas.FineCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    db_fine = models.Fine(**fine.dict())
    db.add(db_fine)
    db.commit()
    db.refresh(db_fine)
    return db_fine