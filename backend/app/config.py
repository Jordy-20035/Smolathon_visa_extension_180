import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "ЦОДД Смоленской области"
    VERSION: str = "1.0.0"
    
    # Database - now using environment variable
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-insecure-key-change-me")
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]  # React frontend
    
    # File upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
settings = Settings()