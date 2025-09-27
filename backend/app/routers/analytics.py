from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app import models
from app.routers.auth import require_role, get_current_user
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsRequest, AnalyticsResponse, EvacuationAnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

def require_analytics_access(current_user: models.User = Depends(get_current_user)):
    """Allow both admin and redactor to access analytics"""
    if current_user.role not in ['admin', 'redactor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access analytics"
        )
    return current_user


@router.get("/public/dashboard")
def get_public_dashboard_analytics(db: Session = Depends(get_db)):
    """Get public dashboard analytics (no authentication required)"""
    service = AnalyticsService(db)
    
    # Only show non-financial data
    accidents_data = service.get_accidents_analytics()
    traffic_lights_data = service.get_traffic_lights_analytics()
    evacuations_data = service.get_evacuations_analytics()
    
    return {
        "accidents": {
            "total_count": accidents_data["total_count"],  # FIXED: Use dictionary access
            "time_series": accidents_data["time_series"],
            "by_severity": accidents_data["by_severity"]
        },
        "traffic_lights": {
            "total_count": traffic_lights_data["total_count"],
            "by_status": traffic_lights_data["by_status"],
            "by_district": traffic_lights_data["by_district"]
        },
        "evacuations": {  # Only show non-financial data to public
            "total_count": evacuations_data["total_count"],  # FIXED: Use dictionary access
            "time_series": evacuations_data["time_series"]
        }
    }


@router.get("/fines", response_model=AnalyticsResponse)
def get_fines_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)  
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
    current_user: models.User = Depends(require_analytics_access)  
):
    """Get accidents analytics with optional filters"""
    service = AnalyticsService(db)
    return service.get_accidents_analytics(start_date, end_date, district)

@router.get("/traffic-lights")
def get_traffic_lights_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)  
):
    """Get traffic lights status analytics"""
    service = AnalyticsService(db)
    return service.get_traffic_lights_analytics()


@router.get("/evacuations", response_model=EvacuationAnalyticsResponse)
def get_evacuations_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)  
):
    """Get evacuations analytics with optional filters"""
    service = AnalyticsService(db)
    return service.get_evacuations_analytics(start_date, end_date)

@router.get("/dashboard")
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)  
):
    """Get comprehensive dashboard analytics"""
    service = AnalyticsService(db)
    
    fines_data = service.get_fines_analytics()
    accidents_data = service.get_accidents_analytics()
    traffic_lights_data = service.get_traffic_lights_analytics()
    evacuations_data = service.get_evacuations_analytics()
    
    return {
        "fines": {
            "total_count": fines_data["total_count"],  
            "total_amount": fines_data["total_amount"],
            "time_series": fines_data["time_series"],
            "by_district": fines_data["by_district"]
        },
        "accidents": {
            "total_count": accidents_data["total_count"], 
            "time_series": accidents_data["time_series"],
            "by_severity": accidents_data["by_severity"],
            "by_type": accidents_data["by_type"]
        },
        "traffic_lights": traffic_lights_data,
        "evacuations": {
            "total_count": evacuations_data["total_count"],  
            "total_revenue": evacuations_data["total_revenue"],
            "total_dispatches": evacuations_data["total_dispatches"],
            "avg_tow_trucks": evacuations_data["avg_tow_trucks"],
            "time_series": evacuations_data["time_series"],
            "monthly_comparison": evacuations_data["monthly_comparison"]
        }
    }