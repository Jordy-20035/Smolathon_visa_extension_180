from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Type, TypeVar, Generic, Any
from app import models, core_schemas
import uuid

# Use the actual model classes for type hinting
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=core_schemas.BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=core_schemas.BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: uuid.UUID) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> ModelType:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

# Fine-specific CRUD operations
class CRUDFine(CRUDBase[models.Fine, core_schemas.FineCreate, core_schemas.FineUpdate]):
    def get_with_relations(self, db: Session, id: uuid.UUID) -> Optional[models.Fine]:
        return db.query(self.model).\
            join(models.Vehicle).\
            join(models.Location).\
            filter(self.model.id == id).\
            first()

    def get_multi_with_filters(
        self, db: Session, *, 
        skip: int = 0, 
        limit: int = 100,
        visibility: Optional[str] = None,
        vehicle_id: Optional[uuid.UUID] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[models.Fine]:
        query = db.query(self.model).\
            join(models.Vehicle).\
            join(models.Location)
        
        if visibility:
            query = query.filter(self.model.visibility == visibility)
        if vehicle_id:
            query = query.filter(self.model.vehicle_id == vehicle_id)
        if date_from:
            query = query.filter(self.model.issued_at >= date_from)
        if date_to:
            query = query.filter(self.model.issued_at <= date_to)
            
        return query.offset(skip).limit(limit).all()

    def get_count(self, db: Session, visibility: str = "public") -> int:
        return db.query(func.count(self.model.id)).\
            filter(self.model.visibility == visibility).\
            scalar()

# Accident-specific CRUD operations
class CRUDAccident(CRUDBase[models.Accident, core_schemas.AccidentCreate, core_schemas.AccidentUpdate]):
    def get_with_relations(self, db: Session, id: uuid.UUID) -> Optional[models.Accident]:
        return db.query(self.model).\
            join(models.Location).\
            filter(self.model.id == id).\
            first()

    def get_multi_with_filters(
        self, db: Session, *, 
        skip: int = 0, 
        limit: int = 100,
        visibility: Optional[str] = None
    ) -> List[models.Accident]:
        query = db.query(self.model).join(models.Location)
        
        if visibility:
            query = query.filter(self.model.visibility == visibility)
            
        return query.offset(skip).limit(limit).all()

    def get_count(self, db: Session, visibility: str = "public") -> int:
        return db.query(func.count(self.model.id)).\
            filter(self.model.visibility == visibility).\
            scalar()

# TrafficLight-specific CRUD operations
class CRUDTrafficLight(CRUDBase[models.TrafficLight, core_schemas.TrafficLightCreate, core_schemas.TrafficLightUpdate]):
    def get_with_relations(self, db: Session, id: uuid.UUID) -> Optional[models.TrafficLight]:
        return db.query(self.model).\
            join(models.Location).\
            filter(self.model.id == id).\
            first()

    def get_multi_with_filters(
        self, db: Session, *, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[models.TrafficLight]:
        query = db.query(self.model).join(models.Location)
        
        if status:
            query = query.filter(self.model.status == status)
            
        return query.offset(skip).limit(limit).all()

# Create CRUD instances with proper type annotations
crud_fine: CRUDFine = CRUDFine(models.Fine)
crud_accident: CRUDAccident = CRUDAccident(models.Accident)
crud_traffic_light: CRUDTrafficLight = CRUDTrafficLight(models.TrafficLight)
crud_location: CRUDBase[models.Location, core_schemas.LocationCreate, Any] = CRUDBase(models.Location)
crud_vehicle: CRUDBase[models.Vehicle, core_schemas.VehicleCreate, Any] = CRUDBase(models.Vehicle)

# Helper functions for relations
def get_fines_with_relations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    visibility: str = "public"
) -> List[models.Fine]:
    return db.query(models.Fine).\
        join(models.Vehicle).\
        join(models.Location).\
        filter(models.Fine.visibility == visibility).\
        offset(skip).limit(limit).all()

def get_accidents_with_relations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    visibility: str = "public"
) -> List[models.Accident]:
    return db.query(models.Accident).\
        join(models.Location).\
        filter(models.Accident.visibility == visibility).\
        offset(skip).limit(limit).all()

def get_traffic_lights_with_relations(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.TrafficLight]:
    return db.query(models.TrafficLight).\
        join(models.Location).\
        offset(skip).limit(limit).all()