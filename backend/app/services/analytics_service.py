from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from app import models
from app.models import TrafficLight, Location 
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_fines_analytics(self, start_date: Optional[date] = None, 
                          end_date: Optional[date] = None,
                          district: Optional[str] = None) -> Dict:
        """Get fines analytics with filters"""
        query = self.db.query(models.Fine)
        
        # Apply filters
        if start_date:
            query = query.filter(models.Fine.issued_at >= start_date)
        if end_date:
            query = query.filter(models.Fine.issued_at <= end_date)
        if district:
            query = query.join(models.Location).filter(models.Location.district == district)
        
        total_count = query.count()
        total_amount = query.with_entities(func.sum(models.Fine.amount)).scalar() or 0
        
        # Time series (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        time_series_query = self.db.query(
            func.date(models.Fine.issued_at).label('date'),
            func.count(models.Fine.id).label('count'),
            func.sum(models.Fine.amount).label('amount')
        ).filter(
            models.Fine.issued_at >= thirty_days_ago
        ).group_by(func.date(models.Fine.issued_at)).order_by('date')
        
        time_series = [
            {"date": row.date, "count": row.count, "amount": float(row.amount or 0)}
            for row in time_series_query.all()
        ]
        
        # By district
        district_query = self.db.query(
            models.Location.district,
            func.count(models.Fine.id)
        ).join(models.Fine).group_by(models.Location.district)
        
        by_district = {row.district or 'Unknown': row.count for row in district_query.all()}
        
        return {
            "total_count": total_count,
            "total_amount": float(total_amount),
            "time_series": time_series,
            "by_district": by_district
        }

    def get_accidents_analytics(self, start_date: Optional[date] = None,
                              end_date: Optional[date] = None,
                              district: Optional[str] = None) -> Dict:
        """Get accidents analytics with filters"""
        query = self.db.query(models.Accident)
        
        if start_date:
            query = query.filter(models.Accident.occurred_at >= start_date)
        if end_date:
            query = query.filter(models.Accident.occurred_at <= end_date)
        if district:
            query = query.join(models.Location).filter(models.Location.district == district)
        
        total_count = query.count()
        
        # By severity
        severity_query = self.db.query(
            models.Accident.severity,
            func.count(models.Accident.id)
        ).group_by(models.Accident.severity)
        
        by_severity = {row.severity or 'Unknown': row.count for row in severity_query.all()}
        
        # By type
        type_query = self.db.query(
            models.Accident.accident_type,
            func.count(models.Accident.id)
        ).group_by(models.Accident.accident_type)
        
        by_type = {row.accident_type: row.count for row in type_query.all()}
        
        # Time series
        thirty_days_ago = datetime.now() - timedelta(days=30)
        time_series_query = self.db.query(
            func.date(models.Accident.occurred_at).label('date'),
            func.count(models.Accident.id).label('count')
        ).filter(
            models.Accident.occurred_at >= thirty_days_ago
        ).group_by(func.date(models.Accident.occurred_at)).order_by('date')
        
        time_series = [
            {"date": row.date, "count": row.count}
            for row in time_series_query.all()
        ]
        
        return {
            "total_count": total_count,
            "time_series": time_series,
            "by_severity": by_severity,
            "by_type": by_type
        }

