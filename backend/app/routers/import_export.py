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
    

# Simple import for evacuation data
@router.post("/evacuations")
async def import_evacuations(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import evacuation data from Excel file"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")
    
    try:
        # Read Excel file
        df = pd.read_excel(await file.read())
        
        # Map Russian column names to English
        column_mapping = {
            'Дата': 'evacuated_at',
            'Количество эвакуаторов на линии': 'towing_vehicles_count', 
            'Количество выездов': 'dispatches_count',
            'Количество эвакуаций': 'evacuations_count',
            'Сумма поступлений по штрафстоянке': 'revenue'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Filter out header rows and empty data
        df = df[df['evacuated_at'].notna()]
        df = df[df['evacuated_at'] != 'Дата']  # Remove header row
        
        # Convert date column
        df['evacuated_at'] = pd.to_datetime(df['evacuated_at'])
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Create a default location or use an existing one
                # For simplicity, we'll create a generic location
                location = models.Location(
                    address=f"Эвакуация {row['evacuated_at'].strftime('%Y-%m-%d')}",
                    district="Смоленск"
                )
                db.add(location)
                db.flush()  # Get the location ID
                
                # Create evacuation record
                evacuation = models.Evacuation(
                    location_id=location.id,
                    evacuated_at=row['evacuated_at'],
                    towing_vehicles_count=int(row['towing_vehicles_count']),
                    dispatches_count=int(row['dispatches_count']),
                    evacuations_count=int(row['evacuations_count']),
                    revenue=float(row['revenue'])
                )
                
                db.add(evacuation)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index+1}: {str(e)}")
        
        db.commit()
        
        return {
            "message": f"Successfully imported {imported_count} records",
            "errors": errors,
            "total_imported": imported_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

# Export evacuation data
@router.get("/evacuations/export")
async def export_evacuations(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Export evacuation data to Excel"""
    try:
        # Build query
        query = db.query(models.Evacuation)
        
        if start_date:
            query = query.filter(models.Evacuation.evacuated_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(models.Evacuation.evacuated_at <= datetime.fromisoformat(end_date))
        
        evacuations = query.all()
        
        # Prepare data for Excel
        data = []
        for evac in evacuations:
            data.append({
                'Дата': evac.evacuated_at,
                'Количество эвакуаторов на линии': evac.towing_vehicles_count,
                'Количество выездов': evac.dispatches_count,
                'Количество эвакуаций': evac.evacuations_count,
                'Сумма поступлений по штрафстоянке': evac.revenue
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Эвакуации', index=False)
        
        output.seek(0)
        
        # Return as downloadable file
        filename = f"evacuations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Template download
@router.get("/evacuations/template")
async def download_template():
    """Download import template"""
    template_data = {
        'Дата': ['2024-01-01 00:00:00', '2024-01-02 00:00:00'],
        'Количество эвакуаторов на линии': [1, 2],
        'Количество выездов': [3, 5], 
        'Количество эвакуаций': [2, 4],
        'Сумма поступлений по штрафстоянке': [10000, 20000]
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Шаблон', index=False)
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=import_template.xlsx"}
    )