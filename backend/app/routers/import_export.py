import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from typing import Optional
from fastapi import Form
from app.database import get_db
from app import models
from app.routers.auth import require_role
from app.utils.importer import FineImporter, AccidentImporter, TrafficLightImporter
from app.utils.exporter import PredefinedExports, DataExporter
from app.schemas.import_export import ImportRequest, ImportResponse, FileType, DEFAULT_COLUMN_MAPPINGS

router = APIRouter(prefix="/api/v1", tags=["import-export"])

@router.post("/import/{model_type}", response_model=ImportResponse)
async def import_data(
    model_type: str,
    file: UploadFile = File(...),
    column_mapping: Optional[str] = Form(None),
    sheet_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Import data from CSV or Excel file"""
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_type = file.filename.split('.')[-1].lower()
    if file_type not in ['csv', 'xlsx', 'xls']:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Read file content
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # Determine importer based on model type
    if model_type == "fines":
        importer = FineImporter(db)
        import_func = importer.import_fines
        default_mapping = DEFAULT_COLUMN_MAPPINGS["fines"]
    elif model_type == "accidents":
        importer = AccidentImporter(db)
        import_func = importer.import_accidents
        default_mapping = DEFAULT_COLUMN_MAPPINGS["accidents"]
    elif model_type == "traffic_lights":
        importer = TrafficLightImporter(db)
        import_func = importer.import_traffic_lights
        default_mapping = DEFAULT_COLUMN_MAPPINGS["traffic_lights"]
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_type}")
    
    # FIX: Parse column mapping properly
    if column_mapping:
        try:
            # Parse the JSON string into a dictionary
            final_mapping = json.loads(column_mapping)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid column mapping JSON: {str(e)}")
    else:
        final_mapping = default_mapping
    
    try:
        # Perform import
        result = import_func(
            file_content=content,
            file_type='excel' if file_type in ['xlsx', 'xls'] else 'csv',
            column_mapping=final_mapping  # Now this is a dict, not a string
        )
        
        return ImportResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export/{export_type}")
def export_data(
    export_type: str,
    format: FileType = FileType.CSV,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Export data in CSV or Excel format"""
    
    exporter = PredefinedExports(db)
    
    try:
        if export_type == "public_fines":
            data = exporter.export_public_fines(format.value)
            filename = "public_fines"
        elif export_type == "accidents":
            data = exporter.export_accidents_stats(format.value)
            filename = "accidents_statistics"
        elif export_type == "traffic_lights":
            data = exporter.export_traffic_lights(format.value)
            filename = "traffic_lights"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export type: {export_type}")
        
        # Determine content type and file extension
        if format == FileType.CSV:
            media_type = "text/csv"
            extension = "csv"
        else:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            extension = "xlsx"
        
        return StreamingResponse(
            io.BytesIO(data),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}.{extension}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/export/custom")
def export_custom_data(
    query: str,
    format: FileType = FileType.CSV,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Export custom SQL query results"""
    
    exporter = DataExporter(db)
    
    try:
        if format == FileType.CSV:
            data = exporter.export_to_csv(query)
            media_type = "text/csv"
            extension = "csv"
        else:
            data = exporter.export_to_excel(query)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            extension = "xlsx"
        
        return StreamingResponse(
            io.BytesIO(data),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=custom_export.{extension}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")

# Additional endpoint to get available column mappings
@router.get("/import/mappings/{model_type}")
def get_column_mappings(
    model_type: str,
    current_user: models.User = Depends(require_role("admin"))
):
    """Get available column mappings for import"""
    
    if model_type in DEFAULT_COLUMN_MAPPINGS:
        return {
            "model_type": model_type,
            "available_mappings": DEFAULT_COLUMN_MAPPINGS[model_type],
            "description": "Map your file columns to database fields"
        }
    else:
        raise HTTPException(status_code=404, detail=f"No mappings found for {model_type}")