# In analytics_service.py - fix the get_traffic_lights_analytics method

    def get_traffic_lights_analytics(self):
        """Get traffic lights analytics"""
        try:
            # Get total count directly
            total_count = self.db.query(func.count(TrafficLight.id)).scalar() or 0
            
            # Get traffic lights count by status
            status_counts = self.db.query(
                TrafficLight.status,
                func.count(TrafficLight.id)
            ).group_by(TrafficLight.status).all()
            
            by_status = {}
            for status, count in status_counts:
                by_status[status] = int(count) if count else 0
            
            # Get traffic lights count by district
            district_counts = self.db.query(
                Location.district,
                func.count(TrafficLight.id)
            ).join(TrafficLight.location).group_by(Location.district).all()
            
            by_district = {}
            for district, count in district_counts:
                if district:
                    by_district[district] = int(count) if count else 0
            
            return {
                "total_count": total_count,
                "by_status": by_status,
                "by_district": by_district
            }
            
        except Exception as e:
            logger.error(f"Traffic lights analytics error: {e}")
            return {
                "total_count": 0,
                "by_status": {},
                "by_district": {}
            }

    # Add to backend/app/services/analytics_service.py

    def get_evacuations_analytics(self, start_date: Optional[date] = None, end_date: Optional[date] = None):
        """Get evacuation analytics"""
        query = self.db.query(models.Evacuation)
        
        # Apply date filters if provided - use evacuated_at instead of date
        if start_date:
            query = query.filter(models.Evacuation.evacuated_at >= start_date)
        if end_date:
            query = query.filter(models.Evacuation.evacuated_at <= end_date)
        
        evacuations = query.all()
        
        if not evacuations:
            return {
                "total_count": 0,
                "total_revenue": 0,
                "total_dispatches": 0,
                "avg_tow_trucks": 0,
                "time_series": [],
                "monthly_comparison": {
                    "current_month": 0,
                    "previous_month": 0,
                    "change_percentage": 0
                }
            }
        
        # Use the correct field names from your model
        total_evacuations = sum(e.evacuations_count for e in evacuations)  # FIXED: evacuations_count
        total_revenue = sum(e.revenue for e in evacuations)  # FIXED: revenue
        total_dispatches = sum(e.dispatches_count for e in evacuations)  # FIXED: dispatches_count
        avg_tow_trucks = sum(e.towing_vehicles_count for e in evacuations) / len(evacuations)  # FIXED: towing_vehicles_count
        
        # Time series data (group by month)
        time_series = self._get_evacuations_time_series(evacuations)
        
        # Monthly comparison
        monthly_comparison = self._get_evacuations_monthly_comparison(evacuations)
        
        return {
            "total_count": total_evacuations,
            "total_revenue": total_revenue,
            "total_dispatches": total_dispatches,
            "avg_tow_trucks": round(avg_tow_trucks, 1),
            "time_series": time_series,
            "monthly_comparison": monthly_comparison
        }

    def _get_evacuations_time_series(self, evacuations):
        """Convert evacuations to time series data"""
        from collections import defaultdict
        from datetime import datetime
        
        monthly_data = defaultdict(lambda: {"evacuations": 0, "revenue": 0, "dispatches": 0})
        
        for evacuation in evacuations:
            if evacuation.evacuated_at:  # FIXED: use evacuated_at
                month_key = evacuation.evacuated_at.strftime("%Y-%m")
                monthly_data[month_key]["evacuations"] += evacuation.evacuations_count  # FIXED
                monthly_data[month_key]["revenue"] += evacuation.revenue  # FIXED
                monthly_data[month_key]["dispatches"] += evacuation.dispatches_count  # FIXED
        
        time_series = []
        for month, data in sorted(monthly_data.items()):
            time_series.append({
                "date": f"{month}-01",
                "count": data["evacuations"],
                "amount": data["revenue"],
                "dispatches": data["dispatches"]
            })
        
        return time_series

    def _get_evacuations_monthly_comparison(self, evacuations):
        """Compare current month with previous month"""
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        monthly_totals = defaultdict(int)
        
        for evacuation in evacuations:
            if evacuation.evacuated_at:  # FIXED: use evacuated_at
                month_key = evacuation.evacuated_at.strftime("%Y-%m")
                monthly_totals[month_key] += evacuation.evacuations_count  # FIXED: evacuations_count
        
        # Get current and previous month
        current_date = datetime.now()
        current_month = current_date.strftime("%Y-%m")
        previous_month = (current_date.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        
        current_count = monthly_totals.get(current_month, 0)
        previous_count = monthly_totals.get(previous_month, 0)
        
        if previous_count > 0:
            change_percentage = ((current_count - previous_count) / previous_count) * 100
        else:
            change_percentage = 100 if current_count > 0 else 0
        
        return {
            "current_month": current_count,
            "previous_month": previous_count,
            "change_percentage": round(change_percentage, 1)
        }

    def get_comparison_analytics(self, period: str = "month") -> Dict:
        """Compare current period with previous period"""
        # This would compare current month vs previous month, etc.

        pass