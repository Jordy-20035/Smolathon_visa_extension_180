"""
Схемы для API анализа транспортных потоков
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class DetectorBase(BaseModel):
    detector_id: str
    latitude: float
    longitude: float
    description: Optional[str] = None


class DetectorCreate(DetectorBase):
    pass


class DetectorResponse(DetectorBase):
    id: str
    
    class Config:
        from_attributes = True


class VehicleTrackReadingBase(BaseModel):
    detector_id: str  # external detector_id
    timestamp: datetime
    vehicle_identifier: str
    speed: Optional[float] = None


class VehicleTrackReadingCreate(VehicleTrackReadingBase):
    pass


class VehicleTrackReadingResponse(VehicleTrackReadingBase):
    id: str
    
    class Config:
        from_attributes = True


class VehicleTrackResponse(BaseModel):
    """Трек транспортного средства"""
    vehicle_identifier: str
    readings: List[Dict]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class JointMovementMatch(BaseModel):
    """Совпадение прохождения узла графа"""
    detector_id: str
    detector_external_id: str
    target_timestamp: str
    other_timestamp: str
    time_diff_seconds: float
    latitude: float
    longitude: float


class JointMovementResponse(BaseModel):
    """Результат анализа совместного движения"""
    vehicle_id: str
    common_nodes_count: int
    matches: List[JointMovementMatch]
    start_time: str
    end_time: str
    duration_seconds: float


class JointMovementRequest(BaseModel):
    """Запрос анализа совместного движения"""
    target_vehicle_id: str
    min_common_nodes: int = Field(default=3, ge=2, le=20)
    max_time_gap_seconds: int = Field(default=300, ge=10, le=3600)
    max_lead_seconds: int = Field(default=60, ge=5, le=300)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class JointMovementAnalysisResponse(BaseModel):
    """Полный ответ анализа совместного движения"""
    target_vehicle_id: str
    target_track: List[Dict]
    joint_movements: List[JointMovementResponse]


class RouteClusterRequest(BaseModel):
    """Запрос кластеризации маршрутов"""
    start_time: datetime
    end_time: datetime
    top_n: int = Field(default=10, ge=1, le=50)
    min_vehicles_per_route: int = Field(default=2, ge=1)


class RouteClusterResponse(BaseModel):
    """Кластер маршрута с статистикой"""
    route_signature: str
    detector_sequence: List[str]
    total_vehicles: int
    intensity_per_hour: float
    average_speed_kmh: Optional[float] = None
    average_passage_time_seconds: Optional[float] = None
    coordinates: List[Dict]
    vehicles: List[str]


class RouteClusteringResponse(BaseModel):
    """Ответ кластеризации маршрутов"""
    routes: List[RouteClusterResponse]
    time_range_hours: float
    total_vehicles_analyzed: int
