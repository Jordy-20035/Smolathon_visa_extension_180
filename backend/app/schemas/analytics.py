from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import date, datetime

class AnalyticsRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    district: Optional[str] = None
    group_by: Optional[str] = None  # day, week, month, year

class TimeSeriesPoint(BaseModel):
    date: date
    count: int
    amount: Optional[float] = None

class AnalyticsResponse(BaseModel):
    total_count: int
    total_amount: Optional[float] = None
    time_series: List[TimeSeriesPoint]
    by_district: Dict[str, int]
    by_severity: Optional[Dict[str, int]] = None
    by_type: Optional[Dict[str, int]] = None

class ComparisonResponse(BaseModel):
    current_period: AnalyticsResponse
    previous_period: AnalyticsResponse
    change_percentage: float

# Add to schemas/analytics.py
class EvacuationAnalyticsResponse(BaseModel):
    total_count: int
    total_revenue: float
    total_dispatches: int
    avg_tow_trucks: float
    time_series: List[TimeSeriesPoint]
    monthly_comparison: Dict[str, float]
    
    class Config:
        from_attributes = True