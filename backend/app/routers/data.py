from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app import models, schemas, crud
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/api/v1", tags=["data"])

# Fines endpoints
@router.get("/fines/", response_model=schemas.FineList)
def read_fines(
    skip: int = 0,
    limit: int = 100,
    visibility: str = Query("public", regex="^(public|private)$"),
    vehicle_id: Optional[uuid.UUID] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get list of fines with filtering"""
    # Citizens can only see public data
    if current_user.role == "citizen":
        visibility = "public"
    
    fines = crud.crud_fine.get_multi_with_filters(
        db, 
        skip=skip, 
        limit=limit,
        visibility=visibility,
        vehicle_id=vehicle_id,
        date_from=date_from,
        date_to=date_to
    )
    
    total = crud.crud_fine.get_count(db, visibility=visibility)
    
    return {"items": fines, "total": total}

@router.get("/fines/{fine_id}", response_model=schemas.Fine)
def read_fine(
    fine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific fine by ID"""
    fine = crud.crud_fine.get_with_relations(db, id=fine_id)
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    
    # Check visibility permissions
    if fine.visibility == "private" and current_user.role == "citizen":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return fine

@router.post("/fines/", response_model=schemas.Fine, status_code=status.HTTP_201_CREATED)
def create_fine(
    fine: schemas.FineCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Create a new fine (admin only)"""
    return crud.crud_fine.create(db, obj_in=fine)

@router.put("/fines/{fine_id}", response_model=schemas.Fine)
def update_fine(
    fine_id: uuid.UUID,
    fine_update: schemas.FineUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Update a fine (admin only)"""
    fine = crud.crud_fine.get(db, id=fine_id)
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    
    return crud.crud_fine.update(db, db_obj=fine, obj_in=fine_update)

@router.delete("/fines/{fine_id}")
def delete_fine(
    fine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Delete a fine (admin only)"""
    fine = crud.crud_fine.get(db, id=fine_id)
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    
    crud.crud_fine.delete(db, id=fine_id)
    return {"message": "Fine deleted successfully"}

# Accidents endpoints
@router.get("/accidents/", response_model=schemas.AccidentList)
def read_accidents(
    skip: int = 0,
    limit: int = 100,
    visibility: str = Query("public", regex="^(public|private)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get list of accidents"""
    if current_user.role == "citizen":
        visibility = "public"
    
    accidents = crud.get_accidents_with_relations(db, skip=skip, limit=limit, visibility=visibility)
    total = db.query(models.Accident).filter(models.Accident.visibility == visibility).count()
    
    return {"items": accidents, "total": total}

@router.get("/accidents/{accident_id}", response_model=schemas.Accident)
def read_accident(
    accident_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific accident by ID"""
    accident = crud.crud_accident.get(db, id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")
    
    if accident.visibility == "private" and current_user.role == "citizen":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return accident

@router.post("/accidents/", response_model=schemas.Accident, status_code=status.HTTP_201_CREATED)
def create_accident(
    accident: schemas.AccidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    return crud.crud_accident.create(db, obj_in=accident)

# Traffic Lights endpoints
@router.get("/traffic-lights/", response_model=schemas.TrafficLightList)
def read_traffic_lights(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = Query(None, regex="^(working|outage|maintenance)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get list of traffic lights"""
    query = db.query(models.TrafficLight).join(models.Location)
    
    if status_filter:
        query = query.filter(models.TrafficLight.status == status_filter)
    
    traffic_lights = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {"items": traffic_lights, "total": total}

@router.get("/traffic-lights/{traffic_light_id}", response_model=schemas.TrafficLight)
def read_traffic_light(
    traffic_light_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific traffic light by ID"""
    traffic_light = crud.crud_traffic_light.get(db, id=traffic_light_id)
    if not traffic_light:
        raise HTTPException(status_code=404, detail="Traffic light not found")
    return traffic_light

@router.post("/traffic-lights/", response_model=schemas.TrafficLight, status_code=status.HTTP_201_CREATED)
def create_traffic_light(
    traffic_light: schemas.TrafficLightCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    return crud.crud_traffic_light.create(db, obj_in=traffic_light)

# Locations endpoints
@router.get("/locations/", response_model=List[schemas.Location])
def read_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get list of locations"""
    return crud.crud_location.get_multi(db, skip=skip, limit=limit)

@router.post("/locations/", response_model=schemas.Location, status_code=status.HTTP_201_CREATED)
def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    return crud.crud_location.create(db, obj_in=location)