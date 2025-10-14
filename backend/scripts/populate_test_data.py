import sys
import os
import uuid
from datetime import datetime, date, timedelta

# parent directory to Python path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Location, Vehicle, Fine, Accident, TrafficLight, Evacuation
from app.config import settings

def populate_test_data():
    # Create database connection directly
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Populating database with test data...")
        
        # Create test user if not exists
        test_user = db.query(User).filter(User.username == "test_admin").first()
        if not test_user:
            test_user = User(
                id=uuid.uuid4(),
                username="test_admin",
                api_key="test_api_key_123",
                role="admin"
            )
            db.add(test_user)
            db.commit()
            print("Created test user")
        
        # Create test locations
        locations_data = [
            {"address": "ул. Ленина, 15", "district": "Центральный"},
            {"address": "пр. Гагарина, 42", "district": "Западный"},
            {"address": "ул. Кирова, 88", "district": "Восточный"},
            {"address": "ул. Советская, 25", "district": "Северный"},
        ]
        
        locations = []
        for loc_data in locations_data:
            location = db.query(Location).filter(Location.address == loc_data["address"]).first()
            if not location:
                location = Location(
                    id=uuid.uuid4(),
                    address=loc_data["address"],
                    district=loc_data["district"]
                )
                db.add(location)
                locations.append(location)
        
        db.commit()
        print(f"Created {len(locations)} locations")
        
        # Create test vehicles
        vehicles_data = [
            {"plate_number": "А123ВС77", "type": "car"},
            {"plate_number": "В456ОР78", "type": "car"},
            {"plate_number": "С789ТУ79", "type": "truck"},
        ]
        
        vehicles = []
        for vehicle_data in vehicles_data:
            vehicle = db.query(Vehicle).filter(Vehicle.plate_number == vehicle_data["plate_number"]).first()
            if not vehicle:
                vehicle = Vehicle(
                    id=uuid.uuid4(),
                    plate_number=vehicle_data["plate_number"],
                    type=vehicle_data["type"]
                )
                db.add(vehicle)
                vehicles.append(vehicle)
        
        db.commit()
        print(f"Created {len(vehicles)} vehicles")
        
        # Create test fines (mix of public and private)
        fines_data = []
        for i in range(10):
            fines_data.append({
                "vehicle_id": vehicles[i % len(vehicles)].id,
                "location_id": locations[i % len(locations)].id,
                "amount": 1500.00 + (i * 500),
                "issued_at": datetime.now() - timedelta(days=i),
                "violation_code": f"01.{i:02d}",
                "status": "issued",
                "visibility": "public" if i % 2 == 0 else "private"
            })
        
        for fine_data in fines_data:
            fine = Fine(**fine_data)
            db.add(fine)
        
        db.commit()
        print(f"Created {len(fines_data)} fines")
        
        # Create test accidents
        accidents_data = []
        for i in range(8):
            accidents_data.append({
                "location_id": locations[i % len(locations)].id,
                "accident_type": ["Столкновение", "Наезд", "Опрокидывание"][i % 3],
                "severity": ["minor", "injury", "fatal"][i % 3],
                "occurred_at": datetime.now() - timedelta(days=i * 2),
                "casualties": i % 4,
                "visibility": "public" if i < 6 else "private"
            })
        
        for accident_data in accidents_data:
            accident = Accident(**accident_data)
            db.add(accident)
        
        db.commit()
        print(f"Created {len(accidents_data)} accidents")
        
        # Create test traffic lights
        traffic_lights_data = []
        for i in range(6):
            traffic_lights_data.append({
                "location_id": locations[i % len(locations)].id,
                "type": ["pedestrian", "vehicular"][i % 2],
                "status": ["working", "maintenance", "outage"][i % 3],
                "install_date": date(2023, 1, 1) + timedelta(days=i * 30),
                "last_maintenance": date(2024, 1, 1) + timedelta(days=i * 60)
            })
        
        for tl_data in traffic_lights_data:
            traffic_light = TrafficLight(**tl_data)
            db.add(traffic_light)
        
        db.commit()
        print(f"Created {len(traffic_lights_data)} traffic lights")
        
        # Create test evacuations
        evacuations_data = []
        for i in range(12):
            evacuations_data.append({
                "location_id": locations[i % len(locations)].id,
                "evacuated_at": datetime.now() - timedelta(days=i),
                "towing_vehicles_count": 2 + (i % 3),
                "dispatches_count": 5 + (i % 5),
                "evacuations_count": 3 + (i % 4),
                "revenue": 5000.00 + (i * 1000),
                "visibility": "public" if i % 3 == 0 else "private"
            })
        
        for evacuation_data in evacuations_data:
            evacuation = Evacuation(**evacuation_data)
            db.add(evacuation)
        
        db.commit()
        print(f"Created {len(evacuations_data)} evacuations")
        
        print("✅ Database populated successfully!")
        print("\n📊 Test Data Summary:")
        print(f"   - Locations: {len(locations)}")
        print(f"   - Vehicles: {len(vehicles)}")
        print(f"   - Fines: {len(fines_data)} (mix of public/private)")
        print(f"   - Accidents: {len(accidents_data)} (mix of public/private)")
        print(f"   - Traffic Lights: {len(traffic_lights_data)}")
        print(f"   - Evacuations: {len(evacuations_data)} (mix of public/private)")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        import traceback
        print(traceback.format_exc())
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_test_data()