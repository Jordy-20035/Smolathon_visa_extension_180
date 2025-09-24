#!/usr/bin/env python3
"""
Secure database initialization script
"""
import os
import uuid
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    try:
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Import models after successful connection
        from app.database import Base
        from app.models import User, Location
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully")
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if users already exist
            existing_users = db.query(User).count()
            if existing_users > 0:
                logger.info("✅ Database already contains data, skipping initialization")
                return True
            
            # Create default users with secure API keys
            users = [
                User(
                    id=uuid.uuid4(),
                    username="admin",
                    api_key=str(uuid.uuid4()),  # Secure random API key
                    role="admin"
                ),
                User(
                    id=uuid.uuid4(),
                    username="editor", 
                    api_key=str(uuid.uuid4()),
                    role="redactor"
                ),
                User(
                    id=uuid.uuid4(),
                    username="citizen",
                    api_key=str(uuid.uuid4()),
                    role="citizen"
                )
            ]
            
            for user in users:
                db.merge(user)
            
            # Create sample locations
            locations = [
                Location(
                    id=uuid.uuid4(),
                    address="ул. Ленина, 1, Смоленск",
                    latitude=54.7818,
                    longitude=32.0401,
                    district="Центральный"
                )
            ]
            
            for location in locations:
                db.merge(location)
            
            db.commit()
            logger.info("✅ Database initialized successfully!")
            
            # Display created users with their API keys
            created_users = db.query(User).all()
            logger.info("👤 Default users created:")
            for user in created_users:
                logger.info(f"   - {user.username} (api_key: {user.api_key})")
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"❌ Database error: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    init_database()