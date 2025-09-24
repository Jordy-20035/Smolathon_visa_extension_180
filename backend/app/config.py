import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the root directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    PROJECT_NAME: str = "ЦОДД Смоленской области"
    VERSION: str = "1.0.0"
    
    # Database - now using environment variable
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        # Fallback for development
        DATABASE_URL = "postgresql://codd_user:1234@localhost:5432/codd_db"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-insecure-key-change-me")
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]  # React frontend
    
    # File upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
settings = Settings()