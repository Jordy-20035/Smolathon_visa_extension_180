from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Dict
import uuid


# Base schemas with common fields
class LocationBase(BaseModel):
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    district: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VehicleBase(BaseModel):
    plate_number: str
    type: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Fine schemas
class FineBase(BaseModel):
    vehicle_id: uuid.UUID
    location_id: uuid.UUID
    amount: float
    issued_at: datetime
    violation_code: Optional[str] = None
    status: str = "issued"
    visibility: str = "private"

class FineCreate(FineBase):
    pass

class FineUpdate(BaseModel):
    amount: Optional[float] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    violation_code: Optional[str] = None

class Fine(FineBase):
    id: uuid.UUID
    created_at: datetime
    vehicle: Optional[Vehicle] = None
    location: Optional[Location] = None
    
    model_config = ConfigDict(from_attributes=True)

# Accident schemas
class AccidentBase(BaseModel):
    location_id: uuid.UUID
    accident_type: str
    severity: Optional[str] = None
    occurred_at: datetime
    casualties: int = 0
    visibility: str = "private"

class AccidentCreate(AccidentBase):
    pass

class AccidentUpdate(BaseModel):
    accident_type: Optional[str] = None
    severity: Optional[str] = None
    casualties: Optional[int] = None
    visibility: Optional[str] = None

class Accident(AccidentBase):
    id: uuid.UUID
    created_at: datetime
    location: Optional[Location] = None
    
    model_config = ConfigDict(from_attributes=True)

# Traffic Light schemas
class TrafficLightBase(BaseModel):
    location_id: uuid.UUID
    type: Optional[str] = None
    status: str = "working"
    install_date: Optional[date] = None
    last_maintenance: Optional[date] = None

class TrafficLightCreate(TrafficLightBase):
    pass

class TrafficLightUpdate(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    last_maintenance: Optional[date] = None

class TrafficLight(TrafficLightBase):
    id: uuid.UUID
    created_at: datetime
    location: Optional[Location] = None
    
    model_config = ConfigDict(from_attributes=True)

# Response schemas for lists
class FineList(BaseModel):
    items: List[Fine]
    total: int

class AccidentList(BaseModel):
    items: List[Accident]
    total: int

class TrafficLightList(BaseModel):
    items: List[TrafficLight]
    total: int

# User schemas
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(BaseModel):
    username: str
    role: str = "guest"

class User(UserBase):
    id: uuid.UUID
    api_key: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    username: str

class LoginResponse(BaseModel):
    username: str
    api_key: str
    role: str

class ColumnMapping(BaseModel):
    plate_number: Optional[str] = None
    amount: Optional[str] = None
    issued_at: Optional[str] = None
    violation_code: Optional[str] = None
    # Add other columns you need to map
    
    model_config = ConfigDict(from_attributes=True)