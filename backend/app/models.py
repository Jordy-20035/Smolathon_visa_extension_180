from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, Text, Boolean, ForeignKey, Index
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
    role = Column(String(20), nullable=False)  # citizen, redactor, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(200), nullable=False)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    district = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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

class ContentPage(Base):
    __tablename__ = "content_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    is_published = Column(Boolean, default=False)
    page_type = Column(String(20), nullable=False)  # news, service, about, statistics
    
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    author = relationship("User", back_populates="content_pages")