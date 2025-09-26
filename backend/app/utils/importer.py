import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import inspect
import uuid
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self, db: Session):
        self.db = db
    
    def import_csv(self, file_content: bytes, model_class, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Import data from CSV file"""
        try:
            # Read CSV
            df = pd.read_csv(io.BytesIO(file_content))
            return self._import_dataframe(df, model_class, column_mapping)
        except Exception as e:
            logger.error(f"CSV import error: {e}")
            raise ValueError(f"CSV import failed: {str(e)}")
    
    def import_excel(self, file_content: bytes, model_class, column_mapping: Dict[str, str], sheet_name: str = 0) -> Dict[str, Any]:
        """Import data from Excel file"""
        try:
            # Read Excel
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
            return self._import_dataframe(df, model_class, column_mapping)
        except Exception as e:
            logger.error(f"Excel import error: {e}")
            raise ValueError(f"Excel import failed: {str(e)}")
    
    def _import_dataframe(self, df: pd.DataFrame, model_class, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Process DataFrame and import data"""
        # Validate column mapping
        self._validate_mapping(df.columns, column_mapping)
        
        # Rename columns according to mapping
        df = df.rename(columns=column_mapping)
        
        # Convert DataFrame to records
        records = df.to_dict('records')
        
        # Import records
        return self._import_records(records, model_class)
    
    def _validate_mapping(self, file_columns: List[str], column_mapping: Dict[str, str]):
        """Validate that all mapped columns exist in the file"""
        for file_col in column_mapping.keys():
            if file_col not in file_columns:
                raise ValueError(f"Column '{file_col}' not found in file")
    
    def _import_records(self, records: List[Dict[str, Any]], model_class) -> Dict[str, Any]:
        """Import records into database"""
        successful = 0
        failed = 0
        errors = []
        
        for i, record in enumerate(records, 1):
            try:
                # Clean and validate record
                cleaned_record = self._clean_record(record, model_class)
                
                # Create model instance
                db_obj = model_class(**cleaned_record)
                self.db.add(db_obj)
                successful += 1
                
            except Exception as e:
                failed += 1
                errors.append(f"Row {i}: {str(e)}")
                logger.warning(f"Failed to import row {i}: {e}")
        
        # Commit all successful imports
        if successful > 0:
            self.db.commit()
        
        return {
            "total_processed": len(records),
            "successful": successful,
            "failed": failed,
            "errors": errors
        }
    
    def _clean_record(self, record: Dict[str, Any], model_class) -> Dict[str, Any]:
        """Clean and validate record data"""
        cleaned = {}
        mapper = inspect(model_class)
        
        for key, value in record.items():
            if pd.isna(value) or value == '':
                continue  # Skip empty values
                
            # Get column info from model
            column = mapper.columns.get(key)
            if column is None:
                continue  # Skip unknown columns
                
            # Type conversion
            cleaned[key] = self._convert_value(value, column.type)
        
        return cleaned
    
    def _convert_value(self, value, column_type):
        """Convert value to appropriate type based on column type"""
        try:
            # Handle UUID fields
            if hasattr(column_type, 'python_type') and column_type.python_type == uuid.UUID:
                return uuid.UUID(str(value))
            
            # Handle datetime fields
            elif hasattr(column_type, 'python_type') and column_type.python_type == datetime:
                if isinstance(value, str):
                    return pd.to_datetime(value).to_pydatetime()
                return value
            
            # Handle numeric fields
            elif hasattr(column_type, 'python_type') and column_type.python_type in (int, float):
                return float(value) if '.' in str(value) else int(value)
            
            # Default: return as string
            return str(value) if value is not None else None
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Conversion error for value '{value}': {e}")
            return value

# Model-specific importers
class FineImporter(DataImporter):
    def import_fines(self, file_content: bytes, file_type: str, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        from app.models import Fine
        if file_type == 'csv':
            return self.import_csv(file_content, Fine, column_mapping)
        elif file_type == 'excel':
            return self.import_excel(file_content, Fine, column_mapping)
        else:
            raise ValueError("Unsupported file type")

class AccidentImporter(DataImporter):
    def import_accidents(self, file_content: bytes, file_type: str, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        from app.models import Accident
        if file_type == 'csv':
            return self.import_csv(file_content, Accident, column_mapping)
        elif file_type == 'excel':
            return self.import_excel(file_content, Accident, column_mapping)
        else:
            raise ValueError("Unsupported file type")

class TrafficLightImporter(DataImporter):
    def import_traffic_lights(self, file_content: bytes, file_type: str, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        from app.models import TrafficLight
        if file_type == 'csv':
            return self.import_csv(file_content, TrafficLight, column_mapping)
        elif file_type == 'excel':
            return self.import_excel(file_content, TrafficLight, column_mapping)
        else:
            raise ValueError("Unsupported file type")