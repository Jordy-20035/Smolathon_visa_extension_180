"""
API endpoints для анализа транспортных потоков
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app import models
from app.routers.auth import require_role, get_current_user
from app.services.traffic_analysis_service import TrafficAnalysisService
from app.schemas.traffic_analysis import (
    JointMovementRequest,
    JointMovementAnalysisResponse,
    JointMovementResponse,
    RouteClusterRequest,
    RouteClusteringResponse,
    RouteClusterResponse,
    DetectorResponse,
    VehicleTrackReadingResponse,
    VehicleTrackResponse
)

router = APIRouter(prefix="/api/v1/traffic-analysis", tags=["traffic-analysis"])


def require_analytics_access(current_user: models.User = Depends(get_current_user)):
    """Allow both admin and redactor to access traffic analysis"""
    if current_user.role not in ['admin', 'redactor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access traffic analysis"
        )
    return current_user


@router.post("/joint-movement", response_model=JointMovementAnalysisResponse)
def analyze_joint_movement(
    request: JointMovementRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)
):
    """
    Анализ совместного движения для целевого ТС
    
    Находит транспортные средства, движущиеся совместно с целевым ТС
    по заданным критериям.
    """
    service = TrafficAnalysisService(db)
    
    # Получаем трек целевого ТС
    target_track = service.get_vehicle_track(
        request.target_vehicle_id,
        request.start_time,
        request.end_time
    )
    
    if not target_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No track found for vehicle {request.target_vehicle_id}"
        )
    
    # Находим совместные движения
    joint_movements_data = service.find_joint_movements(
        target_vehicle_id=request.target_vehicle_id,
        min_common_nodes=request.min_common_nodes,
        max_time_gap_seconds=request.max_time_gap_seconds,
        max_lead_seconds=request.max_lead_seconds,
        start_time=request.start_time,
        end_time=request.end_time
    )
    
    # Преобразуем в формат ответа
    joint_movements = []
    for movement in joint_movements_data:
        matches = []
        for match in movement["matches"]:
            matches.append({
                "detector_id": match["detector_id"],
                "detector_external_id": match["detector_external_id"],
                "target_timestamp": match["target_timestamp"],
                "other_timestamp": match["other_timestamp"],
                "time_diff_seconds": match["time_diff_seconds"],
                "latitude": match["latitude"],
                "longitude": match["longitude"]
            })
        
        joint_movements.append({
            "vehicle_id": movement["vehicle_id"],
            "common_nodes_count": movement["common_nodes_count"],
            "matches": matches,
            "start_time": movement["start_time"],
            "end_time": movement["end_time"],
            "duration_seconds": movement["duration_seconds"]
        })
    
    return {
        "target_vehicle_id": request.target_vehicle_id,
        "target_track": target_track,
        "joint_movements": joint_movements
    }


@router.post("/route-clustering", response_model=RouteClusteringResponse)
def cluster_routes(
    request: RouteClusterRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)
):
    """
    Кластеризация маршрутов за заданный период времени
    
    Находит N наиболее популярных маршрутов и предоставляет статистику:
    - Интенсивность (ТС/час)
    - Средняя скорость
    - Среднее время прохождения
    """
    if request.start_time >= request.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be before end_time"
        )
    
    service = TrafficAnalysisService(db)
    
    routes_data = service.cluster_routes(
        start_time=request.start_time,
        end_time=request.end_time,
        top_n=request.top_n,
        min_vehicles_per_route=request.min_vehicles_per_route
    )
    
    # Подсчитываем общее количество проанализированных ТС
    total_vehicles = set()
    for route in routes_data:
        total_vehicles.update(route["vehicles"])
    
    time_range_hours = (request.end_time - request.start_time).total_seconds() / 3600.0
    
    routes = []
    for route_data in routes_data:
        routes.append({
            "route_signature": route_data["route_signature"],
            "detector_sequence": route_data["detector_sequence"],
            "total_vehicles": route_data["total_vehicles"],
            "intensity_per_hour": route_data["intensity_per_hour"],
            "average_speed_kmh": route_data["average_speed_kmh"],
            "average_passage_time_seconds": route_data["average_passage_time_seconds"],
            "coordinates": route_data["coordinates"],
            "vehicles": route_data["vehicles"]
        })
    
    return {
        "routes": routes,
        "time_range_hours": round(time_range_hours, 2),
        "total_vehicles_analyzed": len(total_vehicles)
    }


@router.get("/vehicle-track/{vehicle_identifier}", response_model=VehicleTrackResponse)
def get_vehicle_track(
    vehicle_identifier: str,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)
):
    """
    Получение трека транспортного средства
    """
    service = TrafficAnalysisService(db)
    
    track = service.get_vehicle_track(
        vehicle_identifier,
        start_time,
        end_time
    )
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No track found for vehicle {vehicle_identifier}"
        )
    
    return {
        "vehicle_identifier": vehicle_identifier,
        "readings": track,
        "start_time": datetime.fromisoformat(track[0]["timestamp"].replace('Z', '+00:00')) if track else None,
        "end_time": datetime.fromisoformat(track[-1]["timestamp"].replace('Z', '+00:00')) if track else None
    }


@router.post("/build-graph")
def build_road_graph(
    max_distance_meters: float = Query(default=1000.0, ge=10.0, le=10000.0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """
    Построение графа дорожной сети из расположений детекторов
    
    Создает ребра между детекторами, находящимися в пределах max_distance_meters друг от друга
    """
    service = TrafficAnalysisService(db)
    
    result = service.build_road_graph(max_distance_meters)
    
    return {
        "status": "success",
        "detectors_count": result["detectors_count"],
        "edges_created": result["edges_created"],
        "max_distance_meters": max_distance_meters
    }


@router.get("/detectors", response_model=List[DetectorResponse])
def get_detectors(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_analytics_access)
):
    """Получение списка всех детекторов"""
    detectors = db.query(models.Detector).all()
    
    return [
        {
            "id": str(det.id),
            "detector_id": det.detector_id,
            "latitude": float(det.latitude),
            "longitude": float(det.longitude),
            "description": det.description
        }
        for det in detectors
    ]
