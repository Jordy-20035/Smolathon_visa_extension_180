from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, data, analytics, import_export, content
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.models import User, Location, Vehicle, Fine, Accident, TrafficLight, ContentPage


# Create tables on startup
Base.metadata.create_all(bind=engine)


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

@app.get("/")
def read_root():
    return {"message": "Traffic Management API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
