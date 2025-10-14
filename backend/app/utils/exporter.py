import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import io
from datetime import datetime
import json

class DataExporter:
    def __init__(self, db: Session):
        self.db = db
    
    def export_to_csv(self, query: str, params: Dict[str, Any] = None) -> bytes:
        """Export query results to CSV"""
        df = self._execute_query(query, params)
        return self._dataframe_to_bytes(df, 'csv')
    
    def export_to_excel(self, query: str, params: Dict[str, Any] = None, sheet_name: str = "Data") -> bytes:
        """Export query results to Excel"""
        df = self._execute_query(query, params)
        return self._dataframe_to_bytes(df, 'excel', sheet_name)
    
    def export_model_to_csv(self, model_class, filters: Dict[str, Any] = None) -> bytes:
        """Export entire model to CSV"""
        query = self.db.query(model_class)
        
        if filters:
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
        
        results = query.all()
        
        # Convert to DataFrame
        data = []
        for obj in results:
            row = {}
            for column in obj.__table__.columns:
                value = getattr(obj, column.name)
                # Convert UUID and datetime to string
                if hasattr(value, 'hex'):  # UUID
                    row[column.name] = str(value)
                elif isinstance(value, datetime):
                    row[column.name] = value.isoformat()
                else:
                    row[column.name] = value
            data.append(row)
        
        df = pd.DataFrame(data)
        return self._dataframe_to_bytes(df, 'csv')
    
    def _execute_query(self, query: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        if params is None:
            params = {}
        
        result = self.db.execute(text(query), params)
        columns = [col for col in result.keys()]
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return pd.DataFrame(data)
    
    def _dataframe_to_bytes(self, df: pd.DataFrame, format: str, sheet_name: str = "Data") -> bytes:
        """Convert DataFrame to bytes in specified format"""
        buffer = io.BytesIO()
        
        if format == 'csv':
            df.to_csv(buffer, index=False, encoding='utf-8')
        elif format == 'excel':
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        buffer.seek(0)
        return buffer.getvalue()

# Predefined queries for common exports
class PredefinedExports:
    def __init__(self, db: Session):
        self.exporter = DataExporter(db)
    

    def export_fines(self, format: str = 'csv') -> bytes:
        """Export fines data"""
        query = """
        SELECT 
            f.issued_at as "Дата нарушения",
            v.plate_number as "Госномер",
            f.violation_code as "Код нарушения", 
            f.amount as "Сумма штрафа",
            l.address as "Место нарушения",
            l.district as "Район"
        FROM fines f
        JOIN vehicles v ON f.vehicle_id = v.id
        JOIN locations l ON f.location_id = l.id
        WHERE f.visibility = 'public'
        ORDER BY f.issued_at DESC
        """
        return self._export_query(query, format, "Штрафы")

    def export_accidents(self, format: str = 'csv') -> bytes:
        """Export accident data"""
        query = """
        SELECT 
            a.accident_type as "Тип ДТП",
            a.severity as "Тяжесть",
            a.casualties as "Пострадавшие",
            a.occurred_at as "Дата и время",
            l.address as "Место",
            l.district as "Район"
        FROM accidents a
        JOIN locations l ON a.location_id = l.id
        WHERE a.visibility = 'public'
        ORDER BY a.occurred_at DESC
        """
        return self._export_query(query, format, "ДТП")

    def export_traffic_lights(self, format: str = 'csv') -> bytes:
        """Export traffic lights data"""
        query = """
        SELECT 
            tl.type as "Тип светофора",
            tl.status as "Статус",
            tl.install_date as "Дата установки",
            tl.last_maintenance as "Последнее обслуживание",
            l.address as "Адрес",
            l.district as "Район"
        FROM traffic_lights tl
        JOIN locations l ON tl.location_id = l.id
        ORDER BY tl.install_date DESC
        """
        return self._export_query(query, format, "Светофоры")

    def export_evacuations(self, format: str = 'csv') -> bytes:
        """Export evacuations data"""
        query = """
        SELECT 
            e.evacuated_at as "Дата эвакуации",
            e.towing_vehicles_count as "Количество эвакуаторов", 
            e.dispatches_count as "Количество выездов",
            e.evacuations_count as "Количество эвакуаций",
            e.revenue as "Поступления",
            l.address as "Место",
            l.district as "Район"
        FROM evacuations e
        JOIN locations l ON e.location_id = l.id
        WHERE e.visibility = 'public'
        ORDER BY e.evacuated_at DESC
        """
        return self._export_query(query, format, "Эвакуации")
    
    def _export_query(self, query: str, format: str, filename: str) -> bytes:
        """Helper method to export query results"""
        if format == 'csv':
            return self.exporter.export_to_csv(query)
        elif format == 'excel':
            return self.exporter.export_to_excel(query, sheet_name=filename)
        else:
            raise ValueError("Unsupported format")