"""
Сервис анализа транспортных потоков для ЦОДД
Реализует задачи:
1. Анализ совместного движения (совместное движение)
2. Кластеризация маршрутов и анализ загруженности
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, distinct
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import math
from app import models


class TrafficAnalysisService:
    """Сервис для анализа транспортных потоков"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def build_road_graph(self, max_distance_meters: float = 1000.0) -> Dict:
        """
        Построение графа дорожной сети из расположений детекторов
        Создает ребра между детекторами, если они находятся близко друг к другу
        """
        detectors = self.db.query(models.Detector).all()
        
        # Вычисляем расстояние между всеми парами детекторов
        edges = []
        detector_coords = {}
        
        for det in detectors:
            detector_coords[det.id] = (float(det.latitude), float(det.longitude))
        
        for i, det1 in enumerate(detectors):
            for det2 in detectors[i+1:]:
                lat1, lon1 = detector_coords[det1.id]
                lat2, lon2 = detector_coords[det2.id]
                
                distance = self._haversine_distance(lat1, lon1, lat2, lon2)
                
                if distance <= max_distance_meters:
                    # Проверяем, существует ли уже такое ребро
                    existing = self.db.query(models.RoadNetworkEdge).filter(
                        and_(
                            models.RoadNetworkEdge.from_detector_id == det1.id,
                            models.RoadNetworkEdge.to_detector_id == det2.id
                        )
                    ).first()
                    
                    if not existing:
                        reverse_existing = self.db.query(models.RoadNetworkEdge).filter(
                            and_(
                                models.RoadNetworkEdge.from_detector_id == det2.id,
                                models.RoadNetworkEdge.to_detector_id == det1.id
                            )
                        ).first()
                        
                        if not reverse_existing:
                            edge = models.RoadNetworkEdge(
                                from_detector_id=det1.id,
                                to_detector_id=det2.id,
                                distance_meters=distance
                            )
                            edges.append(edge)
        
        if edges:
            self.db.add_all(edges)
            self.db.commit()
        
        return {
            "detectors_count": len(detectors),
            "edges_created": len(edges)
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Вычисление расстояния между двумя точками на Земле (в метрах)"""
        R = 6371000  # Радиус Земли в метрах
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_vehicle_track(self, vehicle_identifier: str, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[Dict]:
        """
        Получение трека транспортного средства (последовательности прохождений детекторов)
        """
        query = self.db.query(models.VehicleTrackReading).filter(
            models.VehicleTrackReading.vehicle_identifier == vehicle_identifier
        )
        
        if start_time:
            query = query.filter(models.VehicleTrackReading.timestamp >= start_time)
        if end_time:
            query = query.filter(models.VehicleTrackReading.timestamp <= end_time)
        
        readings = query.order_by(models.VehicleTrackReading.timestamp).all()
        
        track = []
        for reading in readings:
            track.append({
                "detector_id": str(reading.detector.id),
                "detector_external_id": reading.detector.detector_id,
                "latitude": float(reading.detector.latitude),
                "longitude": float(reading.detector.longitude),
                "timestamp": reading.timestamp.isoformat(),
                "speed": float(reading.speed) if reading.speed else None
            })
        
        return track
    
    def find_joint_movements(self, target_vehicle_id: str,
                           min_common_nodes: int = 3,
                           max_time_gap_seconds: int = 300,
                           max_lead_seconds: int = 60,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[Dict]:
        """
        Находит транспортные средства, движущиеся совместно с целевым ТС
        
        Критерии совместного движения:
        1. Минимальное количество последовательно совпадающих узлов графа (K узлов)
        2. Пространственно-временная близость прохождения узлов (не более max_time_gap_seconds)
        3. Отсутствие значительного опережения (не более max_lead_seconds разницы)
        
        Args:
            target_vehicle_id: Идентификатор целевого ТС
            min_common_nodes: Минимальное количество совпадающих узлов (K)
            max_time_gap_seconds: Максимальный временной разрыв между прохождениями одного узла
            max_lead_seconds: Максимальное допустимое опережение одним ТС другого
            start_time: Начало временного диапазона
            end_time: Конец временного диапазона
        """
        # Получаем трек целевого ТС
        target_track = self.get_vehicle_track(target_vehicle_id, start_time, end_time)
        
        if len(target_track) < min_common_nodes:
            return []
        
        # Получаем все треки других ТС в том же временном диапазоне
        if start_time and end_time:
            all_readings = self.db.query(models.VehicleTrackReading).filter(
                and_(
                    models.VehicleTrackReading.vehicle_identifier != target_vehicle_id,
                    models.VehicleTrackReading.timestamp >= start_time,
                    models.VehicleTrackReading.timestamp <= end_time
                )
            ).all()
        else:
            # Используем временной диапазон целевого трека
            if target_track:
                min_time = datetime.fromisoformat(target_track[0]["timestamp"].replace('Z', '+00:00'))
                max_time = datetime.fromisoformat(target_track[-1]["timestamp"].replace('Z', '+00:00'))
                all_readings = self.db.query(models.VehicleTrackReading).filter(
                    and_(
                        models.VehicleTrackReading.vehicle_identifier != target_vehicle_id,
                        models.VehicleTrackReading.timestamp >= min_time - timedelta(seconds=max_time_gap_seconds),
                        models.VehicleTrackReading.timestamp <= max_time + timedelta(seconds=max_time_gap_seconds)
                    )
            ).all()
            else:
                return []
        
        # Группируем чтения по идентификаторам ТС
        vehicle_tracks = defaultdict(list)
        for reading in all_readings:
            vehicle_tracks[reading.vehicle_identifier].append({
                "detector_id": str(reading.detector.id),
                "detector_external_id": reading.detector.detector_id,
                "timestamp": reading.timestamp,
                "speed": float(reading.speed) if reading.speed else None,
                "latitude": float(reading.detector.latitude),
                "longitude": float(reading.detector.longitude)
            })
        
        # Сортируем треки каждого ТС по времени
        for vehicle_id in vehicle_tracks:
            vehicle_tracks[vehicle_id].sort(key=lambda x: x["timestamp"])
        
        joint_movements = []
        
        # Для каждого потенциального ТС проверяем критерии совместного движения
        for vehicle_id, other_track in vehicle_tracks.items():
            matches = []
            target_idx = 0
            
            for other_reading in other_track:
                # Ищем совпадение с целевым треком
                while target_idx < len(target_track):
                    target_reading = target_track[target_idx]
                    
                    # Проверяем совпадение детектора
                    if target_reading["detector_id"] == other_reading["detector_id"]:
                        time_diff = abs((other_reading["timestamp"] - 
                                        datetime.fromisoformat(target_reading["timestamp"].replace('Z', '+00:00'))).total_seconds())
                        
                        if time_diff <= max_time_gap_seconds:
                            matches.append({
                                "detector_id": target_reading["detector_id"],
                                "detector_external_id": target_reading["detector_external_id"],
                                "target_timestamp": target_reading["timestamp"],
                                "other_timestamp": other_reading["timestamp"].isoformat(),
                                "time_diff_seconds": time_diff,
                                "latitude": target_reading["latitude"],
                                "longitude": target_reading["longitude"]
                            })
                        
                        target_idx += 1
                        break
                    
                    # Проверяем, не слишком ли далеко мы ушли по времени
                    target_time = datetime.fromisoformat(target_reading["timestamp"].replace('Z', '+00:00'))
                    if other_reading["timestamp"] > target_time + timedelta(seconds=max_time_gap_seconds):
                        break
                    
                    target_idx += 1
                
                if target_idx >= len(target_track):
                    break
            
            # Проверяем, достаточно ли совпадений и нет ли значительного опережения
            if len(matches) >= min_common_nodes:
                # Проверяем критерий опережения
                time_leads = []
                for match in matches:
                    target_time = datetime.fromisoformat(match["target_timestamp"].replace('Z', '+00:00'))
                    other_time = datetime.fromisoformat(match["other_timestamp"].replace('Z', '+00:00'))
                    lead = (other_time - target_time).total_seconds()
                    time_leads.append(lead)
                
                max_lead = max(time_leads) if time_leads else 0
                min_lead = min(time_leads) if time_leads else 0
                
                # Если один ТС постоянно опережает другой более чем на max_lead_seconds, это не совместное движение
                if abs(max_lead) <= max_lead_seconds or abs(min_lead) <= max_lead_seconds:
                    # Проверяем, что совпадения идут последовательно (не разрозненно)
                    consecutive_matches = self._check_consecutive_matches(matches, target_track)
                    
                    if consecutive_matches:
                        joint_movements.append({
                            "vehicle_id": vehicle_id,
                            "common_nodes_count": len(matches),
                            "matches": matches,
                            "start_time": matches[0]["target_timestamp"],
                            "end_time": matches[-1]["target_timestamp"],
                            "duration_seconds": (
                                datetime.fromisoformat(matches[-1]["target_timestamp"].replace('Z', '+00:00')) -
                                datetime.fromisoformat(matches[0]["target_timestamp"].replace('Z', '+00:00'))
                            ).total_seconds() if len(matches) > 1 else 0
                        })
        
        return joint_movements
    
    def _check_consecutive_matches(self, matches: List[Dict], target_track: List[Dict]) -> bool:
        """Проверяет, что совпадения идут последовательно в треке"""
        if len(matches) < 2:
            return True
        
        # Создаем словарь позиций детекторов в целевом треке
        detector_positions = {}
        for idx, reading in enumerate(target_track):
            detector_positions[reading["detector_id"]] = idx
        
        # Проверяем, что совпадающие детекторы идут последовательно (или почти последовательно)
        match_positions = [detector_positions[m["detector_id"]] for m in matches]
        match_positions.sort()
        
        # Разрешаем небольшие пропуски (не более 2 узлов между совпадениями)
        for i in range(len(match_positions) - 1):
            gap = match_positions[i + 1] - match_positions[i]
            if gap > 3:  # Более 3 узлов пропуска - не считается последовательным
                return False
        
        return True
    
    def cluster_routes(self, start_time: datetime, end_time: datetime, 
                      top_n: int = 10, min_vehicles_per_route: int = 2) -> List[Dict]:
        """
        Кластеризация маршрутов за заданный период времени
        
        Находит N наиболее популярных маршрутов (кластеров треков)
        и предоставляет статистику по каждому маршруту
        
        Args:
            start_time: Начало периода анализа
            end_time: Конец периода анализа
            top_n: Количество топовых маршрутов для возврата
            min_vehicles_per_route: Минимальное количество ТС для формирования маршрута
        """
        # Получаем все чтения в указанном периоде
        readings = self.db.query(models.VehicleTrackReading).filter(
            and_(
                models.VehicleTrackReading.timestamp >= start_time,
                models.VehicleTrackReading.timestamp <= end_time
            )
        ).order_by(models.VehicleTrackReading.vehicle_identifier, 
                  models.VehicleTrackReading.timestamp).all()
        
        # Группируем чтения по ТС и строим треки
        vehicle_tracks = defaultdict(list)
        for reading in readings:
            vehicle_tracks[reading.vehicle_identifier].append({
                "detector_id": str(reading.detector.id),
                "detector_external_id": reading.detector.detector_id,
                "timestamp": reading.timestamp,
                "speed": float(reading.speed) if reading.speed else None,
                "latitude": float(reading.detector.latitude),
                "longitude": float(reading.detector.longitude)
            })
        
        # Сортируем каждую траекторию по времени
        for vehicle_id in vehicle_tracks:
            vehicle_tracks[vehicle_id].sort(key=lambda x: x["timestamp"])
        
        # Преобразуем треки в маршруты (последовательности детекторов)
        routes = defaultdict(list)  # route_signature -> list of vehicle_ids
        
        for vehicle_id, track in vehicle_tracks.items():
            if len(track) < 2:  # Маршрут должен содержать минимум 2 узла
                continue
            
            # Создаем сигнатуру маршрута (последовательность ID детекторов)
            route_signature = "->".join([r["detector_external_id"] for r in track])
            routes[route_signature].append({
                "vehicle_id": vehicle_id,
                "track": track,
                "start_time": track[0]["timestamp"],
                "end_time": track[-1]["timestamp"]
            })
        
        # Фильтруем маршруты по минимальному количеству ТС
        filtered_routes = {
            sig: vehicles for sig, vehicles in routes.items() 
            if len(vehicles) >= min_vehicles_per_route
        }
        
        # Вычисляем статистику для каждого маршрута
        route_stats = []
        time_range_hours = (end_time - start_time).total_seconds() / 3600.0
        
        for route_signature, vehicles in filtered_routes.items():
            # Парсим сигнатуру маршрута для получения последовательности детекторов
            detector_ids = route_signature.split("->")
            
            # Вычисляем статистику
            total_vehicles = len(vehicles)
            intensity = total_vehicles / time_range_hours if time_range_hours > 0 else 0
            
            # Средняя скорость (если доступна)
            speeds = []
            for vehicle_data in vehicles:
                for reading in vehicle_data["track"]:
                    if reading["speed"]:
                        speeds.append(reading["speed"])
            
            avg_speed = sum(speeds) / len(speeds) if speeds else None
            
            # Среднее время прохождения маршрута
            passage_times = []
            for vehicle_data in vehicles:
                if vehicle_data["track"]:
                    start = vehicle_data["start_time"]
                    end = vehicle_data["end_time"]
                    passage_time = (end - start).total_seconds()
                    passage_times.append(passage_time)
            
            avg_passage_time = sum(passage_times) / len(passage_times) if passage_times else None
            
            # Получаем координаты детекторов для визуализации
            route_coordinates = []
            for vehicle_data in vehicles:
                if vehicle_data["track"]:
                    for reading in vehicle_data["track"]:
                        route_coordinates.append({
                            "latitude": reading["latitude"],
                            "longitude": reading["longitude"],
                            "detector_id": reading["detector_external_id"]
                        })
                    break  # Берем координаты из первого трека
            
            route_stats.append({
                "route_signature": route_signature,
                "detector_sequence": detector_ids,
                "total_vehicles": total_vehicles,
                "intensity_per_hour": round(intensity, 2),
                "average_speed_kmh": round(avg_speed, 2) if avg_speed else None,
                "average_passage_time_seconds": round(avg_passage_time, 2) if avg_passage_time else None,
                "coordinates": route_coordinates,
                "vehicles": [v["vehicle_id"] for v in vehicles]
            })
        
        # Сортируем по интенсивности и возвращаем топ-N
        route_stats.sort(key=lambda x: x["intensity_per_hour"], reverse=True)
        
        return route_stats[:top_n]
