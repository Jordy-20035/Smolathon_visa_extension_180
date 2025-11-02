from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, data, analytics, import_export, content, traffic_analysis
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.models import User, Location, Vehicle, Fine, Accident, TrafficLight, ContentPage, Detector, VehicleTrackReading, RoadNetworkEdge
import logging

logger = logging.getLogger(__name__)

# Create tables on startup
def create_tables():
    """Create database tables and indexes, handling existing objects gracefully"""
    from sqlalchemy.exc import ProgrammingError
    
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Database tables created/verified successfully")
    except ProgrammingError as e:
        # Handle PostgreSQL-specific errors (like duplicate table/index/relation)
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if any(keyword in error_str for keyword in ['already exists', 'DuplicateTable', 'DuplicateIndex', 'relation']):
            logger.info("Database objects already exist, skipping creation")
        else:
            logger.warning(f"Database initialization note: {e}")
    except Exception as e:
        # For other errors, log but don't fail startup
        logger.warning(f"Database initialization note: {e}")

create_tables()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API для ЦОДД Смоленской области - управление данными о дорожном движении",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for 404
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Include routers
app.include_router(auth.router)
app.include_router(data.router)
app.include_router(import_export.router)
app.include_router(analytics.router)
app.include_router(content.router)
app.include_router(traffic_analysis.router)

@app.get("/")
def read_root():
    return {"message": "Traffic Management API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
