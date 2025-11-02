from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, Text, Boolean, Float, ForeignKey, Index
from datetime import datetime  
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    api_key = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), nullable=False)  # citizen, editor, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    content_pages = relationship("ContentPage", back_populates="author")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(200), nullable=False)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    district = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    evacuations = relationship("Evacuation", back_populates="location")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String(20), nullable=False)
    type = Column(String(50))  # car, truck, motorcycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Fine(Base):
    __tablename__ = "fines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    amount = Column(Numeric(10, 2))
    issued_at = Column(DateTime(timezone=True), nullable=False)
    violation_code = Column(String(20))
    status = Column(String(20), default="issued")  # issued, paid, contested
    visibility = Column(String(20), nullable=False, default="private")  # public, private
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_fines_issued_at', 'issued_at'),
        Index('idx_fines_vehicle_id', 'vehicle_id'),
        Index('idx_fines_visibility', 'visibility'),
    )

class Accident(Base):
    __tablename__ = "accidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    accident_type = Column(String(100), nullable=False)
    severity = Column(String(20))  # minor, injury, fatal
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    casualties = Column(Integer, default=0)
    visibility = Column(String(20), nullable=False, default="private")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_accidents_occurred_at', 'occurred_at'),
        Index('idx_accidents_visibility', 'visibility'),
    )

    location = relationship("Location", backref="accidents")


class TrafficLight(Base):
    __tablename__ = "traffic_lights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    type = Column(String(50))  # pedestrian, vehicular
    status = Column(String(20), nullable=False, default="working")  # working, outage, maintenance
    install_date = Column(Date)
    last_maintenance = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_traffic_lights_status', 'status'),
    )

    location = relationship("Location", backref="traffic_lights")


class ContentPage(Base):
    __tablename__ = "content_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    is_published = Column(Boolean, default=False)
    page_type = Column(String(20), nullable=False)  # news, service, about, statistics
    
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Changed to func.now()
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # Fixed
    
    # Relationship
    author = relationship("User", back_populates="content_pages")


class Evacuation(Base):
    __tablename__ = "evacuations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey('locations.id'), nullable=False)
    evacuated_at = Column(DateTime, nullable=False)
    towing_vehicles_count = Column(Integer, default=0)
    dispatches_count = Column(Integer, default=0)
    evacuations_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    visibility = Column(String, default="private")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    location = relationship("Location", back_populates="evacuations")


class Detector(Base):
    """Детектор транспортных средств (датчик) на узле графа дорожной сети"""
    __tablename__ = "detectors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detector_id = Column(String(100), unique=True, nullable=False)  # ID_детектора из исходных данных
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    description = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    location = relationship("Location", backref="detectors")
    track_readings = relationship("VehicleTrackReading", back_populates="detector")
    
    __table_args__ = (
        Index('idx_detector_id', 'detector_id'),
        Index('idx_detector_coords', 'latitude', 'longitude'),
    )


class VehicleTrackReading(Base):
    """Запись прохождения ТС через детектор"""
    __tablename__ = "vehicle_track_readings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detector_id = Column(UUID(as_uuid=True), ForeignKey("detectors.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Временная_метка
    vehicle_identifier = Column(String(100), nullable=False)  # Идентификатор_ТС
    speed = Column(Numeric(10, 2))  # Скорость_прохождения (опционально)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    detector = relationship("Detector", back_populates="track_readings")
    
    __table_args__ = (
        Index('idx_track_timestamp', 'timestamp'),
        Index('idx_track_vehicle', 'vehicle_identifier'),
        Index('idx_track_detector', 'detector_id'),
        Index('idx_track_vehicle_timestamp', 'vehicle_identifier', 'timestamp'),
    )


class RoadNetworkEdge(Base):
    """Ребро графа дорожной сети - участок дороги между двумя детекторами"""
    __tablename__ = "road_network_edges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_detector_id = Column(UUID(as_uuid=True), ForeignKey("detectors.id"), nullable=False)
    to_detector_id = Column(UUID(as_uuid=True), ForeignKey("detectors.id"), nullable=False)
    distance_meters = Column(Numeric(10, 2))  # Расстояние в метрах
    average_speed_kmh = Column(Numeric(10, 2))  # Средняя скорость на участке
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    from_detector = relationship("Detector", foreign_keys=[from_detector_id], backref="outgoing_edges")
    to_detector = relationship("Detector", foreign_keys=[to_detector_id], backref="incoming_edges")
    
    __table_args__ = (
        Index('idx_edge_from_to', 'from_detector_id', 'to_detector_id'),
    )