from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, data, content, analytics, import_export

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(data.router)
app.include_router(content.router)
app.include_router(analytics.router)
app.include_router(import_export.router)

@app.get("/")
def root():
    return {"message": "ЦОДД Смоленской области API", "version": settings.VERSION}

@app.get("/health")
def health_check():
    return {"status": "healthy"}