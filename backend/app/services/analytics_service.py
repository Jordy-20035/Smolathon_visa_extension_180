from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from app import models

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

    def get_traffic_lights_analytics(self) -> Dict:
        """Get traffic lights status analytics"""
        status_query = self.db.query(
            models.TrafficLight.status,
            func.count(models.TrafficLight.id)
        ).group_by(models.TrafficLight.status)
        
        by_status = {row.status: row.count for row in status_query.all()}
        
        # By district
        district_query = self.db.query(
            models.Location.district,
            func.count(models.TrafficLight.id)
        ).join(models.TrafficLight).group_by(models.Location.district)
        
        by_district = {row.district or 'Unknown': row.count for row in district_query.all()}
        
        return {
            "total_count": sum(by_status.values()),
            "by_status": by_status,
            "by_district": by_district
        }

    def get_comparison_analytics(self, period: str = "month") -> Dict:
        """Compare current period with previous period"""
        # This would compare current month vs previous month, etc.

        pass