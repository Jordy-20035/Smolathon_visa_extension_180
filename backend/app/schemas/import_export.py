from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional
from enum import Enum

class FileType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"

class ImportRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    file_type: FileType
    model_type: str  # "fine", "accident", "traffic_light"
    column_mapping: Dict[str, str]  # {"file_column": "db_column"}
    sheet_name: Optional[str] = None  # For Excel files

class ImportResponse(BaseModel):
    total_processed: int
    successful: int
    failed: int
    errors: List[str]

class ExportRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    format: FileType
    query: Optional[str] = None  # Custom SQL query
    model_type: Optional[str] = None  # Export entire model
    filters: Optional[Dict[str, str]] = None  # Model filters

# Predefined column mappings for common import formats
DEFAULT_COLUMN_MAPPINGS = {
    "fines": {
        "Дата нарушения": "issued_at",
        "Госномер": "plate_number", 
        "Код нарушения": "violation_code",
        "Сумма штрафа": "amount",
        "Адрес": "address",
        "Статус": "status"
    },
    "accidents": {
        "Тип ДТП": "accident_type",
        "Тяжесть": "severity", 
        "Пострадавшие": "casualties",
        "Дата и время": "occurred_at",
        "Адрес": "address"
    },
    "traffic_lights": {
        "Тип светофора": "type",
        "Статус": "status",
        "Дата установки": "install_date", 
        "Адрес": "address"
    },
    "evacuations": {
        "evacuated_at": "evacuated_at",
        "towing_vehicles_count": "towing_vehicles_count",
        "dispatches_count": "dispatches_count", 
        "evacuations_count": "evacuations_count",
        "revenue": "revenue"
    }
}