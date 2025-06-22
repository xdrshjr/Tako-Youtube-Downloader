"""
Main FastAPI application for YouTube Downloader.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .routes import video_router, search_router, batch_router, config_router
from .models.responses import HealthResponse, ErrorResponse, StatusEnum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting YouTube Downloader API...")
    yield
    # Shutdown
    logger.info("Shutting down YouTube Downloader API...")


# Create FastAPI application
app = FastAPI(
    title="YouTube Downloader API",
    description="REST API for YouTube video downloading and search functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status=StatusEnum.ERROR,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            error_details={"detail": str(exc)}
        ).dict()
    )


# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic health check."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint."""
    try:
        # You could add more health checks here
        # e.g., database connectivity, external service checks, etc.
        
        return HealthResponse(
            status="healthy",
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )


# Include routers
app.include_router(video_router)
app.include_router(search_router)
app.include_router(batch_router)
app.include_router(config_router)


# Additional utility endpoints
@app.get("/api/v1/info")
async def get_api_info():
    """Get API information and capabilities."""
    return {
        "name": "YouTube Downloader API",
        "version": "1.0.0",
        "description": "REST API for YouTube video downloading and search functionality",
        "endpoints": {
            "video": {
                "info": "POST /api/v1/video/info - Get video information",
                "download": "POST /api/v1/video/download - Download single video",
                "cancel": "DELETE /api/v1/video/download/{task_id} - Cancel download",
                "active": "GET /api/v1/video/downloads/active - Get active downloads"
            },
            "search": {
                "videos": "POST /api/v1/search/videos - Search for videos",
                "trending": "GET /api/v1/search/trending - Get trending videos",
                "recent": "GET /api/v1/search/recent - Get recent videos",
                "suggestions": "GET /api/v1/search/suggestions - Get video suggestions"
            },
            "batch": {
                "download": "POST /api/v1/batch/download - Start batch download",
                "progress": "GET /api/v1/batch/progress/{task_id} - Get batch progress",
                "cancel": "DELETE /api/v1/batch/download/{task_id} - Cancel batch",
                "active": "GET /api/v1/batch/active - Get active batches"
            },
            "config": {
                "get": "GET /api/v1/config/ - Get configuration",
                "defaults": "GET /api/v1/config/defaults - Get default options"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.youtube_downloader.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 