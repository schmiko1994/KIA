"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, close_db
from app.utils.logger import app_logger

# Import API routers
from app.api import accounts, proxies, trends, content, video, toto, scheduler, upload, kpi, logs, settings as settings_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    app_logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    await init_db()
    app_logger.info("Application started successfully")
    
    # Optionally start background workers (commented out to avoid blocking)
    # import asyncio
    # from app.workers.upload_worker import start_upload_worker
    # from app.workers.metrics_worker import start_metrics_worker
    # asyncio.create_task(start_upload_worker())
    # asyncio.create_task(start_metrics_worker())
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down application")
    await close_db()
    app_logger.info("Application shut down successfully")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-Account TikTok Management System with automated content generation, video assembly, and upload scheduling",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware (optional, for production)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )

# Include API routers
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(proxies.router, prefix="/api/proxies", tags=["Proxies"])
app.include_router(trends.router, prefix="/api/trends", tags=["Trends"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(video.router, prefix="/api/video", tags=["Video"])
app.include_router(toto.router, prefix="/api/toto", tags=["ToTo/ComfyUI"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["Scheduler"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(kpi.router, prefix="/api/kpi", tags=["KPI"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
