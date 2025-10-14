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
from app.utils.importer import FineImporter, AccidentImporter, TrafficLightImporter, EvacuationImporter
from app.utils.exporter import PredefinedExports, DataExporter
from app.schemas.import_export import ImportRequest, ImportResponse, FileType, DEFAULT_COLUMN_MAPPINGS
import pandas as pd
import uuid
from datetime import datetime


router = APIRouter(prefix="/api/v1", tags=["import-export"])


@router.post("/import/{model_type}", response_model=ImportResponse)
async def import_data(
    model_type: str,
    file: UploadFile = File(...),
    column_mapping: Optional[str] = Form(None),   # <- accept as string
    sheet_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    # --- parse mapping ---
    if column_mapping:
        try:
            mapping = json.loads(column_mapping)
            if not isinstance(mapping, dict):
                raise ValueError("column_mapping must be a JSON object (dict)")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in column_mapping: {e}")
    else:
        # fallback to default mapping or error
        if model_type not in DEFAULT_COLUMN_MAPPINGS:
            raise HTTPException(status_code=400, detail="No column_mapping provided and no default mapping found")
        mapping = DEFAULT_COLUMN_MAPPINGS[model_type]

    # --- check file ---
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    ext = file.filename.split(".")[-1].lower()
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    # --- select importer class (you already have these) ---
    if model_type == "fines":
        importer = FineImporter(db)
        import_func = importer.import_fines
    elif model_type == "accidents":
        importer = AccidentImporter(db)
        import_func = importer.import_accidents
    elif model_type == "traffic_lights":
        importer = TrafficLightImporter(db)
        import_func = importer.import_traffic_lights
    elif model_type == "evacuations":
        importer = EvacuationImporter(db)
        import_func = importer.import_evacuations
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_type}")

    # --- execute import (expecting dict result matching ImportResponse) ---
    try:
        result = import_func(
            file_content=content,
            file_type='excel' if ext in ('xlsx','xls') else 'csv',
            column_mapping=mapping,
            sheet_name=sheet_name
        )
        return ImportResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


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
        if export_type == "fines":
            data = exporter.export_fines(format.value)
            filename = "fines"
        elif export_type == "accidents":
            data = exporter.export_accidents(format.value)
            filename = "accidents"
        elif export_type == "traffic_lights":
            data = exporter.export_traffic_lights(format.value)
            filename = "traffic_lights"
        elif export_type == "evacuations":
            data = exporter.export_evacuations(format.value)
            filename = "evacuations"
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