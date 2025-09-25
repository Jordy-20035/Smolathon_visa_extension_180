from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app import models
from app.routers.auth import require_role
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsRequest, AnalyticsResponse

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/fines", response_model=AnalyticsResponse)
def get_fines_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("redactor"))  # Redactor or admin can access
):
    """Get fines analytics with optional filters"""
    service = AnalyticsService(db)
    return service.get_fines_analytics(start_date, end_date, district)

@router.get("/accidents", response_model=AnalyticsResponse)
def get_accidents_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("redactor"))
):
    """Get accidents analytics with optional filters"""
    service = AnalyticsService(db)
    return service.get_accidents_analytics(start_date, end_date, district)

@router.get("/traffic-lights")
def get_traffic_lights_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("redactor"))
):
    """Get traffic lights status analytics"""
    service = AnalyticsService(db)
    return service.get_traffic_lights_analytics()

@router.get("/dashboard")
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("redactor"))
):
    """Get comprehensive dashboard analytics"""
    service = AnalyticsService(db)
    
    return {
        "fines": service.get_fines_analytics(),
        "accidents": service.get_accidents_analytics(),
        "traffic_lights": service.get_traffic_lights_analytics()
    }